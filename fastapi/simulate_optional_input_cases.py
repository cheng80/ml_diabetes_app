"""
현재 KNHANES 모델/데이터를 유지한 상태에서 입력 시나리오별 성능을 비교한다.

시나리오:
- glu_exact: 혈당 정밀 입력 (상세 화면 가정)
- glu_binned: 혈당 구간값(midpoint) 입력 (심플 화면 가정)
- no_glu: 혈당 미입력
- blend_exact: 운영 블렌드(혈당 정밀)
- blend_binned: 운영 블렌드(혈당 구간)

출력:
- fastapi/resources/simulation/simulation_summary.csv
- fastapi/resources/simulation/simulation_summary.md
- fastapi/resources/simulation/fig_simulation_metrics.png
- fastapi/resources/simulation/fig_simulation_errors.png
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from app.model_loader import KNHANES_GLU, KNHANES_NO_GLU

GLUCOSE_BLEND_WEIGHT = 0.55

BLOOD_GLUCOSE_RANGES: list[tuple[int, int]] = [
    (44, 98),
    (99, 116),
    (117, 139),
    (140, 199),
]

ROOT = Path(__file__).resolve().parent
SAV_PATH = ROOT / "resources" / "data" / "HN19_ALL.sav"
OUT_DIR = ROOT / "resources" / "simulation"


@dataclass
class EvalResult:
    scenario: str
    model_desc: str
    n_samples: int
    threshold: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    tn: int
    fp: int
    fn: int
    tp: int


def _midpoint_glucose(value: float) -> float:
    v = max(44.0, min(199.0, float(value)))
    for low, high in BLOOD_GLUCOSE_RANGES:
        if low <= v <= high:
            return (low + high) / 2.0
    return 169.5


def _prepare_common_test_df(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """모든 시나리오를 동일 표본에서 비교하기 위한 공통 테스트셋 생성."""
    cols = ["sex", "age", "HE_BMI", "HE_wc", "HE_glu", "HE_ht", "HE_DM_HbA1c"]
    d = df[cols].copy()
    d = d[d["age"] >= 19]
    d = d.dropna(subset=cols)
    d = d[(d["HE_glu"] >= 44) & (d["HE_glu"] <= 199)]
    d = d[d["HE_DM_HbA1c"].isin([1, 2, 3])]
    d["_target"] = (d["HE_DM_HbA1c"] == 3.0).astype(int)

    X = d.drop(columns=["_target", "HE_DM_HbA1c"])
    y = d["_target"]

    # 학습 파이프라인(train_knhanes.py)과 동일한 70/10/20 분할 재현
    X_train, X_rest, y_train, y_rest = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y,
    )
    _ = X_train, y_train
    X_val, X_test, y_val, y_test = train_test_split(
        X_rest,
        y_rest,
        test_size=2 / 3,
        random_state=42,
        stratify=y_rest,
    )
    _ = X_val, y_val
    return X_test.reset_index(drop=True), y_test.reset_index(drop=True)


def _predict_with_bundle(bundle: dict, df_raw: pd.DataFrame, glucose_mode: str) -> np.ndarray:
    features: list[str] = bundle["features"]
    imputer = bundle["imputer"]
    scaler = bundle["scaler"]
    poly = bundle.get("poly")
    poly_enabled = bundle.get("poly_enabled", False)
    model = bundle["model"]
    glucose_scale = bundle.get("glucose_scale", 1.0)

    rows = pd.DataFrame(
        {
            "sex": df_raw["sex"].astype(float),
            "age": df_raw["age"].astype(float),
            "HE_BMI": df_raw["HE_BMI"].astype(float),
            "HE_wc": df_raw["HE_wc"].astype(float),
        }
    )

    if "HE_glu" in features:
        if glucose_mode == "exact":
            glu = df_raw["HE_glu"].astype(float)
        elif glucose_mode == "binned":
            glu = df_raw["HE_glu"].astype(float).apply(_midpoint_glucose)
        else:
            raise ValueError(f"unsupported glucose_mode: {glucose_mode}")
        rows["HE_glu"] = glu * float(glucose_scale)

    if "HE_whr" in features:
        rows["HE_whr"] = rows["HE_wc"] / df_raw["HE_ht"].astype(float)
    if "HE_bmi_wc" in features:
        rows["HE_bmi_wc"] = rows["HE_BMI"] * (rows["HE_wc"] / 100.0)

    for col in features:
        if col not in rows.columns:
            rows[col] = 0.0
    rows = rows[features]

    x_imp = imputer.transform(rows)
    x_scaled = scaler.transform(x_imp)
    if poly_enabled and poly is not None:
        x_scaled = poly.transform(x_scaled)
    return model.predict_proba(x_scaled)[:, 1]


def _evaluate_probs(
    scenario: str,
    model_desc: str,
    y_true: np.ndarray,
    probs: np.ndarray,
    threshold: float,
) -> EvalResult:
    y_pred = (probs >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return EvalResult(
        scenario=scenario,
        model_desc=model_desc,
        n_samples=len(y_true),
        threshold=threshold,
        accuracy=float(accuracy_score(y_true, y_pred)),
        precision=float(precision_score(y_true, y_pred, zero_division=0)),
        recall=float(recall_score(y_true, y_pred, zero_division=0)),
        f1=float(f1_score(y_true, y_pred, zero_division=0)),
        roc_auc=float(roc_auc_score(y_true, probs)),
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
    )


def _build_charts(df: pd.DataFrame) -> None:
    metric_cols = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    x = np.arange(len(df["scenario"]))
    width = 0.16

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, m in enumerate(metric_cols):
        ax.bar(x + (i - 2) * width, df[m].values, width=width, label=m.upper())
    ax.set_ylim(0, 1)
    ax.set_xticks(x)
    ax.set_xticklabels(df["scenario"], rotation=15, ha="right")
    ax.set_ylabel("Score")
    ax.set_title("Simulation Metrics Comparison")
    ax.legend(loc="lower right", ncol=3, fontsize=9)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_simulation_metrics.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    width2 = 0.35
    ax.bar(x - width2 / 2, df["fp"].values, width=width2, label="FP")
    ax.bar(x + width2 / 2, df["fn"].values, width=width2, label="FN")
    ax.set_xticks(x)
    ax.set_xticklabels(df["scenario"], rotation=15, ha="right")
    ax.set_ylabel("Count")
    ax.set_title("Error Type Comparison (FP / FN)")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_simulation_errors.png", dpi=180)
    plt.close(fig)


def _to_markdown_table(df: pd.DataFrame) -> str:
    ordered = df[
        [
            "scenario",
            "model_desc",
            "n_samples",
            "threshold",
            "accuracy",
            "precision",
            "recall",
            "f1",
            "roc_auc",
            "tn",
            "fp",
            "fn",
            "tp",
        ]
    ].copy()
    for c in ["threshold", "accuracy", "precision", "recall", "f1", "roc_auc"]:
        ordered[c] = ordered[c].map(lambda v: f"{v:.4f}")
    return ordered.to_markdown(index=False)


def main() -> None:
    if KNHANES_GLU is None or KNHANES_NO_GLU is None:
        raise RuntimeError("KNHANES 모델 파일(model_knhanes_glu/no_glu.joblib)이 필요합니다.")
    if not SAV_PATH.exists():
        raise FileNotFoundError(f"데이터 파일 없음: {SAV_PATH}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df_raw, _meta = pyreadstat.read_sav(str(SAV_PATH))
    x_test, y_test = _prepare_common_test_df(df_raw)

    thr_glu = float(KNHANES_GLU.get("threshold", 0.5))
    thr_no = float(KNHANES_NO_GLU.get("threshold", 0.5))

    prob_glu_exact = _predict_with_bundle(KNHANES_GLU, x_test, glucose_mode="exact")
    prob_glu_binned = _predict_with_bundle(KNHANES_GLU, x_test, glucose_mode="binned")
    prob_no_glu = _predict_with_bundle(KNHANES_NO_GLU, x_test, glucose_mode="exact")

    prob_blend_exact = GLUCOSE_BLEND_WEIGHT * prob_no_glu + (1.0 - GLUCOSE_BLEND_WEIGHT) * prob_glu_exact
    prob_blend_binned = GLUCOSE_BLEND_WEIGHT * prob_no_glu + (1.0 - GLUCOSE_BLEND_WEIGHT) * prob_glu_binned

    results = [
        _evaluate_probs("glu_exact", "KNHANES glu model", y_test.values, prob_glu_exact, thr_glu),
        _evaluate_probs("glu_binned", "KNHANES glu model + bucket glucose", y_test.values, prob_glu_binned, thr_glu),
        _evaluate_probs("no_glu", "KNHANES no-glu model", y_test.values, prob_no_glu, thr_no),
        _evaluate_probs("blend_exact", "production blend (exact glucose)", y_test.values, prob_blend_exact, thr_glu),
        _evaluate_probs("blend_binned", "production blend (bucket glucose)", y_test.values, prob_blend_binned, thr_glu),
    ]

    out_df = pd.DataFrame([r.__dict__ for r in results])
    out_df.to_csv(OUT_DIR / "simulation_summary.csv", index=False, encoding="utf-8-sig")

    md = []
    md.append("# 선택형 입력 시뮬레이션 결과\n")
    md.append("- 모델/데이터: 기존 KNHANES 학습 결과 유지\n")
    md.append("- 테스트셋: KNHANES 성인 표본(동일 분할 재현, seed=42)\n")
    md.append(f"- 샘플 수: {len(y_test)}\n")
    md.append(f"- 블렌드 가중치: 위험인자 {GLUCOSE_BLEND_WEIGHT:.2f} / 혈당 {1-GLUCOSE_BLEND_WEIGHT:.2f}\n")
    md.append("\n## 성능 표\n")
    md.append(_to_markdown_table(out_df))
    md.append("\n\n## 생성 차트\n")
    md.append("- fig_simulation_metrics.png (정확도/정밀도/재현율/F1/AUC)\n")
    md.append("- fig_simulation_errors.png (FP/FN 비교)\n")

    (OUT_DIR / "simulation_summary.md").write_text("".join(md), encoding="utf-8")
    _build_charts(out_df)

    print(f"[완료] {OUT_DIR / 'simulation_summary.csv'}")
    print(f"[완료] {OUT_DIR / 'simulation_summary.md'}")
    print(f"[완료] {OUT_DIR / 'fig_simulation_metrics.png'}")
    print(f"[완료] {OUT_DIR / 'fig_simulation_errors.png'}")


if __name__ == "__main__":
    main()

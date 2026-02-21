"""
플랜 피처(F1~F4) 중 KNHANES에서 실사용 가능한 항목(F1~F3)을
포함/미포함 비교 시뮬레이션으로 평가한다.

F1: 가족력(당뇨)  -> HE_DMfh1/2/3 기반
F2: 고혈압/혈압약 -> DI1_dg, HE_HPdr, HE_HP 기반
F3: 운동량(주150분) -> BE3 활동 변수 기반
F4: 임신성 당뇨 이력 -> KNHANES 2019 직접 대응 컬럼 미확인(본 실험 제외)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat
from sklearn.impute import KNNImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

try:
    from imblearn.over_sampling import SMOTE

    HAS_IMBLEARN = True
except Exception:
    HAS_IMBLEARN = False


ROOT = Path(__file__).resolve().parent
SAV_PATH = ROOT / "resources" / "data" / "HN19_ALL.sav"
OUT_DIR = ROOT / "resources" / "simulation"


def _clean_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _unknown_to_nan(series: pd.Series, unknown_codes: tuple[float, ...]) -> pd.Series:
    s = _clean_num(series).copy()
    for c in unknown_codes:
        s = s.mask(s == c, np.nan)
    return s


def _midpoint_glucose(v: float) -> float:
    ranges = [(44, 98), (99, 116), (117, 139), (140, 199)]
    x = max(44.0, min(199.0, float(v)))
    for lo, hi in ranges:
        if lo <= x <= hi:
            return (lo + hi) / 2.0
    return 169.5


def _build_feature_frame(df: pd.DataFrame, glucose_mode: str, use_optional: bool) -> tuple[pd.DataFrame, pd.Series]:
    work = df.copy()
    work = work[work["age"] >= 19].copy()
    work = work[work["HE_DM_HbA1c"].isin([1, 2, 3])].copy()
    y = (work["HE_DM_HbA1c"] == 3.0).astype(int)

    x = pd.DataFrame(
        {
            "sex": _clean_num(work["sex"]),
            "age": _clean_num(work["age"]),
            "HE_BMI": _clean_num(work["HE_BMI"]),
            "HE_wc": _clean_num(work["HE_wc"]),
            "HE_ht": _clean_num(work["HE_ht"]),
            "HE_glu_raw": _clean_num(work["HE_glu"]),
        }
    )

    # 기본 품질 필터
    x = x[(x["HE_BMI"] > 0) & (x["HE_wc"] > 0) & (x["HE_ht"] > 0)]
    y = y.loc[x.index]

    # 혈당 처리
    if glucose_mode == "exact":
        x["HE_glu"] = x["HE_glu_raw"]
    elif glucose_mode == "binned":
        x["HE_glu"] = x["HE_glu_raw"].apply(lambda v: _midpoint_glucose(v) if pd.notna(v) else np.nan)
    elif glucose_mode == "none":
        pass
    else:
        raise ValueError(f"unsupported glucose_mode: {glucose_mode}")

    # 파생 피처(기존 유지)
    x["HE_whr"] = x["HE_wc"] / x["HE_ht"]
    x["HE_bmi_wc"] = x["HE_BMI"] * (x["HE_wc"] / 100.0)

    if use_optional:
        idx = x.index
        # F1 가족력(당뇨)
        f1 = pd.concat(
            [
                _unknown_to_nan(work["HE_DMfh1"], (8.0, 9.0)),
                _unknown_to_nan(work["HE_DMfh2"], (8.0, 9.0)),
                _unknown_to_nan(work["HE_DMfh3"], (8.0, 9.0)),
            ],
            axis=1,
        ).loc[idx]
        # 1: 있음 / 0: 없음 / NaN: 모름
        x["F1_family_dm"] = np.where((f1 == 1).any(axis=1), 1.0, np.where((f1 == 0).all(axis=1), 0.0, np.nan))

        # F2 고혈압/혈압약
        di1 = _unknown_to_nan(work["DI1_dg"], (8.0, 9.0)).loc[idx]
        hpdr = _unknown_to_nan(work["HE_HPdr"], (8.0, 9.0)).loc[idx]
        he_hp = _unknown_to_nan(work["HE_HP"], (8.0, 9.0)).loc[idx]
        f2_yes = (di1 == 1) | (hpdr == 1) | (he_hp == 1)
        f2_no = (di1 == 0) & (hpdr == 0) & (he_hp.isin([2, 3]))
        x["F2_htn_or_med"] = np.where(f2_yes, 1.0, np.where(f2_no, 0.0, np.nan))

        # F3 운동량(WHO 유사): 2*고강도 + 중강도 + 걷기 >= 150분/주
        vig_days = _unknown_to_nan(work["BE3_72"], (8.0, 9.0)).loc[idx]
        vig_h = _unknown_to_nan(work["BE3_73"], (88.0, 99.0)).loc[idx]
        vig_m = _unknown_to_nan(work["BE3_74"], (88.0, 99.0)).loc[idx]
        mod_days = _unknown_to_nan(work["BE3_82"], (8.0, 9.0)).loc[idx]
        mod_h = _unknown_to_nan(work["BE3_83"], (88.0, 99.0)).loc[idx]
        mod_m = _unknown_to_nan(work["BE3_84"], (88.0, 99.0)).loc[idx]
        walk_days = _unknown_to_nan(work["BE3_31"], (8.0, 9.0)).loc[idx]
        walk_h = _unknown_to_nan(work["BE3_32"], (88.0, 99.0)).loc[idx]
        walk_m = _unknown_to_nan(work["BE3_33"], (88.0, 99.0)).loc[idx]

        vig_week = vig_days * (vig_h * 60 + vig_m)
        mod_week = mod_days * (mod_h * 60 + mod_m)
        walk_week = walk_days * (walk_h * 60 + walk_m)
        mvpa_equiv = 2.0 * vig_week + mod_week + walk_week
        x["F3_exercise_150"] = np.where(mvpa_equiv >= 150, 1.0, np.where(mvpa_equiv < 150, 0.0, np.nan))

    base_cols = ["sex", "age", "HE_BMI", "HE_wc", "HE_whr", "HE_bmi_wc"]
    if glucose_mode != "none":
        base_cols.append("HE_glu")
    if use_optional:
        base_cols += ["F1_family_dm", "F2_htn_or_med", "F3_exercise_150"]

    out = x[base_cols].copy()
    # 최소 기본정보는 존재해야 함
    required = ["sex", "age", "HE_BMI", "HE_wc", "HE_whr", "HE_bmi_wc"]
    out = out.dropna(subset=required)
    y = y.loc[out.index]
    return out, y


def _fit_eval(x: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    x_train, x_rest, y_train, y_rest = train_test_split(
        x, y, test_size=0.3, random_state=42, stratify=y
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_rest, y_rest, test_size=2 / 3, random_state=42, stratify=y_rest
    )

    imputer = KNNImputer(n_neighbors=5)
    x_train_i = imputer.fit_transform(x_train)
    x_val_i = imputer.transform(x_val)
    x_test_i = imputer.transform(x_test)

    scaler = StandardScaler()
    x_train_s = scaler.fit_transform(x_train_i)
    x_val_s = scaler.transform(x_val_i)
    x_test_s = scaler.transform(x_test_i)

    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    x_train_p = poly.fit_transform(x_train_s)
    x_val_p = poly.transform(x_val_s)
    x_test_p = poly.transform(x_test_s)

    if HAS_IMBLEARN:
        smote = SMOTE(random_state=42, k_neighbors=3)
        x_train_p, y_train = smote.fit_resample(x_train_p, y_train)

    model = KNeighborsClassifier(n_neighbors=3, weights="distance", p=2)
    model.fit(x_train_p, y_train)

    # threshold tuning (balanced_recall = 0.6*BA + 0.4*Recall)
    p_val = model.predict_proba(x_val_p)[:, 1]
    best_t, best_s = 0.5, -1.0
    for t in np.arange(0.15, 0.85, 0.02):
        yv = (p_val >= t).astype(int)
        ba = balanced_accuracy_score(y_val, yv)
        rec = recall_score(y_val, yv, zero_division=0)
        sc = 0.6 * ba + 0.4 * rec
        if sc > best_s:
            best_s = sc
            best_t = float(t)

    p_test = model.predict_proba(x_test_p)[:, 1]
    yp = (p_test >= best_t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, yp, labels=[0, 1]).ravel()

    return {
        "n_samples": int(len(x)),
        "threshold": best_t,
        "accuracy": float(accuracy_score(y_test, yp)),
        "precision": float(precision_score(y_test, yp, zero_division=0)),
        "recall": float(recall_score(y_test, yp, zero_division=0)),
        "f1": float(f1_score(y_test, yp, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, p_test)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def _make_charts(df: pd.DataFrame, prefix: str) -> None:
    metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    x = np.arange(len(df))
    w = 0.16
    fig, ax = plt.subplots(figsize=(13, 5))
    for i, m in enumerate(metrics):
        ax.bar(x + (i - 2) * w, df[m].values, width=w, label=m.upper())
    ax.set_ylim(0, 1)
    ax.set_xticks(x)
    ax.set_xticklabels(df["scenario"], rotation=15, ha="right")
    ax.set_title("Feature Plan Simulation Metrics (F1~F3)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{prefix}_metrics.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5))
    w2 = 0.35
    ax.bar(x - w2 / 2, df["fp"].values, width=w2, label="FP")
    ax.bar(x + w2 / 2, df["fn"].values, width=w2, label="FN")
    ax.set_xticks(x)
    ax.set_xticklabels(df["scenario"], rotation=15, ha="right")
    ax.set_title("Feature Plan Simulation Errors (FP/FN)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{prefix}_errors.png", dpi=180)
    plt.close(fig)


def main() -> None:
    if not SAV_PATH.exists():
        raise FileNotFoundError(f"data not found: {SAV_PATH}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    usecols = [
        "sex",
        "age",
        "HE_BMI",
        "HE_wc",
        "HE_ht",
        "HE_glu",
        "HE_DM_HbA1c",
        "HE_DMfh1",
        "HE_DMfh2",
        "HE_DMfh3",
        "DI1_dg",
        "HE_HPdr",
        "HE_HP",
        "BE3_72",
        "BE3_73",
        "BE3_74",
        "BE3_82",
        "BE3_83",
        "BE3_84",
        "BE3_31",
        "BE3_32",
        "BE3_33",
    ]
    df, _meta = pyreadstat.read_sav(str(SAV_PATH), usecols=usecols)

    scenarios = [
        ("base_no_glu", "none", False),
        ("base_glu_binned", "binned", False),
        ("base_glu_exact", "exact", False),
        ("opt123_no_glu", "none", True),
        ("opt123_glu_binned", "binned", True),
        ("opt123_glu_exact", "exact", True),
    ]

    rows: list[dict[str, float | int | str]] = []
    for name, glu_mode, use_opt in scenarios:
        x, y = _build_feature_frame(df, glucose_mode=glu_mode, use_optional=use_opt)
        m = _fit_eval(x, y)
        row = {"scenario": name, "glucose_mode": glu_mode, "use_optional_f123": int(use_opt)}
        row.update(m)
        rows.append(row)
        print(f"[done] {name} n={m['n_samples']} acc={m['accuracy']:.4f} recall={m['recall']:.4f}")

    out = pd.DataFrame(rows)
    out_path_csv = OUT_DIR / "feature_plan_simulation_summary.csv"
    out_path_md = OUT_DIR / "feature_plan_simulation_summary.md"
    out.to_csv(out_path_csv, index=False, encoding="utf-8-sig")

    md = []
    md.append("# 플랜 피처(F1~F4) 사전 시뮬레이션 결과\n")
    md.append("- 데이터: KNHANES 2019 (기존)\n")
    md.append("- 모델: KNN(n=3, distance, p=2) + KNNImputer + StandardScaler + PolynomialFeatures + (가능 시)SMOTE\n")
    md.append("- 분할: train/val/test = 70/10/20, seed=42\n")
    md.append("- F4(임신성 당뇨 이력): 데이터셋 직접 대응 컬럼 미확인으로 이번 실험 제외\n")
    md.append(f"- SMOTE 사용: {'yes' if HAS_IMBLEARN else 'no'}\n\n")
    show = out.copy()
    for c in ["threshold", "accuracy", "precision", "recall", "f1", "roc_auc"]:
        show[c] = show[c].map(lambda v: f"{v:.4f}")
    md.append("## 결과 표\n")
    md.append(show.to_markdown(index=False))
    md.append("\n\n## 생성 차트\n")
    md.append("- feature_plan_sim_metrics.png\n")
    md.append("- feature_plan_sim_errors.png\n")
    out_path_md.write_text("".join(md), encoding="utf-8")

    _make_charts(out, "feature_plan_sim")
    print(f"[saved] {out_path_csv}")
    print(f"[saved] {out_path_md}")
    print(f"[saved] {OUT_DIR / 'feature_plan_sim_metrics.png'}")
    print(f"[saved] {OUT_DIR / 'feature_plan_sim_errors.png'}")


if __name__ == "__main__":
    main()

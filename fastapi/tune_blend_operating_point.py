#!/usr/bin/env python3
"""Tune blend operating point (weight, threshold) without retraining.

Searches (GLUCOSE_BLEND_WEIGHT, threshold) pairs on fixed KNHANES test split
and recommends an FP-reducing operating point under FN-increase constraints.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from app.model_loader import KNHANES_GLU, KNHANES_NO_GLU


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
class Metrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    tn: int
    fp: int
    fn: int
    tp: int


def midpoint_glucose(value: float) -> float:
    v = max(44.0, min(199.0, float(value)))
    for low, high in BLOOD_GLUCOSE_RANGES:
        if low <= v <= high:
            return (low + high) / 2.0
    return 169.5


def prepare_common_test_df(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    cols = ["sex", "age", "HE_BMI", "HE_wc", "HE_glu", "HE_ht", "HE_DM_HbA1c"]
    d = df[cols].copy()
    d = d[d["age"] >= 19]
    d = d.dropna(subset=cols)
    d = d[(d["HE_glu"] >= 44) & (d["HE_glu"] <= 199)]
    d = d[d["HE_DM_HbA1c"].isin([1, 2, 3])]
    d["_target"] = (d["HE_DM_HbA1c"] == 3.0).astype(int)

    x = d.drop(columns=["_target", "HE_DM_HbA1c"])
    y = d["_target"]

    x_train, x_rest, y_train, y_rest = train_test_split(
        x,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y,
    )
    _ = x_train, y_train
    x_val, x_test, y_val, y_test = train_test_split(
        x_rest,
        y_rest,
        test_size=2 / 3,
        random_state=42,
        stratify=y_rest,
    )
    _ = x_val, y_val
    return x_test.reset_index(drop=True), y_test.reset_index(drop=True)


def predict_with_bundle(bundle: dict, df_raw: pd.DataFrame, glucose_mode: str) -> np.ndarray:
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
            glu = df_raw["HE_glu"].astype(float).apply(midpoint_glucose)
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


def eval_probs(y_true: np.ndarray, probs: np.ndarray, threshold: float) -> Metrics:
    y_pred = (probs >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return Metrics(
        accuracy=float(accuracy_score(y_true, y_pred)),
        precision=float(precision_score(y_true, y_pred, zero_division=0)),
        recall=float(recall_score(y_true, y_pred, zero_division=0)),
        f1=float(f1_score(y_true, y_pred, zero_division=0)),
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
    )


def frange(start: float, stop: float, step: float) -> list[float]:
    n = int(round((stop - start) / step))
    return [round(start + i * step, 10) for i in range(n + 1)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Tune blend weight and threshold.")
    parser.add_argument("--w-start", type=float, default=0.45)
    parser.add_argument("--w-stop", type=float, default=0.75)
    parser.add_argument("--w-step", type=float, default=0.01)
    parser.add_argument("--t-start", type=float, default=0.50)
    parser.add_argument("--t-stop", type=float, default=0.75)
    parser.add_argument("--t-step", type=float, default=0.01)
    parser.add_argument(
        "--max-fn-increase",
        type=int,
        default=5,
        help="Allowed FN increase per mode (exact, binned) over baseline.",
    )
    args = parser.parse_args()

    if KNHANES_GLU is None or KNHANES_NO_GLU is None:
        raise RuntimeError("KNHANES 모델 파일(model_knhanes_glu/no_glu.joblib)이 필요합니다.")
    if not SAV_PATH.exists():
        raise FileNotFoundError(f"데이터 파일 없음: {SAV_PATH}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df_raw, _meta = pyreadstat.read_sav(str(SAV_PATH))
    x_test, y_test = prepare_common_test_df(df_raw)

    prob_glu_exact = predict_with_bundle(KNHANES_GLU, x_test, glucose_mode="exact")
    prob_glu_binned = predict_with_bundle(KNHANES_GLU, x_test, glucose_mode="binned")
    prob_no_glu = predict_with_bundle(KNHANES_NO_GLU, x_test, glucose_mode="exact")

    baseline_w = 0.55
    baseline_t = float(KNHANES_GLU.get("threshold", 0.5))
    base_blend_exact = baseline_w * prob_no_glu + (1.0 - baseline_w) * prob_glu_exact
    base_blend_binned = baseline_w * prob_no_glu + (1.0 - baseline_w) * prob_glu_binned
    base_exact_m = eval_probs(y_test.values, base_blend_exact, baseline_t)
    base_binned_m = eval_probs(y_test.values, base_blend_binned, baseline_t)

    rows: list[dict] = []
    for w in frange(args.w_start, args.w_stop, args.w_step):
        blend_exact = w * prob_no_glu + (1.0 - w) * prob_glu_exact
        blend_binned = w * prob_no_glu + (1.0 - w) * prob_glu_binned
        for t in frange(args.t_start, args.t_stop, args.t_step):
            m_exact = eval_probs(y_test.values, blend_exact, t)
            m_binned = eval_probs(y_test.values, blend_binned, t)

            rows.append(
                {
                    "weight": w,
                    "threshold": t,
                    "fp_exact": m_exact.fp,
                    "fn_exact": m_exact.fn,
                    "recall_exact": m_exact.recall,
                    "acc_exact": m_exact.accuracy,
                    "fp_binned": m_binned.fp,
                    "fn_binned": m_binned.fn,
                    "recall_binned": m_binned.recall,
                    "acc_binned": m_binned.accuracy,
                    "fp_total": m_exact.fp + m_binned.fp,
                    "fn_total": m_exact.fn + m_binned.fn,
                    "eligible": (
                        m_exact.fn <= base_exact_m.fn + args.max_fn_increase
                        and m_binned.fn <= base_binned_m.fn + args.max_fn_increase
                    ),
                }
            )

    sweep_df = pd.DataFrame(rows)
    out_csv = OUT_DIR / "blend_threshold_sweep.csv"
    sweep_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    eligible_df = sweep_df[sweep_df["eligible"] == True].copy()
    if eligible_df.empty:
        print("[WARN] 제약을 만족하는 후보가 없습니다. 제약 완화가 필요합니다.")
        print(f"[완료] {out_csv}")
        return

    eligible_df = eligible_df.sort_values(
        by=["fp_total", "fn_total", "acc_exact", "acc_binned"],
        ascending=[True, True, False, False],
    )
    best = eligible_df.iloc[0]

    summary_md = OUT_DIR / "blend_threshold_tuning.md"
    lines = []
    lines.append("# Blend 운영점 튜닝 결과\n\n")
    lines.append("## 기준(Baseline)\n\n")
    lines.append(f"- weight: `{baseline_w:.2f}`\n")
    lines.append(f"- threshold: `{baseline_t:.2f}`\n")
    lines.append(f"- baseline exact: FP `{base_exact_m.fp}`, FN `{base_exact_m.fn}`, Recall `{base_exact_m.recall:.4f}`\n")
    lines.append(f"- baseline binned: FP `{base_binned_m.fp}`, FN `{base_binned_m.fn}`, Recall `{base_binned_m.recall:.4f}`\n\n")
    lines.append("## 탐색 조건\n\n")
    lines.append(f"- weight: `{args.w_start}` ~ `{args.w_stop}` (step `{args.w_step}`)\n")
    lines.append(f"- threshold: `{args.t_start}` ~ `{args.t_stop}` (step `{args.t_step}`)\n")
    lines.append(f"- FN 제약: 각 모드에서 baseline 대비 `+{args.max_fn_increase}` 이하\n\n")
    lines.append("## 추천 운영값\n\n")
    lines.append(f"- weight: `{best['weight']:.2f}`\n")
    lines.append(f"- threshold: `{best['threshold']:.2f}`\n")
    lines.append(f"- exact: FP `{int(best['fp_exact'])}`, FN `{int(best['fn_exact'])}`, Recall `{best['recall_exact']:.4f}`, Accuracy `{best['acc_exact']:.4f}`\n")
    lines.append(f"- binned: FP `{int(best['fp_binned'])}`, FN `{int(best['fn_binned'])}`, Recall `{best['recall_binned']:.4f}`, Accuracy `{best['acc_binned']:.4f}`\n")
    lines.append(f"- FP total: `{int(best['fp_total'])}` / FN total: `{int(best['fn_total'])}`\n")
    lines.append("\n## 파일\n\n")
    lines.append(f"- 전체 탐색 결과: `{out_csv}`\n")
    lines.append(f"- 요약: `{summary_md}`\n")
    summary_md.write_text("".join(lines), encoding="utf-8")

    print(f"[완료] {out_csv}")
    print(f"[완료] {summary_md}")
    print(
        "[추천] "
        f"weight={best['weight']:.2f}, threshold={best['threshold']:.2f}, "
        f"exact(FP={int(best['fp_exact'])},FN={int(best['fn_exact'])}), "
        f"binned(FP={int(best['fp_binned'])},FN={int(best['fn_binned'])})"
    )


if __name__ == "__main__":
    main()

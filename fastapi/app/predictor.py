# 혈당/허리둘레 유무에 따라 모델 분기 (Pima vs KNHANES)
from __future__ import annotations

import base64
import io
import os
from pathlib import Path

import matplotlib
from matplotlib import font_manager as fm

# 혈당 의존도 조절: 0.5=동등, 0.6=혈당미포함 60%+혈당포함 40% (혈당 영향 감소)
GLUCOSE_BLEND_WEIGHT = float(os.environ.get("GLUCOSE_BLEND_WEIGHT", "0.55"))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastapi import HTTPException

from app.model_loader import (
    FEATURE_LABELS,
    FEATURE_RANGES,
    FEATURES_NO_SUGAR,
    FEATURES_SUGAR,
    KNHANES_GLU,
    KNHANES_NO_GLU,
    MODEL_NO_SUGAR,
    MODEL_SUGAR,
    standardize,
)


def _build_chart_input(feature_names: list[str], user: dict[str, float]) -> dict[str, float]:
    """KNHANES/Pima 피처명을 user_provided 키에 맞춰 차트용 입력값 생성"""
    height_cm = user.get("height_cm", 170.0) or 170.0
    chart_input: dict[str, float] = {}
    for f in feature_names:
        if f == "sex":
            chart_input[f] = user.get("sex", 1.0)
        elif f == "age":
            chart_input[f] = user.get("age", 30.0)
        elif f == "HE_BMI":
            chart_input[f] = user.get("bmi", 25.0)
        elif f == "HE_wc":
            chart_input[f] = user.get("waist_cm", 85.0)
        elif f == "HE_glu":
            chart_input[f] = user.get("glucose", 100.0)
        elif f == "HE_whr":
            wc = user.get("waist_cm", 85.0)
            chart_input[f] = wc / height_cm if height_cm > 0 else 0.0
        elif f == "HE_bmi_wc":
            bmi = user.get("bmi", 25.0)
            wc = user.get("waist_cm", 85.0)
            chart_input[f] = bmi * (wc / 100)
        else:
            chart_input[f] = user.get(f, 0.0)
    return chart_input
from app.schemas import PredictRequest, PredictResponse

matplotlib.use("Agg")
plt.rcParams["axes.unicode_minus"] = False


def _configure_chart_font() -> bool:
    """
    차트 한글 폰트 설정.
    - 서버에 한글 폰트가 있으면 한글 라벨 유지
    - 없으면 영문 라벨로 폴백 (글자 깨짐 방지)
    """
    # 1) 폰트 파일 경로 직접 로드 (NAS/서버 폰트 미설치 환경 대응)
    app_dir = Path(__file__).resolve().parent
    font_path_candidates = [
        os.environ.get("CHART_FONT_PATH"),
        str(app_dir.parent / "resources" / "fonts" / "NotoSansKR-Regular.otf"),
        str(app_dir.parent / "resources" / "fonts" / "NotoSansKR-Regular.ttf"),
    ]
    for fp in font_path_candidates:
        if not fp:
            continue
        p = Path(fp)
        if p.exists():
            try:
                fm.fontManager.addfont(str(p))
                font_name = fm.FontProperties(fname=str(p)).get_name()
                plt.rcParams["font.family"] = font_name
                return True
            except Exception:
                pass

    # 2) 설치된 시스템 폰트 이름으로 탐색
    preferred = os.environ.get("CHART_FONT_FAMILY")
    candidates = [preferred] if preferred else []
    candidates += [
        "AppleGothic",
        "NanumGothic",
        "Noto Sans CJK KR",
        "Noto Sans KR",
        "Malgun Gothic",
    ]
    installed = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name and name in installed:
            plt.rcParams["font.family"] = name
            return True

    plt.rcParams["font.family"] = "DejaVu Sans"
    return False


USE_KOREAN_CHART_TEXT = _configure_chart_font()


def _txt(ko: str, en: str) -> str:
    return ko if USE_KOREAN_CHART_TEXT else en


# 정상 범위 기준 (당뇨 위험 관련)
REF_BMI_NORMAL = 25
REF_BMI_OBESE = 30
REF_WAIST_M = 90  # 남성 허리둘레 기준 (cm)
REF_WAIST_F = 80  # 여성 허리둘레 기준 (cm)
REF_GLU_NORMAL = 100
REF_GLU_DIABETES = 126


def _input_vs_reference_chart(ax, input_values: dict[str, float]) -> None:
    """입력값 vs 정상 범위 막대 차트. BMI·허리둘레·혈당에 기준 구간 표시"""
    metrics: list[tuple[str, str, float, float, tuple[float, float] | None]] = []

    bmi = input_values.get("HE_BMI") or input_values.get("bmi")
    if bmi is not None and bmi > 0:
        metrics.append(("BMI", f"{bmi:.1f}", bmi, 45, (REF_BMI_NORMAL, REF_BMI_OBESE)))

    wc = input_values.get("HE_wc") or input_values.get("waist_cm")
    if wc is not None and wc > 0:
        sex = input_values.get("sex", 1)
        ref_w = REF_WAIST_M if sex == 1 else REF_WAIST_F
        metrics.append((_txt("허리둘레 (cm)", "Waist (cm)"), f"{wc:.0f}", wc, 130, (ref_w, None)))

    glu = input_values.get("HE_glu") or input_values.get("glucose")
    if glu is not None and glu > 0:
        metrics.append((_txt("공복 혈당 (mg/dL)", "Fasting glucose (mg/dL)"), f"{glu:.0f}", glu, 200, (REF_GLU_NORMAL, REF_GLU_DIABETES)))

    age = input_values.get("age")
    if age is not None and age > 0:
        metrics.append((_txt("나이", "Age"), f"{age:.0f}" + (_txt("세", "y")), age, 100, None))

    if not metrics:
        ax.text(0.5, 0.5, _txt("입력값 없음", "No input"), ha="center", va="center", transform=ax.transAxes)
        return

    labels = [m[0] for m in metrics]
    vals = [m[2] for m in metrics]
    xmax_list = [m[3] for m in metrics]
    refs = [m[4] for m in metrics]

    y_pos = np.arange(len(labels))
    bar_height = 0.5
    x_axis_max = max(xmax_list)
    for i, (xm, ref) in enumerate(zip(xmax_list, refs)):
        if ref:
            r1, r2 = ref
            x1 = r1 / x_axis_max
            x2 = (r2 if r2 else xm) / x_axis_max
            ax.axhspan(i - bar_height / 2, i + bar_height / 2, xmin=0, xmax=x1, facecolor="#C8E6C9", alpha=0.5)
            ax.axhspan(i - bar_height / 2, i + bar_height / 2, xmin=x1, xmax=min(1.0, x2), facecolor="#FFF9C4", alpha=0.5)
            if r2:
                ax.axhspan(i - bar_height / 2, i + bar_height / 2, xmin=x2, xmax=1, facecolor="#FFCDD2", alpha=0.5)

    colors = []
    for val, xm, ref in zip(vals, xmax_list, refs):
        if ref:
            r1, r2 = ref
            if val < r1:
                colors.append("#4CAF50")
            elif r2 and val < r2:
                colors.append("#FF9800")
            else:
                colors.append("#E53935")
        else:
            colors.append("#1976D2")

    bars = ax.barh(y_pos, vals, height=bar_height, color=colors, edgecolor="black", linewidth=1, zorder=2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlim(0, x_axis_max * 1.05)
    ax.set_xlabel(_txt("값", "Value"))
    ax.set_title(_txt("내 수치 vs 정상 범위 (녹색=정상, 노랑=주의, 빨강=위험)", "My values vs reference ranges"))
    ax.grid(True, axis="x", alpha=0.3)

    for bar, m in zip(bars, metrics):
        _, label_txt, val = m[0], m[1], m[2]
        ax.text(val + x_axis_max * 0.01, bar.get_y() + bar.get_height() / 2, label_txt, va="center", fontsize=9, fontweight="bold")


def create_chart_base64(
    probability: float,
    input_values: dict[str, float],
    model,
    feature_names: list[str],
) -> str:
    """당뇨/정상 확률 + 입력값 vs 정상 범위 차트"""
    fig, axes = plt.subplots(2, 1, figsize=(6, 7))

    # 상단: 당뇨/정상 확률 바 차트
    ax1 = axes[0]
    diabetes_prob = max(0.0, min(1.0, probability))
    normal_prob = 1.0 - diabetes_prob
    labels = [_txt("정상 가능성", "Normal"), _txt("당뇨 가능성", "Diabetes risk")]
    values = [normal_prob, diabetes_prob]
    colors = ["#4CAF50", "#E53935"]

    bars = ax1.bar(labels, values, color=colors)
    ax1.set_ylim(0, 1)
    ax1.set_ylabel(_txt("확률", "Probability"))
    ax1.set_title(_txt("당뇨 예측 결과 (ML 모델)", "Diabetes prediction result"))

    for bar, value in zip(bars, values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.02,
            f"{value * 100:.1f}%",
            ha="center",
            va="bottom",
            fontsize=11,
        )

    # 하단: 입력값 vs 정상 범위
    _input_vs_reference_chart(axes[1], input_values)

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _predict_knhanes(bundle: dict, user: dict[str, float]) -> tuple[float, int, str]:
    """KNHANES 모델로 예측. user: sex, age, bmi, waist_cm, glucose(선택), height_cm"""
    model = bundle["model"]
    imputer = bundle["imputer"]
    scaler = bundle["scaler"]
    poly = bundle.get("poly")
    poly_enabled = bundle.get("poly_enabled", False)
    features = bundle["features"]
    threshold = bundle.get("threshold", 0.5)

    height_cm = user.get("height_cm", 170.0)
    if height_cm <= 0:
        height_cm = 170.0

    glucose_scale = bundle.get("glucose_scale", 1.0)
    row = {
        "sex": user.get("sex", 1),
        "age": user.get("age", 30),
        "HE_BMI": user.get("bmi", 25),
        "HE_wc": user.get("waist_cm", 85),
    }
    if "HE_glu" in features:
        row["HE_glu"] = user.get("glucose", 100) * glucose_scale
    if "HE_whr" in features:
        row["HE_whr"] = row["HE_wc"] / height_cm
    if "HE_bmi_wc" in features:
        row["HE_bmi_wc"] = row["HE_BMI"] * (row["HE_wc"] / 100)

    X_df = pd.DataFrame([row])
    X_df = X_df[[f for f in features if f in X_df.columns]]
    for f in features:
        if f not in X_df.columns:
            X_df[f] = 0
    X_df = X_df[features]
    X_imp = imputer.transform(X_df)
    X_scaled = scaler.transform(X_imp)
    if poly_enabled and poly is not None:
        X_scaled = poly.transform(X_scaled)

    proba = model.predict_proba(X_scaled)[0]
    probability = float(proba[1])
    prediction = int(probability >= threshold)
    return probability, prediction, model.__class__.__name__


def predict_with_model(payload: PredictRequest) -> PredictResponse:
    """허리둘레 유무에 따라 KNHANES/Pima 분기"""

    raw_input: dict[str, float | None] = {
        "pregnancies": payload.pregnancies,
        "glucose": payload.glucose,
        "bmi": payload.bmi,
        "age": payload.age,
        "waist_cm": payload.waist_cm,
        "sex": float(payload.sex) if payload.sex is not None else None,
        "height_cm": payload.height_cm,
    }

    user_provided = {k: float(v) for k, v in raw_input.items() if v is not None}

    if not user_provided:
        raise HTTPException(status_code=400, detail="최소 1개 이상의 입력 항목이 필요합니다.")

    for key, value in user_provided.items():
        if key in FEATURE_RANGES:
            min_v, max_v = FEATURE_RANGES[key]
            if value < min_v or value > max_v:
                lbl = FEATURE_LABELS.get(key, key)
                raise HTTPException(
                    status_code=400,
                    detail=f"{lbl}({key}) 값은 {min_v} ~ {max_v} 범위여야 합니다.",
                )

    use_knhanes = user_provided.get("waist_cm") is not None and (
        (KNHANES_NO_GLU and "glucose" not in user_provided)
        or (KNHANES_GLU and "glucose" in user_provided)
    )

    bundle = None
    if use_knhanes:
        has_glu = "glucose" in user_provided
        bundle = KNHANES_GLU if has_glu else KNHANES_NO_GLU
        if bundle is None:
            use_knhanes = False
        else:
            if user_provided.get("sex") is None:
                user_provided["sex"] = 1.0
            if user_provided.get("height_cm") is None:
                user_provided["height_cm"] = 170.0
            probability, prediction, model_name = _predict_knhanes(bundle, user_provided)

            # 혈당 포함 시 블렌딩: 혈당 의존도 감소 (BMI·허리둘레 등 다른 위험인자 반영)
            if has_glu and KNHANES_NO_GLU is not None:
                prob_no_glu, _, _ = _predict_knhanes(KNHANES_NO_GLU, user_provided)
                probability = (
                    GLUCOSE_BLEND_WEIGHT * prob_no_glu
                    + (1.0 - GLUCOSE_BLEND_WEIGHT) * probability
                )
                prediction = int(probability >= bundle.get("threshold", 0.5))
                used_model_name = (
                    f"KNHANES 블렌드 (위험인자 {GLUCOSE_BLEND_WEIGHT:.0%} + 혈당 {1-GLUCOSE_BLEND_WEIGHT:.0%})"
                )
            else:
                used_model_name = f"KNHANES ({model_name})" + (
                    " 혈당 포함" if has_glu else " 혈당 미포함"
                )
            feature_names = bundle["features"]
            model = bundle["model"]
    else:
        has_glucose = "glucose" in user_provided
        model = MODEL_SUGAR if has_glucose else MODEL_NO_SUGAR
        feature_names = FEATURES_SUGAR if has_glucose else FEATURES_NO_SUGAR
        if model is None:
            raise HTTPException(
                status_code=503,
                detail="Pima 모델을 찾을 수 없습니다. 허리둘레를 입력하면 KNHANES 모델을 사용합니다.",
            )
        active_count = sum(1 for k in feature_names if k in user_provided)
        if active_count == 0:
            raise HTTPException(
                status_code=400,
                detail=f"필요 항목: {', '.join(feature_names)}. 또는 허리둘레를 입력하면 KNHANES 모델을 사용합니다.",
            )
        x_values = [standardize(f, user_provided.get(f, 0.0)) for f in feature_names]
        X = np.array([x_values])
        proba = model.predict_proba(X)[0]
        probability = float(proba[1])
        prediction = int(probability >= 0.5)
        used_model_name = "AdaBoost (혈당 포함)" if has_glucose else "RandomForest (혈당 미포함)"

    label = "당뇨 위험" if prediction == 1 else "정상 범위"

    chart_image_base64: str | None = None
    try:
        chart_input = _build_chart_input(feature_names, user_provided)
        chart_image_base64 = create_chart_base64(
            probability, chart_input, model, feature_names,
        )
    except Exception:
        chart_image_base64 = None

    return PredictResponse(
        prediction=prediction,
        probability=round(probability, 4),
        label=label,
        input=user_provided,
        used_model=used_model_name,
        chart_image_base64=chart_image_base64,
    )

from __future__ import annotations

from pathlib import Path

import joblib

APP_DIR = Path(__file__).resolve().parent

MODEL_SUGAR_PATH = APP_DIR / "model_sugar.joblib"
MODEL_NO_SUGAR_PATH = APP_DIR / "model_no_sugar.joblib"
MODEL_KNHANES_GLU_PATH = APP_DIR / "model_knhanes_glu.joblib"
MODEL_KNHANES_NO_GLU_PATH = APP_DIR / "model_knhanes_no_glu.joblib"

if not MODEL_SUGAR_PATH.exists():
    raise FileNotFoundError(f"혈당 포함 모델 파일을 찾을 수 없습니다: {MODEL_SUGAR_PATH}")
if not MODEL_NO_SUGAR_PATH.exists():
    raise FileNotFoundError(f"혈당 미포함 모델 파일을 찾을 수 없습니다: {MODEL_NO_SUGAR_PATH}")

MODEL_SUGAR = joblib.load(MODEL_SUGAR_PATH)
MODEL_NO_SUGAR = joblib.load(MODEL_NO_SUGAR_PATH)

KNHANES_GLU: dict | None = None
KNHANES_NO_GLU: dict | None = None
if MODEL_KNHANES_GLU_PATH.exists():
    KNHANES_GLU = joblib.load(MODEL_KNHANES_GLU_PATH)
if MODEL_KNHANES_NO_GLU_PATH.exists():
    KNHANES_NO_GLU = joblib.load(MODEL_KNHANES_NO_GLU_PATH)

FEATURES_SUGAR = ["glucose", "bmi", "age", "pregnancies"]
FEATURES_NO_SUGAR = ["bmi", "age", "pregnancies"]

ALIAS_TO_ENG = {
    "혈당": "glucose",
    "BMI": "bmi",
    "나이": "age",
    "임신횟수": "pregnancies",
    "허리둘레": "waist_cm",
    "성별": "sex",
    "키": "height_cm",
}

FEATURE_LABELS = {
    "glucose": "혈당",
    "bmi": "BMI",
    "age": "나이",
    "pregnancies": "임신횟수",
    "waist_cm": "허리둘레",
    "sex": "성별",
    "HE_BMI": "BMI",
    "HE_wc": "허리둘레",
    "HE_glu": "혈당",
    "HE_whr": "허리/신장비",
    "HE_bmi_wc": "BMI×허리",
}


FEATURE_RANGES = {
    "glucose": (44.0, 199.0),
    "bmi": (0.0, 67.1),
    "age": (19.0, 100.0),  # KNHANES 만19세 이상
    "pregnancies": (0.0, 17.0),
    "waist_cm": (50.0, 150.0),
    "height_cm": (80.0, 220.0),
}

# ---------------------------------------------------------------------------
# Pima 전처리: 원본 수치 -> StandardScaler 표준화 (z-score)
# ---------------------------------------------------------------------------
SCALER_STATS: dict[str, tuple[float, float]] = {
    "pregnancies": (3.837240, 3.341979),
    "glucose": (121.686763, 30.515624),
    "bmi": (32.394716, 6.711356),
    "age": (33.199870, 11.620831),
}


def standardize(feature: str, raw_value: float) -> float:
    """원본 수치를 z-score 표준화 (Pima용)"""
    mean, scale = SCALER_STATS[feature]
    return (raw_value - mean) / scale


def _log(msg: str) -> None:
    print(f"[모델 로드] {msg}")


_log(f"Pima 혈당 포함: {type(MODEL_SUGAR).__name__ if MODEL_SUGAR else 'None'}, "
     f"혈당 미포함: {type(MODEL_NO_SUGAR).__name__ if MODEL_NO_SUGAR else 'None'}")
if KNHANES_GLU:
    _log("KNHANES 혈당 포함 로드됨")
if KNHANES_NO_GLU:
    _log("KNHANES 혈당 미포함 로드됨")

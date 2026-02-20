"""
당뇨 예측 모델 학습 및 테스트 스크립트

- 기존 app/predictor.py에서 사용하는 모델을 학습/교체하기 위한 독립 실행 파일
- Pima Indians Diabetes Dataset (당뇨.csv) 기반
- 혈당 포함/미포함 두 시나리오로 모델 학습
- 학습 완료 후 model_sugar.joblib, model_no_sugar.joblib 저장
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.impute import KNNImputer
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = APP_DIR / "당뇨.csv"
OUTPUT_DIR = APP_DIR / "app"

FEATURES_SUGAR = ["glucose", "bmi", "age", "pregnancies"]
FEATURES_NO_SUGAR = ["bmi", "age", "pregnancies"]
TARGET_COL = "outcome"

# Pima 데이터셋 컬럼 매핑 (한글/영문)
COLUMN_MAP = {
    "Pregnancies": "pregnancies",
    "Glucose": "glucose",
    "BloodPressure": "blood_pressure",
    "SkinThickness": "skin_thickness",
    "Insulin": "insulin",
    "BMI": "bmi",
    "DiabetesPedigreeFunction": "dpf",
    "Age": "age",
    "Outcome": "outcome",
}


def load_data(csv_path: Path) -> pd.DataFrame:
    """CSV 로드 및 컬럼 정규화"""
    df = pd.read_csv(csv_path)
    df.columns = [COLUMN_MAP.get(c, c) for c in df.columns]
    return df


def preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, dict]:
    """
    전처리: 0→NaN, IQR 클리핑, KNN 임퓨트, StandardScaler 표준화

    Returns:
        X_scaled: 표준화된 피처
        y: 타겟
        scaler_stats: model_loader.py용 (mean, std) 딕셔너리
    """
    # 사용할 피처만 추출
    feature_cols = ["pregnancies", "glucose", "bmi", "age"]
    X = df[feature_cols].copy()
    y = df[TARGET_COL]

    # 0을 결측으로 처리 (당뇨 데이터셋 관례)
    X = X.replace(0, np.nan)

    # IQR 기반 이상치 클리핑
    for col in X.columns:
        q1 = X[col].quantile(0.25)
        q3 = X[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        X[col] = X[col].clip(lower=lower, upper=upper)

    # KNN 임퓨트로 결측 보간
    imputer = KNNImputer(n_neighbors=5)
    X_imputed = imputer.fit_transform(X)
    X_imputed = pd.DataFrame(X_imputed, columns=feature_cols)

    # StandardScaler 표준화
    scaler = StandardScaler()
    X_scaled_arr = scaler.fit_transform(X_imputed)
    X_scaled = pd.DataFrame(X_scaled_arr, columns=feature_cols)

    # model_loader.py용 통계값 (mean, std)
    scaler_stats = {
        col: (float(scaler.mean_[i]), float(np.sqrt(scaler.var_[i])))
        for i, col in enumerate(feature_cols)
    }

    return X_scaled, y, scaler_stats


def train_and_evaluate(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    features: list[str],
    model_name: str,
    model,
) -> None:
    """모델 학습 및 평가"""
    X_tr = X_train[features]
    X_te = X_test[features]

    model.fit(X_tr, y_train)
    y_pred = model.predict(X_te)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\n[{model_name}]")
    print(f"  Accuracy: {acc:.4f}")
    print(f"  F1 Score: {f1:.4f}")
    print(classification_report(y_test, y_pred, target_names=["정상", "당뇨"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="당뇨 예측 모델 학습")
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help=f"데이터 CSV 경로 (기본: {DEFAULT_CSV_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"모델 저장 경로 (기본: {OUTPUT_DIR})",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="테스트 세트 비율 (기본: 0.2)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="랜덤 시드 (기본: 42)",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"오류: 데이터 파일을 찾을 수 없습니다: {args.csv}")
        print("Pima Indians Diabetes Dataset (당뇨.csv)를 해당 경로에 배치하세요.")
        return

    print("=" * 60)
    print("당뇨 예측 모델 학습")
    print("=" * 60)

    # 1. 데이터 로드
    df = load_data(args.csv)
    print(f"\n데이터 로드: {len(df)}행")

    # 2. 전처리
    X, y, scaler_stats = preprocess(df)
    print("\n[Scaler 통계 - model_loader.py에 반영용]")
    for k, (mean, std) in scaler_stats.items():
        print(f"  {k}: ({mean:.6f}, {std:.6f})")

    # 3. train/test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )
    print(f"\n학습: {len(X_train)} / 테스트: {len(X_test)}")

    # 4. 모델 학습
    # 혈당 포함: AdaBoost
    model_sugar = AdaBoostClassifier(n_estimators=100, learning_rate=1.0, random_state=args.seed)
    train_and_evaluate(
        X_train, X_test, y_train, y_test,
        FEATURES_SUGAR, "혈당 포함 (AdaBoost)", model_sugar,
    )

    # 혈당 미포함: RandomForest
    model_no_sugar = RandomForestClassifier(
        n_estimators=100, max_depth=5, random_state=args.seed
    )
    train_and_evaluate(
        X_train, X_test, y_train, y_test,
        FEATURES_NO_SUGAR, "혈당 미포함 (RandomForest)", model_no_sugar,
    )

    # 5. 저장
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path_sugar = args.output_dir / "model_sugar.joblib"
    path_no_sugar = args.output_dir / "model_no_sugar.joblib"

    joblib.dump(model_sugar, path_sugar)
    joblib.dump(model_no_sugar, path_no_sugar)
    print(f"\n모델 저장 완료:")
    print(f"  {path_sugar}")
    print(f"  {path_no_sugar}")

    # 6. scaler 통계 출력 (model_loader.py 업데이트용)
    print("\n" + "=" * 60)
    print("model_loader.py SCALER_STATS 업데이트용:")
    print("=" * 60)
    print('SCALER_STATS: dict[str, tuple[float, float]] = {')
    for k, (mean, std) in scaler_stats.items():
        print(f'    "{k}": ({mean:.6f}, {std:.6f}),')
    print("}")

    print("\n학습 완료.")


if __name__ == "__main__":
    main()

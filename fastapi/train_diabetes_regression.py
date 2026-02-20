"""
sklearn 당뇨 데이터셋 + 다중 선형 회귀 학습 및 예측력 평가

- sklearn.datasets.load_diabetes 사용 (442 samples, 10 features)
- 타겟: 당뇨병 진행 지표 (25~346, 연속값)
- LinearRegression으로 학습 후 R², MSE, MAE, RMSE로 예측력 측정

참고:
  - https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html
  - https://modulabs.co.kr/blog/diabetes-dataset-multi-linear-regression
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def main() -> None:
    parser = argparse.ArgumentParser(description="당뇨 데이터셋 선형 회귀 학습 및 예측력 평가")
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
    parser.add_argument(
        "--save",
        action="store_true",
        help="학습된 모델을 joblib으로 저장",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("sklearn 당뇨 데이터셋 + 다중 선형 회귀")
    print("=" * 60)

    # 1. 데이터 로드 (scaled=True: 피처가 이미 정규화됨)
    diabetes = load_diabetes(scaled=True)
    X, y = diabetes.data, diabetes.target
    feature_names = diabetes.feature_names

    print(f"\n데이터: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"피처: {list(feature_names)}")
    print(f"타겟 범위: {y.min():.0f} ~ {y.max():.0f} (당뇨병 진행 지표)")

    # 2. train/test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed
    )
    print(f"\n학습: {len(X_train)} / 테스트: {len(X_test)}")

    # 3. 다중 선형 회귀 학습
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 4. 예측
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # 5. 예측력 평가
    print("\n" + "=" * 60)
    print("예측력 평가 (Prediction Performance)")
    print("=" * 60)

    # 학습 세트
    r2_train = r2_score(y_train, y_pred_train)
    mse_train = mean_squared_error(y_train, y_pred_train)
    rmse_train = np.sqrt(mse_train)
    mae_train = mean_absolute_error(y_train, y_pred_train)

    print("\n[학습 세트]")
    print(f"  R² (결정계수):     {r2_train:.4f}")
    print(f"  MSE (평균제곱오차): {mse_train:.2f}")
    print(f"  RMSE:              {rmse_train:.2f}")
    print(f"  MAE (평균절대오차): {mae_train:.2f}")

    # 테스트 세트
    r2_test = r2_score(y_test, y_pred_test)
    mse_test = mean_squared_error(y_test, y_pred_test)
    rmse_test = np.sqrt(mse_test)
    mae_test = mean_absolute_error(y_test, y_pred_test)

    print("\n[테스트 세트]")
    print(f"  R² (결정계수):     {r2_test:.4f}")
    print(f"  MSE (평균제곱오차): {mse_test:.2f}")
    print(f"  RMSE:              {rmse_test:.2f}")
    print(f"  MAE (평균절대오차): {mae_test:.2f}")

    # 6. 회귀 계수 (피처별 기여도)
    print("\n" + "=" * 60)
    print("회귀 계수 (Feature Coefficients)")
    print("=" * 60)
    for name, coef in zip(feature_names, model.coef_):
        print(f"  {name:>6}: {coef:>10.4f}")
    print(f"  (절편): {model.intercept_:.4f}")

    # 7. 모델 저장
    if args.save:
        output_dir = Path(__file__).resolve().parent / "app"
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "model_diabetes_regression.joblib"
        joblib.dump(model, path)
        print(f"\n모델 저장: {path}")

    print("\n완료.")


if __name__ == "__main__":
    main()

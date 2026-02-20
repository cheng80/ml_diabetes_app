"""
KNHANES 기반 당뇨 예측 모델 학습 및 검증 파이프라인

- HN19_ALL.sav (국민건강영양조사 2019) 사용
- 피처: 성별, 나이(19+), BMI, 허리둘레, (선택)혈당
- 타겟: HE_DM_HbA1c (3=당뇨, 1·2=비당뇨)
- 다중 알고리즘 비교 + 하이퍼파라미터 튜닝 + 교차검증
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.impute import KNNImputer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.svm import SVC

# pyreadstat for .sav (optional)
try:
    import pyreadstat
    HAS_PYREADSTAT = True
except ImportError:
    HAS_PYREADSTAT = False

# imbalanced-learn for SMOTE (optional)
try:
    from imblearn.over_sampling import SMOTE
    HAS_IMBLEARN = True
except ImportError:
    HAS_IMBLEARN = False

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
DEFAULT_SAV_PATH = APP_DIR / "resources" / "data" / "HN19_ALL.sav"
OUTPUT_DIR = APP_DIR / "app"

FEATURES_NO_GLU = ["sex", "age", "HE_BMI", "HE_wc"]
FEATURES_WITH_GLU = ["sex", "age", "HE_BMI", "HE_wc", "HE_glu"]
TARGET_COL = "HE_DM_HbA1c"
MIN_AGE = 19

# KNHANES: 1=정상, 2=전당뇨, 3=당뇨 → 이진화: 3=당뇨(1), 1·2=비당뇨(0)
TARGET_DIABETES_VALUE = 3.0

# ---------------------------------------------------------------------------
# 모델 후보 및 하이퍼파라미터 그리드
# ---------------------------------------------------------------------------
MODEL_GRIDS = {
    "LogisticRegression": {
        "model": LogisticRegression(max_iter=2000, random_state=42),
        "param_grid": {
            "C": [0.01, 0.1, 1.0],  # 10.0 제외 (수치 불안정)
            "solver": ["lbfgs", "liblinear"],
            "class_weight": [None, "balanced"],
        },
    },
    "SGDClassifier": {
        "model": SGDClassifier(loss="log_loss", random_state=42, n_iter_no_change=10),
        "param_grid": {
            "max_iter": [500, 1000, 2000, 5000],  # 에포크
            "learning_rate": ["constant", "adaptive"],
            "eta0": [0.001, 0.01, 0.1],
            "alpha": [0.0001, 0.001, 0.01],
            "class_weight": [None, "balanced"],
        },
    },
    "RandomForest": {
        "model": RandomForestClassifier(random_state=42),
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "max_depth": [3, 5, 7, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "class_weight": [None, "balanced"],
        },
    },
    "GradientBoosting": {
        "model": GradientBoostingClassifier(random_state=42),
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "learning_rate": [0.01, 0.1, 0.2],
            "max_depth": [3, 5, 7],
            "min_samples_split": [2, 5],
            "min_samples_leaf": [1, 2],
        },
    },
    "AdaBoost": {
        "model": AdaBoostClassifier(random_state=42),
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "learning_rate": [0.5, 1.0, 1.5],
        },
    },
    "KNN": {
        "model": KNeighborsClassifier(),
        "param_grid": {
            "n_neighbors": [3, 5, 7, 11, 15, 21],
            "weights": ["uniform", "distance"],
            "p": [1, 2],
        },
    },
    "SVM": {
        "model": SVC(probability=True, random_state=42),
        "param_grid": {
            "C": [0.1, 1.0, 10.0],
            "kernel": ["rbf", "linear"],
            "gamma": ["scale", "auto"],
            "class_weight": [None, "balanced"],
        },
    },
    "MLPClassifier": {
        "model": MLPClassifier(random_state=42, early_stopping=True),
        "param_grid": {
            "hidden_layer_sizes": [(64, 32), (128, 64), (64, 32, 16)],
            "activation": ["relu", "tanh"],
            "solver": ["adam"],
            "max_iter": [500, 1000, 2000],  # 에포크
            "learning_rate_init": [0.001, 0.01],
            "alpha": [0.0001, 0.01],
            "batch_size": [32, 64],
        },
    },
}


def _reduce_grids() -> None:
    """빠른 검증용 그리드 축소"""
    for config in MODEL_GRIDS.values():
        new_grid = {}
        for pk, pv in config["param_grid"].items():
            if isinstance(pv, (list, tuple)) and len(pv) > 2:
                new_grid[pk] = list(pv)[:2]
            else:
                new_grid[pk] = pv
        config["param_grid"] = new_grid


def load_knhanes(sav_path: Path) -> pd.DataFrame:
    """KNHANES SAV 파일 로드"""
    if not HAS_PYREADSTAT:
        raise ImportError("pyreadstat 필요: pip install pyreadstat")
    df, _ = pyreadstat.read_sav(str(sav_path))
    return df


def prepare_data(
    df: pd.DataFrame,
    use_glucose: bool,
    feature_eng: bool = False,
    glucose_scale: float = 1.0,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """
    데이터 전처리 및 타겟 이진화
    - 만19세 이상
    - 필수 피처 결측 제외
    - feature_eng: 파생 피처 추가 (허리-신장비, BMI*허리 등)
    - glucose_scale: 혈당 영향도 조절 (0.5~1.0, 1.0=기본). KNN 등에서 혈당 의존도 감소
    """
    features = list(FEATURES_WITH_GLU if use_glucose else FEATURES_NO_GLU)

    # 만19세 이상
    df_adult = df[df["age"] >= MIN_AGE].copy()

    # 혈당 스케일 (혈당 의존도 감소용)
    if use_glucose and "HE_glu" in df_adult.columns and glucose_scale != 1.0:
        df_adult = df_adult.copy()
        df_adult["HE_glu"] = df_adult["HE_glu"] * glucose_scale

    # 파생 피처
    if feature_eng and "HE_ht" in df_adult.columns:
        df_adult["HE_whr"] = df_adult["HE_wc"] / df_adult["HE_ht"]
        df_adult["HE_bmi_wc"] = df_adult["HE_BMI"] * (df_adult["HE_wc"] / 100)
        features = features + ["HE_whr", "HE_bmi_wc"]

    # 타겟: 3=당뇨(1), 1·2=비당뇨(0)
    df_adult["_target"] = (df_adult[TARGET_COL] == TARGET_DIABETES_VALUE).astype(int)

    required = features + ["_target"]
    df_clean = df_adult.dropna(subset=required)

    X = df_clean[features]
    y = df_clean["_target"]
    return X, y, features


def add_polynomial_features(
    X_train: np.ndarray,
    X_test: np.ndarray,
    degree: int = 2,
    interaction_only: bool = True,
) -> tuple[np.ndarray, np.ndarray, Any]:
    """상호작용 항 추가 (age*BMI, BMI*waist 등)"""
    poly = PolynomialFeatures(degree=degree, interaction_only=interaction_only, include_bias=False)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)
    return X_train_poly, X_test_poly, poly


def impute_and_scale(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, Any, Any]:
    """KNN 임퓨트 + StandardScaler (학습 데이터 기준 fit)"""
    imputer = KNNImputer(n_neighbors=5)
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_imp)
    X_test_scaled = scaler.transform(X_test_imp)

    return X_train_scaled, X_test_scaled, imputer, scaler


def _balanced_recall_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """balanced_accuracy와 recall(당뇨 발견율)의 가중 평균 (선별용)"""
    ba = balanced_accuracy_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred, zero_division=0)
    return 0.6 * ba + 0.4 * rec


SCORER_BALANCED_RECALL = make_scorer(_balanced_recall_score)


def run_grid_search(
    X_train: np.ndarray,
    y_train: np.ndarray,
    cv: int = 5,
    scoring: str = "balanced_recall",
    n_jobs: int = -1,
    verbose: int = 1,
) -> list[dict[str, Any]]:
    """그리드 서치로 각 모델 최적화 후 비교"""
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    results = []

    for name, config in MODEL_GRIDS.items():
        print(f"\n{'='*60}")
        print(f"[{name}] GridSearchCV 진행... (scoring={scoring})")
        print("=" * 60)

        scorer = SCORER_BALANCED_RECALL if scoring == "balanced_recall" else scoring
        search = GridSearchCV(
            config["model"],
            config["param_grid"],
            cv=skf,
            scoring=scorer,
            n_jobs=n_jobs,
            verbose=verbose,
        )
        search.fit(X_train, y_train)

        results.append({
            "model_name": name,
            "best_params": search.best_params_,
            "best_cv_score": float(search.best_score_),
            "best_estimator": search.best_estimator_,
        })
        score_name = "balanced_recall" if scoring == "balanced_recall" else scoring
        print(f"  Best {score_name} (CV): {search.best_score_:.4f}")
        print(f"  Best params: {search.best_params_}")

    return results


def find_best_threshold(
    model: Any,
    X_val: np.ndarray,
    y_val: np.ndarray,
    metric: str = "balanced_recall",
) -> tuple[float, float]:
    """
    ROC 기반 최적 임계값 탐색
    - balanced_recall: 0.6*BA + 0.4*recall (선별용, 기본)
    - balanced_accuracy: BA만 최대화
    """
    if not hasattr(model, "predict_proba"):
        return 0.5, 0.0
    y_proba = model.predict_proba(X_val)[:, 1]
    best_thresh, best_score = 0.5, 0.0
    for thresh in np.arange(0.15, 0.85, 0.02):
        y_p = (y_proba >= thresh).astype(int)
        if metric == "balanced_recall":
            score = _balanced_recall_score(y_val, y_p)
        else:
            score = balanced_accuracy_score(y_val, y_p)
        if score > best_score:
            best_score, best_thresh = score, thresh
    return best_thresh, best_score


def evaluate_model(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, float]:
    """테스트 세트 평가 (임계값 적용)"""
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
        y_pred = (y_proba >= threshold).astype(int)
    else:
        y_pred = model.predict(X_test)
        y_proba = None

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
    }
    if y_proba is not None:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba))
        except ValueError:
            metrics["roc_auc"] = 0.0

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="KNHANES 당뇨 예측 모델 학습 및 검증")
    parser.add_argument(
        "--sav",
        type=Path,
        default=DEFAULT_SAV_PATH,
        help=f"HN19_ALL.sav 경로 (기본: {DEFAULT_SAV_PATH})",
    )
    parser.add_argument(
        "--with-glucose",
        action="store_true",
        help="혈당(HE_glu) 포함 시나리오",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="테스트 세트 비율",
    )
    parser.add_argument(
        "--cv",
        type=int,
        default=5,
        help="교차검증 폴드 수",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="랜덤 시드",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="최적 모델 저장",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="빠른 검증 (그리드 축소)",
    )
    parser.add_argument(
        "--feature-eng",
        action="store_true",
        help="파생 피처 추가 (허리-신장비, BMI*허리)",
    )
    parser.add_argument(
        "--poly",
        action="store_true",
        help="상호작용 항 추가 (age*BMI, BMI*waist 등)",
    )
    parser.add_argument(
        "--score-by",
        choices=["accuracy", "balanced_accuracy", "balanced_recall", "f1", "roc_auc", "recall"],
        default="balanced_recall",
        help="모델 선정 기준 (기본: balanced_recall = 0.6*BA + 0.4*recall, 선별용)",
    )
    parser.add_argument(
        "--smote",
        action="store_true",
        help="SMOTE 오버샘플링 (클래스 불균형 완화)",
    )
    parser.add_argument(
        "--tune-threshold",
        action="store_true",
        default=True,
        help="ROC 기반 임계값 최적화 (기본: True)",
    )
    parser.add_argument(
        "--no-tune-threshold",
        action="store_true",
        help="임계값 최적화 비활성화",
    )
    parser.add_argument(
        "--glucose-scale",
        type=float,
        default=1.0,
        help="혈당 피처 스케일 (0.5~1.0). 0.7이면 혈당 영향 70%%로 감소. KNN 등에서 혈당 의존도 완화",
    )
    args = parser.parse_args()

    if not args.sav.exists():
        print(f"오류: 파일 없음: {args.sav}")
        print("HN19_ALL.sav 경로를 --sav로 지정하세요.")
        return

    if not HAS_PYREADSTAT:
        print("오류: pip install pyreadstat 필요")
        return

    print("=" * 60)
    print("KNHANES 당뇨 예측 모델 학습 및 검증")
    print("=" * 60)

    # 1. 데이터 로드
    df = load_knhanes(args.sav)
    print(f"\n데이터 로드: {len(df)}행")

    # 2. 데이터 준비
    use_glu = args.with_glucose
    scenario = "혈당 포함" if use_glu else "혈당 미포함"
    print(f"시나리오: {scenario}")
    print(f"피처 공학: feature_eng={args.feature_eng}, poly={args.poly}")
    if use_glu and args.glucose_scale != 1.0:
        print(f"혈당 스케일: {args.glucose_scale} (영향도 감소)")
    print(f"모델 선정 기준: {args.score_by}")

    X, y, features = prepare_data(
        df,
        use_glucose=use_glu,
        feature_eng=args.feature_eng,
        glucose_scale=args.glucose_scale,
    )
    print(f"분석 대상: {len(X)}행, 피처: {features}")
    print(f"당뇨 비율: {y.mean():.2%} ({y.sum():.0f}/{len(y)})")

    # 3. train/val/test 분할 (임계값 최적화용 val)
    tune_thresh = args.tune_threshold and not args.no_tune_threshold
    if tune_thresh:
        X_train, X_rest, y_train, y_rest = train_test_split(
            X, y, test_size=0.3, random_state=args.seed, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_rest, y_rest, test_size=2 / 3, random_state=args.seed, stratify=y_rest
        )
        print(f"\n학습: {len(X_train)} / 검증: {len(X_val)} / 테스트: {len(X_test)}")
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=args.seed, stratify=y
        )
        X_val, y_val = None, None
        print(f"\n학습: {len(X_train)} / 테스트: {len(X_test)}")

    # 4. 전처리 (임퓨트 + 스케일)
    X_train_s, X_test_s, imputer, scaler = impute_and_scale(X_train, X_test)

    # 4-0. 산포도용 참조 데이터 (BMI vs 허리둘레, 임퓨트 후 원본 스케일)
    scatter_data: dict[str, Any] | None = None
    if "HE_BMI" in features and "HE_wc" in features:
        X_imp = imputer.transform(X_train)
        bmi_idx = features.index("HE_BMI")
        wc_idx = features.index("HE_wc")
        bmi_arr = X_imp[:, bmi_idx]
        wc_arr = X_imp[:, wc_idx]
        y_arr = y_train.values
        # 클래스별 150개씩 샘플 (파일 크기 제한)
        idx0 = np.where(y_arr == 0)[0]
        idx1 = np.where(y_arr == 1)[0]
        n0, n1 = min(150, len(idx0)), min(150, len(idx1))
        np.random.seed(args.seed)
        sel0 = np.random.choice(idx0, n0, replace=False)
        sel1 = np.random.choice(idx1, n1, replace=False)
        sel = np.concatenate([sel0, sel1])
        scatter_data = {
            "bmi": bmi_arr[sel].tolist(),
            "wc": wc_arr[sel].tolist(),
            "y": y_arr[sel].tolist(),
        }
    if tune_thresh and X_val is not None:
        X_val_imp = imputer.transform(X_val)
        X_val_s = scaler.transform(X_val_imp)

    # 4-1. 상호작용 항 (선택)
    poly_obj: Any = None
    if args.poly:
        X_train_s, X_test_s, poly_obj = add_polynomial_features(X_train_s, X_test_s)
        if tune_thresh and X_val is not None:
            X_val_s = poly_obj.transform(X_val_s)
        print(f"\nPolynomialFeatures 적용 후: {X_train_s.shape[1]}개 피처")

    # 4-2. SMOTE (선택)
    if args.smote and HAS_IMBLEARN:
        smote = SMOTE(random_state=args.seed, k_neighbors=3)
        X_train_s, y_train = smote.fit_resample(X_train_s, y_train)
        print(f"SMOTE 적용 후 학습: {len(X_train_s)}행 (당뇨 {y_train.sum():.0f})")
    elif args.smote and not HAS_IMBLEARN:
        print("경고: imbalanced-learn 없음. pip install imbalanced-learn 후 --smote 사용")

    # 5. 빠른 모드: 그리드 축소
    if args.quick:
        _reduce_grids()

    # 6. 그리드 서치
    results = run_grid_search(
        X_train_s, y_train, cv=args.cv, scoring=args.score_by
    )

    # 7. 최적 모델 선정 (CV score 기준)
    best_result = max(results, key=lambda r: r["best_cv_score"])
    best_model = best_result["best_estimator"]

    # 7-1. 임계값 최적화 (검증 세트, balanced_recall 기준)
    threshold = 0.5
    thresh_metric = "balanced_recall" if args.score_by in ("balanced_recall", "recall") else "balanced_accuracy"
    if tune_thresh and X_val is not None and hasattr(best_model, "predict_proba"):
        threshold, thresh_score = find_best_threshold(best_model, X_val_s, y_val, metric=thresh_metric)
        print(f"\n임계값 최적화: {threshold:.2f} (val {thresh_metric}={thresh_score:.4f})")

    # 8. 테스트 세트 평가
    print("\n" + "=" * 60)
    print(f"최적 모델: {best_result['model_name']}")
    print("=" * 60)

    test_metrics = evaluate_model(best_model, X_test_s, y_test, threshold=threshold)
    for k, v in test_metrics.items():
        print(f"  {k}: {v:.4f}")

    print("\n[Classification Report]")
    if hasattr(best_model, "predict_proba"):
        y_proba = best_model.predict_proba(X_test_s)[:, 1]
        y_pred = (y_proba >= threshold).astype(int)
    else:
        y_pred = best_model.predict(X_test_s)
    print(classification_report(y_test, y_pred, target_names=["비당뇨", "당뇨"]))

    # 9. 결과 저장
    output = {
        "scenario": scenario,
        "features": features,
        "feature_eng": args.feature_eng,
        "poly": args.poly,
        "smote": args.smote,
        "glucose_scale": args.glucose_scale,
        "threshold": threshold,
        "score_by": args.score_by,
        "best_model": best_result["model_name"],
        "best_params": best_result["best_params"],
        "best_cv_score": best_result["best_cv_score"],
        "test_metrics": test_metrics,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "glu" if use_glu else "no_glu"
    result_path = OUTPUT_DIR / f"knhanes_result_{suffix}.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n결과 저장: {result_path}")

    if args.save:
        import joblib
        model_path = OUTPUT_DIR / f"model_knhanes_{suffix}.joblib"
        joblib.dump(
            {
                "model": best_model,
                "imputer": imputer,
                "scaler": scaler,
                "poly": poly_obj,
                "features": features,
                "poly_enabled": args.poly,
                "threshold": threshold,
                "scatter_data": scatter_data,
                "glucose_scale": args.glucose_scale if use_glu else 1.0,
            },
            model_path,
        )
        print(f"모델 저장: {model_path}")

    print("\n완료.")


if __name__ == "__main__":
    main()

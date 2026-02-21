# 플랜 피처(F1~F2) 사전 시뮬레이션 결과
- 데이터: KNHANES 2019 (기존)
- 모델: KNN(n=3, distance, p=2) + KNNImputer + StandardScaler + PolynomialFeatures + (가능 시)SMOTE
- 분할: train/val/test = 70/10/20, seed=42
- F3(운동량), F4(임신성 당뇨 이력): 본 결과에서 제외

## 결과 표
| scenario         | glucose_mode   |   use_optional_f12 |   n_samples |   threshold |   accuracy |   precision |   recall |     f1 |   roc_auc |   tn |   fp |   fn |   tp |
|:-----------------|:---------------|-------------------:|------------:|------------:|-----------:|------------:|---------:|-------:|----------:|-----:|-----:|-----:|-----:|
| base_no_glu      | none           |                  0 |        5874 |        0.25 |     0.6752 |      0.2607 |   0.6864 | 0.3779 |    0.696  |  678 |  329 |   53 |  116 |
| base_glu_binned  | binned         |                  0 |        5874 |        0.27 |     0.8376 |      0.4643 |   0.8462 | 0.5996 |    0.8789 |  842 |  165 |   26 |  143 |
| base_glu_exact   | exact          |                  0 |        5874 |        0.23 |     0.8359 |      0.4623 |   0.8698 | 0.6037 |    0.8874 |  836 |  171 |   22 |  147 |
| opt12_no_glu     | none           |                  1 |        5874 |        0.17 |     0.6845 |      0.2705 |   0.7041 | 0.3908 |    0.6989 |  686 |  321 |   50 |  119 |
| opt12_glu_binned | binned         |                  1 |        5874 |        0.17 |     0.8435 |      0.4752 |   0.8521 | 0.6102 |    0.8774 |  848 |  159 |   25 |  144 |
| opt12_glu_exact  | exact          |                  1 |        5874 |        0.17 |     0.8333 |      0.4577 |   0.8639 | 0.5984 |    0.8828 |  834 |  173 |   23 |  146 |

## 생성 차트
- feature_plan_sim_metrics.png
- feature_plan_sim_errors.png

# 선택형 입력 시뮬레이션 결과

- 모델/데이터: 기존 KNHANES 학습 결과 유지
- 테스트셋: KNHANES 성인 표본(동일 분할 재현, seed=42)
- 샘플 수: 1163
- 블렌드 가중치: 위험인자 0.55 / 혈당 0.45

## 성능 표


| scenario     | model_desc                         | n_samples | threshold | accuracy | precision | recall | f1     | roc_auc | tn  | fp  | fn  | tp  |
| ------------ | ---------------------------------- | --------- | --------- | -------- | --------- | ------ | ------ | ------- | --- | --- | --- | --- |
| glu_exact    | KNHANES glu model                  | 1163      | 0.15      | 0.9475   | 0.7526    | 0.9108 | 0.8242 | 0.9457  | 959 | 47  | 14  | 143 |
| glu_binned   | KNHANES glu model + bucket glucose | 1163      | 0.15      | 0.859    | 0.4877    | 0.8854 | 0.629  | 0.9116  | 860 | 146 | 18  | 139 |
| no_glu       | KNHANES no-glu model               | 1163      | 0.25      | 0.902    | 0.5923    | 0.879  | 0.7077 | 0.919   | 911 | 95  | 19  | 138 |
| blend_exact  | production blend (exact glucose)   | 1163      | 0.15      | 0.8942   | 0.562     | 0.9809 | 0.7146 | 0.9846  | 886 | 120 | 3   | 154 |
| blend_binned | production blend (bucket glucose)  | 1163      | 0.15      | 0.8564   | 0.4843    | 0.9809 | 0.6484 | 0.9786  | 842 | 164 | 3   | 154 |


## 생성 차트

- fig_simulation_metrics.png (정확도/정밀도/재현율/F1/AUC)
- fig_simulation_errors.png (FP/FN 비교)


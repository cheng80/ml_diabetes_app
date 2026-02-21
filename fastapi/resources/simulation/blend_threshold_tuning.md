# Blend 운영점 튜닝 결과

## 기준(Baseline)

- weight: `0.55`
- threshold: `0.15`
- baseline exact: FP `120`, FN `3`, Recall `0.9809`
- baseline binned: FP `164`, FN `3`, Recall `0.9809`

## 탐색 조건

- weight: `0.55` ~ `0.55` (step `0.01`)
- threshold: `0.5` ~ `0.75` (step `0.01`)
- FN 제약: 각 모드에서 baseline 대비 `+25` 이하

## 추천 운영값

- weight: `0.55`
- threshold: `0.54`
- exact: FP `32`, FN `21`, Recall `0.8662`, Accuracy `0.9544`
- binned: FP `45`, FN `20`, Recall `0.8726`, Accuracy `0.9441`
- FP total: `77` / FN total: `41`

## 파일

- 전체 탐색 결과: `/Users/cheng80/Desktop/RiverPod_Test/ml_diabetes_app/fastapi/resources/simulation/blend_threshold_sweep.csv`
- 요약: `/Users/cheng80/Desktop/RiverPod_Test/ml_diabetes_app/fastapi/resources/simulation/blend_threshold_tuning.md`

# FastAPI Resources 안내

`fastapi/resources`는 재학습/시뮬레이션/제출 관련 리소스를 모아두는 폴더입니다.

## 폴더 구조

- `data/`: 원본 데이터 다운로드 위치 (`.sav`, 원시자료 PDF)
- `simulation/`: 운영/확장 시나리오 비교 결과(CSV/MD/PNG)
- `submission/`: 제출용 문서/차트

## 데이터 파일 배치

재학습 전에 아래 파일을 `fastapi/resources/data/`에 배치하세요.

- `HN19_ALL.sav`
- `국민건강영양조사+제8기(2019-2021)+원시자료+이용지침서.pdf`

다운로드 경로(동일 폴더):

- SAV: `https://cheng80.myqnapcloud.com/ML_Source/HN19_ALL/HN19_ALL.sav`
- PDF(원본 파일명): `https://cheng80.myqnapcloud.com/ML_Source/HN19_ALL/국민건강영양조사+제8기(2019-2021)+원시자료+이용지침서.pdf`
- PDF(URL 인코딩): `https://cheng80.myqnapcloud.com/ML_Source/HN19_ALL/%EA%B5%AD%EB%AF%BC%EA%B1%B4%EA%B0%95%EC%98%81%EC%96%91%EC%A1%B0%EC%82%AC%2B%EC%A0%9C8%EA%B8%B0%282019-2021%29%2B%EC%9B%90%EC%8B%9C%EC%9E%90%EB%A3%8C%2B%EC%9D%B4%EC%9A%A9%EC%A7%80%EC%B9%A8%EC%84%9C.pdf`

터미널에서 받기(권장):

```bash
cd fastapi/resources/data
curl -L -o HN19_ALL.sav "https://cheng80.myqnapcloud.com/ML_Source/HN19_ALL/HN19_ALL.sav"
curl -L -o "국민건강영양조사+제8기(2019-2021)+원시자료+이용지침서.pdf" "https://cheng80.myqnapcloud.com/ML_Source/HN19_ALL/%EA%B5%AD%EB%AF%BC%EA%B1%B4%EA%B0%95%EC%98%81%EC%96%91%EC%A1%B0%EC%82%AC%2B%EC%A0%9C8%EA%B8%B0%282019-2021%29%2B%EC%9B%90%EC%8B%9C%EC%9E%90%EB%A3%8C%2B%EC%9D%B4%EC%9A%A9%EC%A7%80%EC%B9%A8%EC%84%9C.pdf"
```

## 재학습

학습 스크립트 기본 데이터 경로:

- `fastapi/resources/data/HN19_ALL.sav`

실행:

```bash
cd fastapi
python train_knhanes.py --with-glucose --feature-eng --poly --smote --save
python train_knhanes.py --feature-eng --poly --smote --save
```

## 시뮬레이션 (운영/확장 검증)

실험 재현 전 가상환경 활성화를 권장합니다.

```bash
cd fastapi
source .venv/bin/activate

# 운영 시나리오(glu_exact / glu_binned / no_glu / blend)
python simulate_optional_input_cases.py

# 확장 시나리오(F1/F2 분리 포함: none / f1 / f2 / f12)
python simulate_feature_plan_cases.py
```

주요 산출물:

- `resources/simulation/simulation_summary.csv`
- `resources/simulation/simulation_summary.md`
- `resources/simulation/fig_simulation_metrics.png`
- `resources/simulation/fig_simulation_errors.png`
- `resources/simulation/feature_plan_simulation_summary.csv`
- `resources/simulation/feature_plan_simulation_summary.md`
- `resources/simulation/feature_plan_sim_metrics.png`
- `resources/simulation/feature_plan_sim_errors.png`

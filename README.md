# GlucoInsight (당뇨 위험도 예측 앱)

Flutter + FastAPI 기반의 당뇨 위험도 예측 모바일 앱입니다.  
사용자가 간단한 건강 정보를 입력하면 머신러닝 모델이 당뇨 위험 확률을 분석하고,
필요 시 주변 병원 검색과 길찾기까지 연결해 줍니다.
예측 결과와 건강정보를 참고용으로 제공합니다.  
(본 앱은 의학앱이 아니며 건강 정보만을 다룹니다.)

---

## 주요 기능

### 당뇨 위험도 예측
- **간편 예측**: 나이, 키/몸무게(BMI), 임신횟수, 공복 혈당을 라디오 버튼 구간으로 선택
- **상세 예측**: 각 항목을 직접 수치로 입력
- 공복 혈당은 선택 사항이며, 입력 여부에 따라 서로 다른 모델이 적용됨
- 상세 예측의 보강 질문(F1 가족력, F2 고혈압/혈압약)은 선택 입력
  - 서버 안전장치 정책: `F2`는 KNHANES 경로에서 우선 반영, `F1`은 혈당 미입력 경로에서만 반영
  - Pima 경로에서는 `F1/F2` 입력이 자동 제외됨
- 예측 결과를 확률, 판정, 차트 이미지로 제공
- 차트: 예측 확률 + **내 수치 vs 정상 범위** (BMI·허리둘레·공복 혈당 기준선 표시)

### 병원 검색 및 길찾기
- 주소 검색 후 좌표 기반으로 주변 병원 목록 조회 (공공데이터 API)
- 병원 카드에서 길찾기 버튼을 누르면 카카오맵, 네이버지도, 티맵, Apple Maps 등 설치된 지도 앱으로 바로 연결

### 당뇨 건강정보 페이지
- 별도 페이지에서 당뇨 진단 기준, 주요 증상, 예방·관리 수칙, 응급 대응 정보를 카드형 UI로 제공
- 페이지 하단에 출처 링크를 명시하고, 링크 복사 기능 제공

### 기타
- 다크 모드 / 라이트 모드 전환
- API 서버 주소 사용자 지정 (설정 헤더 롱프레스, 디버그 모드에서만 표시)
- 주소 및 좌표 로컬 저장

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | Flutter (Dart), Material Design 3 |
| 백엔드 | FastAPI (Python) |
| ML 모델 | scikit-learn (AdaBoost, RandomForest) |
| 데이터 시각화 | Matplotlib (서버 사이드 차트 생성, Base64 전송) |
| 주소 검색 | 카카오 주소검색 API (remedi_kopo) |
| 병원 조회 | 공공데이터 건강보험심사평가원 API |
| 좌표 변환 | Nominatim (geopy) |
| 지도 연동 | map_launcher |
| 로컬 저장소 | GetStorage |

---

## 프로젝트 구조

```
diabetes_app/
├── lib/
│   ├── main.dart                          # 앱 진입점
│   ├── config.dart                        # API 키 및 기본 URL 설정
│   ├── view/
│   │   ├── main_tab_page.dart             # 메인 탭 (간편/상세 예측 전환)
│   │   ├── simple_predict_page.dart       # 간편 예측 화면
│   │   ├── detail_predict_page.dart       # 상세 예측 화면
│   │   ├── hospital_search_page.dart      # 병원 검색 + 길찾기
│   │   ├── address_search_page.dart       # 주소 검색 + 좌표 저장
│   │   └── diabetes_info_page.dart        # 당뇨 건강정보 화면(출처 포함)
│   ├── model/
│   │   └── hospital.dart                  # 병원 데이터 모델
│   ├── widgets/
│   │   ├── app_settings_drawer.dart       # 설정 드로어 (테마, API URL)
│   │   ├── age_picker.dart                # 나이 선택 (Cupertino 휠)
│   │   ├── height_weight_picker.dart      # 키/몸무게 입력 및 BMI 자동 계산
│   │   └── percentile_range_radio.dart    # 분위 구간 라디오 버튼
│   ├── constants/
│   │   └── diabetes_predict_mapping.dart  # 혈당/임신횟수 구간 매핑
│   ├── utils/
│   │   ├── app_storage.dart               # GetStorage 래퍼
│   │   ├── custom_common_util.dart        # 공통 유틸 (로딩, 스낵바, 검증 등)
│   │   ├── json/custom_json_util.dart     # JSON 파싱/변환 유틸
│   │   └── xml/custom_xml_util.dart       # XML 파싱/변환 유틸
│   ├── navigation/
│   │   └── custom_navigation_util.dart    # 커스텀 페이지 전환
│   └── theme/
│       ├── app_theme_colors.dart          # 라이트/다크 테마 색상 정의
│       └── theme_provider.dart            # 테마 상태 관리
│
├── fastapi/
│   ├── app/
│   │   ├── main.py                        # FastAPI 앱 (엔드포인트 정의)
│   │   ├── schemas.py                     # Pydantic 요청/응답 스키마
│   │   ├── predictor.py                   # 예측 로직 + 차트 생성
│   │   ├── model_loader.py                # 모델 로드 + StandardScaler 전처리
│   │   ├── geocoding.py                   # 주소 → 좌표 변환
│   │   ├── model_knhanes_glu.joblib       # KNHANES 혈당 포함 모델 번들
│   │   ├── model_knhanes_no_glu.joblib    # KNHANES 혈당 미포함 모델 번들
│   │   ├── model_sugar.joblib             # Pima 혈당 포함 모델
│   │   └── model_no_sugar.joblib          # Pima 혈당 미포함 모델
│   ├── requirements.txt
│   ├── resources/
│   │   ├── data/                         # KNHANES 원본 데이터(.sav) 및 이용지침서
│   │   ├── simulation/                   # 운영/확장 시나리오 검증 결과(CSV/MD/PNG)
│   │   └── submission/                   # 보고서/차트 산출물
│   ├── APIGUIDE.md                        # API 명세 문서
│
├── android/                               # Android 플랫폼
├── ios/                                   # iOS 플랫폼
└── pubspec.yaml                           # Flutter 의존성
```

---

## 실행 방법

### 1. FastAPI 백엔드 서버

```bash
cd fastapi
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버 실행 후 `http://localhost:8000/docs`에서 Swagger UI로 API를 테스트할 수 있습니다.

### 2. Flutter 앱

```bash
flutter pub get
flutter run
```

실기기에서 테스트할 경우, 앱 설정 드로어에서 API 서버 주소를 PC의 로컬 IP로 변경해야 합니다.  
서버의 `/health` 엔드포인트 응답에서 `suggested_url`을 확인할 수 있습니다.

---

## API 엔드포인트

| Method | URL | 설명 |
|--------|-----|------|
| GET | `/health` | 서버 상태 및 모델 정보 확인 |
| POST | `/predict` | 당뇨 위험도 예측 (확률, 판정, 차트) |
| POST | `/geocode` | 한글 주소 → 위도/경도 변환 |

`/geocode`는 주소 미일치 시 `404`, 외부 지오코딩 서비스 일시 지연/장애 시 `503`을 반환합니다.

요청/응답 상세는 [APIGUIDE.md](fastapi/APIGUIDE.md)를 참고하세요.

---

## ML 모델

- **KNHANES(기본 경로)**: 국민건강영양조사 2019 기반 모델
  - 혈당 포함/미포함 모델을 모두 사용
  - 혈당 포함 요청 시 KNHANES 혈당 포함 + 미포함 결과를 블렌딩
- **Pima(호환 경로)**: 허리둘레 미입력 등 레거시 입력 케이스 대응용

### 혈당 의존도 조절

공복 혈당만으로 과도하게 판단되는 것을 줄이기 위해 **블렌딩**을 적용합니다.

- 혈당 입력 시: `(혈당 미포함 모델 × 55%) + (혈당 포함 모델 × 45%)`로 확률 혼합
- 환경변수 `GLUCOSE_BLEND_WEIGHT=0.6`으로 비율 조정 가능 (0.6 = 혈당미포함 60%)
- 재학습 시 `--glucose-scale 0.7`로 혈당 피처 영향도 감소 가능

API에서 사용자 입력(원본 수치)을 받으면 학습 시와 동일한 전처리를 적용한 뒤 모델에 전달합니다.  
모델 선택 근거와 전처리 파이프라인 상세는 [diabetes_model_report.md](fastapi/resources/submission/diabetes_model_report.md)를 참고하세요.

### 선택형 보강 입력(F1/F2) 정책 요약

- 입력 필드: `family_history_dm(가족력)`, `htn_or_med(고혈압/혈압약)`
- KNHANES + 혈당 입력: `F2` 반영, `F1` 제외
- KNHANES + 혈당 미입력: `F1`, `F2` 조건부 반영
- Pima 경로: `F1/F2` 자동 제외
- 참고: 응답 `input`은 서버가 최종 사용한 입력값

### KNHANES 원본 데이터 위치 (재학습)

- 기본 경로: `fastapi/resources/data/HN19_ALL.sav`
- 안내 문서: `fastapi/resources/README.md`
- 제출 문서/차트: `fastapi/resources/submission/`

### KNHANES 재학습 가이드

#### 1) 데이터 파일 배치

아래 파일을 `fastapi/resources/data/`에 복사합니다.

- `HN19_ALL.sav`
- `국민건강영양조사+제8기(2019-2021)+원시자료+이용지침서.pdf` (선택, 참고용)

#### 2) Python 환경 준비

```bash
cd fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3) 모델 재학습 (혈당 포함/미포함)

```bash
cd fastapi
source .venv/bin/activate

# 혈당 포함 모델
python train_knhanes.py \
  --with-glucose \
  --feature-eng --poly --smote \
  --score-by balanced_recall \
  --save

# 혈당 미포함 모델
python train_knhanes.py \
  --feature-eng --poly --smote \
  --score-by balanced_recall \
  --save
```

#### 4) 생성 결과 확인

- 모델 파일: `fastapi/app/model_knhanes_glu.joblib`, `fastapi/app/model_knhanes_no_glu.joblib`
- 결과 JSON: `fastapi/app/knhanes_result_glu.json`, `fastapi/app/knhanes_result_no_glu.json`

#### 5) 시뮬레이션 재현 (운영/확장 검증)

```bash
cd fastapi
source .venv/bin/activate

# 운영 시나리오 (glu_exact / glu_binned / no_glu / blend)
python simulate_optional_input_cases.py

# 확장 시나리오 (F1/F2 분리: none / f1 / f2 / f12)
python simulate_feature_plan_cases.py
```

### ML 결과 리포트

- 최종 리포트: [diabetes_model_report.md](fastapi/resources/submission/diabetes_model_report.md)
- 리포트 이미지: `fastapi/resources/submission/assets/`

---

## 네이티브 권한 설정

외부 지도 앱 호출을 위해 플랫폼별 설정이 필요합니다.

**iOS** (`ios/Runner/Info.plist`) - `LSApplicationQueriesSchemes`에 `kakaomap`, `nmap`, `tmap`, `comgooglemaps`, `maps` 등록

**Android** (`android/app/src/main/AndroidManifest.xml`) - `<queries>` 블록에 `kakaomap`, `nmap`, `tmap` 인텐트 선언

---

## 개발 환경

- Flutter SDK >= 3.10.8
- Python 3.10+
- scikit-learn, FastAPI, uvicorn
- 실기기 테스트 권장 (지도 앱 연동은 시뮬레이터에서 불가)

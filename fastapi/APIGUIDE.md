# 당뇨 예측 FastAPI 가이드 (API GUIDE)

Flutter 앱과 연동되는 FastAPI 백엔드의 최신 엔드포인트/입출력 스펙입니다.

---

## 서버 실행

```bash
cd fastapi
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- 실기기 테스트 시 `--host 0.0.0.0` 권장

---

## 엔드포인트 요약

| Method | URL | 설명 |
|---|---|---|
| GET | `/health` | 서버 상태 + 로컬 접속 URL |
| POST | `/predict` | 당뇨 예측(확률/라벨/차트) |
| POST | `/geocode` | 주소 -> 위도/경도 |

---

## 1) `GET /health`

서버 상태와 실기기 연결용 IP를 반환합니다.

### 응답 예시

```json
{
  "status": "ok",
  "model_sugar": "RandomForest (혈당 포함: 혈당, BMI, 나이, 임신횟수)",
  "model_no_sugar": "RandomForest (혈당 미포함: BMI, 나이, 임신횟수)",
  "local_ip": "192.168.0.15",
  "suggested_url": "http://192.168.0.15:8000"
}
```

---

## 2) `POST /predict`

입력값으로 당뇨 위험도를 예측합니다.

- 한글 키/영문 키 모두 사용 가능 (`populate_by_name=True`)
- 최소 1개 이상 입력 필요
- 허리둘레(`waist_cm`/`허리둘레`)가 들어오면 KNHANES 분기를 우선 사용

### 요청 필드

| 영문 키 | 한글 키 | 타입 | 필수 | 비고 |
|---|---|---|---|---|
| `pregnancies` | `임신횟수` | float | 선택 | Pima 분기용 |
| `glucose` | `혈당` | float | 선택 | 혈당 포함 분기 |
| `bmi` | `BMI` | float | 선택 | |
| `age` | `나이` | float | 선택 | 범위 검증 있음 |
| `waist_cm` | `허리둘레` | float | 선택 | 있으면 KNHANES 분기 |
| `sex` | `성별` | int | 선택 | 1=남, 2=여 |
| `height_cm` | `키` | float | 선택 | KNHANES 파생피처 계산용 |

### 입력값 범위 검증

| 키 | 허용 범위 |
|---|---|
| `glucose` | 44.0 ~ 199.0 |
| `bmi` | 0.0 ~ 67.1 |
| `age` | 19.0 ~ 100.0 |
| `pregnancies` | 0.0 ~ 17.0 |
| `waist_cm` | 50.0 ~ 150.0 |
| `height_cm` | 80.0 ~ 220.0 |

### 요청 예시 (KNHANES)

```json
{
  "성별": 1,
  "나이": 47,
  "키": 170,
  "BMI": 28.0,
  "허리둘레": 94.0,
  "혈당": 95
}
```

### Flutter 요청 예시

#### A. Simple(간편) 화면 스타일 예시

혈당을 입력하지 않는 경우(허리둘레 기반 KNHANES 미포함 혈당 분기):

```json
{
  "성별": 1,
  "나이": 47,
  "키": 170,
  "BMI": 28.0,
  "허리둘레": 94.0
}
```

#### B. Detail(상세) 화면 스타일 예시

혈당을 포함하는 경우(허리둘레 + 혈당 기반 KNHANES 블렌드 분기):

```json
{
  "성별": 1,
  "나이": 47,
  "키": 170,
  "BMI": 28.0,
  "허리둘레": 94.0,
  "혈당": 95.0
}
```

#### C. Dart 코드 예시 (`http` 패키지)

```dart
final uri = Uri.parse('$baseUrl/predict');
final body = {
  '성별': 1,
  '나이': 47,
  '키': 170,
  'BMI': 28.0,
  '허리둘레': 94.0,
  '혈당': 95.0, // 필요 없으면 제거
};

final response = await http.post(
  uri,
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode(body),
);
```

### 응답 예시

```json
{
  "prediction": 1,
  "probability": 0.55,
  "label": "당뇨 위험",
  "input": {
    "glucose": 95.0,
    "bmi": 28.0,
    "age": 47.0,
    "waist_cm": 94.0,
    "sex": 1.0,
    "height_cm": 170.0
  },
  "used_model": "KNHANES 블렌드 (위험인자 55% + 혈당 45%)",
  "chart_image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### 응답 필드

| 필드 | 타입 | 설명 |
|---|---|---|
| `prediction` | int | 0=정상 범위, 1=당뇨 위험 |
| `probability` | float | 당뇨(1) 클래스 확률 |
| `label` | string | 사람이 읽는 라벨 |
| `input` | object | 서버가 실제 사용한 입력값 |
| `used_model` | string | 실제 사용 모델/분기명 |
| `chart_image_base64` | string \| null | PNG base64 이미지 |

### 모델 분기 규칙

| 조건 | 사용 모델 |
|---|---|
| `waist_cm` 있고 `glucose` 있음 | KNHANES 혈당 포함 + 혈당미포함 블렌드 |
| `waist_cm` 있고 `glucose` 없음 | KNHANES 혈당 미포함 |
| `waist_cm` 없음, `glucose` 있음 | Pima 혈당 포함 |
| `waist_cm` 없음, `glucose` 없음 | Pima 혈당 미포함 |

### 주요 에러

| 코드 | 상황 |
|---|---|
| 400 | 입력이 비어 있음 / 범위 벗어남 |
| 503 | 필요한 모델 파일이 없음 |

---

## 3) `POST /geocode`

주소 문자열을 위도/경도로 변환합니다. (`geopy` Nominatim 사용)

### 요청 예시

```json
{
  "address": "서울특별시 송파구 중대로 191"
}
```

### 응답 예시

```json
{
  "lat": "37.4990789571513",
  "lng": "127.125683181707"
}
```

### 에러

| 코드 | 상황 |
|---|---|
| 404 | 주소를 찾지 못함 |
| 503 | 지오코딩 서비스 일시 지연/장애 (잠시 후 재시도) |

---

## 프로젝트 파일 요약

```text
fastapi/
├── APIGUIDE.md (API 명세 문서)
├── requirements.txt (Python 의존성 목록)
├── train_knhanes.py (KNHANES 모델 학습/검증/저장 스크립트)
└── app/
    ├── main.py (FastAPI 앱 시작점, 라우팅)
    ├── schemas.py (요청/응답 Pydantic 스키마)
    ├── predictor.py (예측 분기, 확률 계산, 차트 생성)
    ├── geocoding.py (주소 -> 위도/경도 변환)
    ├── model_loader.py (모델/전처리 객체 로드)
    ├── model_knhanes_glu.joblib (KNHANES 혈당 포함 모델 번들)
    ├── model_knhanes_no_glu.joblib (KNHANES 혈당 미포함 모델 번들)
    ├── model_sugar.joblib (Pima 혈당 포함 모델)
    └── model_no_sugar.joblib (Pima 혈당 미포함 모델)
```
# GlucoInsight 스토어 등록 메타데이터 (Google Play / Apple App Store)

최종 업데이트: 2026-02-26  
앱: `GlucoInsight` (`com.cheng80.glucoinsight`)

이 문서는 기존 타 앱(HabitCell) 문서를 **현재 프로젝트(당뇨 위험도 예측 앱)** 기준으로 전면 교체한 버전입니다.  
목표는 아래 3가지입니다.

1. 심사 시 필요한 **필수 입력 항목** 누락 방지
2. 콘솔에 바로 붙여 넣을 수 있는 **제출 초안(ko-KR / en-US)** 제공
3. 의료/건강 앱에서 중요한 **오해 방지 문구(진단 대체 아님)** 반영

---

## 1) 앱 기준 핵심 정보 (프로젝트 기준)

- 앱 이름: `GlucoInsight`
- Android package: `com.cheng80.glucoinsight`
- iOS display name: `GlucoInsight`
- 앱 버전: `1.0.0+1`
- 카테고리 제안:
  - Google Play: `Health & Fitness`
  - Apple App Store: `Medical` 또는 `Health & Fitness` 중 택1
- 지원 이메일: `cheng80@gmail.com` (기존 운영 이메일 기준)
- 광고: `없음` (현재 코드 기준 광고 SDK 없음)
- 로그인/계정: `없음`
- 타겟 사용자: `성인` (예측 입력이 성인 기준)

### 정책 URL (현재 상태)

현재 레포에는 GlucoInsight 전용 웹 정책 페이지가 아직 보이지 않습니다.  
스토어 제출 전 아래 URL을 **실제 생성 후 치환**하세요.

- 개인정보처리방침: `https://cheng80.myqnapcloud.com/glucoinsight/privacy.html`
- 이용약관(선택): `https://cheng80.myqnapcloud.com/glucoinsight/terms.html`
- 마케팅/소개 페이지(선택): `https://cheng80.myqnapcloud.com/glucoinsight/index.html`

---

## 2) 앱 특징/목적/유의사항 정리 (스토어 설명 핵심)

### 앱 목적
- 성인 사용자가 나이, 키/몸무게(BMI), 허리둘레, 공복혈당(선택) 등 생활·신체 정보를 입력해  
  **당뇨 위험도(참고용)를 빠르게 확인**하도록 돕는 앱

### 주요 기능
- 심플 예측 / 상세 예측 2가지 모드
- BMI 자동 계산, 허리둘레 단위 변환(cm/inch)
- 예측 결과 확률 표시 + 결과 설명 화면
- 주소 저장 후 주변 병원 검색/길찾기 연동
- 당뇨 건강정보(참고 기준/생활수칙/응급 대응 요약) 제공

### 반드시 포함할 유의사항(심사/신뢰성)
- 본 앱은 **의료 진단·치료를 제공하지 않음**
- 결과는 **건강관리 참고용**이며 의학적 판단은 의료진 상담 필요
- 응급 증상/이상 수치 시 즉시 의료기관 방문 권고

---

## 3) Google Play 제출용 입력안 (ko-KR / en-US)

## A. Product details

### ko-KR
- App name (<=30): `GlucoInsight`
- Short description (<=80):
  `성인 당뇨 위험도를 간편/상세 입력으로 예측하고 병원 찾기까지 지원`
- Full description (<=4000):

```text
GlucoInsight는 성인 사용자가 생활·신체 입력값을 바탕으로 당뇨 위험도를 참고용으로 확인할 수 있도록 돕는 건강관리 앱입니다.

[핵심 기능]
- 심플/상세 2가지 예측 모드
- 나이, 성별, 키·몸무게(BMI), 허리둘레, 공복혈당(선택) 기반 위험도 예측
- 결과(위험도 확률) 시각화 및 안내 문구 제공
- 주소 저장 후 주변 병원 검색 및 길찾기 연동
- 당뇨 관련 기본 건강정보(평가 참고 기준/생활수칙/응급 대응) 제공
- 라이트/다크 테마 지원

[중요 안내]
- 본 앱은 의료 진단 또는 치료를 제공하지 않습니다.
- 예측 결과는 건강관리 참고용이며, 의학적 판단과 치료 결정은 의료진 상담이 필요합니다.
- 증상 악화 또는 이상 수치가 의심되면 의료기관에 방문하세요.

[개인정보 및 데이터]
- 앱 기능 제공을 위해 입력값(예: 신체 정보, 혈당 입력값, 주소)이 서버 API 호출에 사용될 수 있습니다.
- 저장 데이터 일부는 기기 로컬 저장소에 보관됩니다.
- 실제 수집/공유 항목은 개인정보처리방침과 Data safety 항목에 따릅니다.

[권한 안내]
- 위치/주소 관련 기능은 사용자가 주소를 입력해 병원 찾기를 이용할 때 사용됩니다.
- 일부 권한을 허용하지 않아도 핵심 예측 기능은 사용 가능합니다.
```

### en-US
- App name (<=30): `GlucoInsight`
- Short description (<=80):
  `Estimate adult diabetes risk with simple/detailed input and nearby hospital search.`
- Full description (<=4000):

```text
GlucoInsight helps adults estimate diabetes risk for self-care reference using lifestyle and body-related inputs.

[Key Features]
- Two prediction modes: Simple and Detailed
- Risk estimation using age, sex, height/weight (BMI), waist circumference, and optional fasting glucose
- Probability-based result display with guidance text
- Save address and search nearby hospitals with map directions
- Built-in diabetes health info (reference criteria, lifestyle tips, emergency guidance)
- Light/Dark theme support

[Important Notice]
- This app does not provide medical diagnosis or treatment.
- Prediction results are for personal health management reference only.
- For medical decisions, diagnosis, or treatment, consult healthcare professionals.
- If you have severe symptoms or abnormal readings, seek medical care immediately.

[Privacy and Data]
- Input data (for example body metrics, glucose input, address) may be transmitted to APIs to provide app features.
- Some data is stored locally on the device.
- Refer to the Privacy Policy and Data safety form for exact data handling details.

[Permissions]
- Address/location-related features are used when users search for nearby hospitals.
- Core prediction features are still available even if optional permissions are denied.
```

---

## B. Graphics checklist (Play)

| 항목 | 필수 여부 | 규격 |
|---|---|---|
| App icon | 필수 | `512 x 512` PNG (32-bit, alpha), 최대 1024KB |
| Feature graphic | 필수 | `1024 x 500` JPG 또는 24-bit PNG |
| Phone screenshots | 필수 | 최소 2장, 최대 8장/기기타입 |

권장 제작:
- 세로 `1080 x 1920` 기준으로 4~8장
- 실제 앱 흐름 순서 추천: 예측 입력 -> 결과 -> 병원찾기 -> 건강정보 -> 설정

---

## C. App content / Data safety 입력 가이드 (GlucoInsight 기준)

> 최종 제출 전 서버 로그/SDK 동작을 기준으로 실제 값으로 최종 확정하세요.

- Ads declaration: `No`
- App access: `No restrictions` (로그인/계정 없음)
- Target audience: `성인 중심` (아동 대상 아님)
- Health declaration: 예측 참고 앱으로 제출, 진단/치료 대체 아님 고지 유지

Data safety 초안(검토용):
- Data collected: `Yes` (건강 관련 입력값, 주소 정보가 기능 수행을 위해 전송될 수 있음)
- Data shared: `No` 또는 `제3자 공유 없음` (실제 운영 구조 재확인 필요)
- Data processed purpose:
  - App functionality (예측/병원검색 기능 제공)
  - Analytics/Advertising 목적은 현재 코드 기준 없음

---

## 4) Apple App Store 제출용 입력안 (ko / en)

## A. App Information

- Name: `GlucoInsight` (<=30)
- Subtitle (ko): `당뇨 위험도 참고 예측` (<=30)
- Subtitle (en): `Diabetes Risk Estimator` (<=30)
- Primary Category: `Medical` 또는 `Health & Fitness`
- Age Rating: 성인 건강정보/예측앱 기준 설문 응답
- Privacy Policy URL: `https://cheng80.myqnapcloud.com/glucoinsight/privacy.html`

---

## B. Version metadata

### Promotional Text (선택, <=170)
- ko: `간단한 입력으로 당뇨 위험도를 빠르게 확인하고, 주변 병원 찾기와 건강 가이드까지 한 번에 확인하세요.`
- en: `Quickly estimate diabetes risk with simple inputs, then find nearby hospitals and practical health guidance in one place.`

### Description (필수, <=4000)

ko:
```text
GlucoInsight는 성인 사용자를 위한 당뇨 위험도 참고 예측 앱입니다.

주요 기능
- 심플/상세 예측 모드 제공
- BMI 자동 계산, 허리둘레 입력, 공복혈당(선택) 기반 위험도 예측
- 위험도 확률 표시 및 참고 안내
- 주소 저장 후 주변 병원 검색/길찾기
- 당뇨 건강정보(평가 참고 기준, 생활수칙, 응급 대응) 제공

중요 고지
- 본 앱은 의료 진단·치료를 제공하지 않습니다.
- 예측 결과는 건강관리 참고용이며, 의학적 판단 및 치료 결정은 의료진 상담이 필요합니다.

데이터 처리
- 기능 제공을 위해 일부 입력 데이터가 API 호출에 사용될 수 있습니다.
- 일부 정보는 기기 로컬 저장소에 저장됩니다.
```

en:
```text
GlucoInsight is an adult-focused diabetes risk estimation app for self-care reference.

Key features
- Simple and detailed prediction modes
- Risk estimation using BMI, waist circumference, and optional fasting glucose input
- Probability-based result and guidance
- Address save, nearby hospital search, and map directions
- Diabetes health info: reference criteria, lifestyle tips, and emergency guidance

Important notice
- This app does not provide medical diagnosis or treatment.
- Results are for reference only. Please consult healthcare professionals for medical decisions.

Data handling
- Some input data may be sent to APIs to provide prediction and location-based features.
- Some information is stored locally on device.
```

### Keywords (필수, <=100 bytes)
- ko 예시: `당뇨,당뇨예측,혈당,BMI,건강관리,병원찾기`
- en 예시: `diabetes,risk,glucose,bmi,health,hospital`

### Support URL (필수)
- `https://cheng80.myqnapcloud.com/glucoinsight/privacy.html` 또는 지원 페이지 URL

### Marketing URL (선택)
- `https://cheng80.myqnapcloud.com/glucoinsight/index.html`

### Copyright
- `2026 KIM TAEK KWON`

---

## C. Screenshot checklist (Apple)

프로젝트 설정(`TARGETED_DEVICE_FAMILY = "1,2"`) 기준 iPhone + iPad 스크린샷 모두 필요.

- 포맷: `.jpeg`, `.jpg`, `.png`
- 수량: 디바이스 타입별 `1~10장`
- iPhone 최소 1장, iPad 최소 1장

권장 해상도 세트:
- iPhone: `1320 x 2868` (또는 Apple 허용 대체 해상도)
- iPad: `2064 x 2752` (또는 Apple 허용 대체 해상도)

---

## 5) 제출 전 최종 체크리스트

- [x] 앱명/패키지명 확인 (`GlucoInsight`, `com.cheng80.glucoinsight`)
- [x] 의료 진단 대체 아님 문구 반영
- [ ] GlucoInsight 전용 개인정보처리방침 URL 실제 배포
- [ ] Play/App Store locale별 문구 최종 교정
- [ ] 최신 UI 기준 스크린샷 교체 (iPhone + iPad)
- [ ] Play Data safety 실제 전송 항목 최종 검증
- [ ] Apple Support URL의 연락 정보 충족 여부 점검
- [ ] App Review 연락처/전화번호 최종 입력

---

## 6) 공식 문서 출처

## Google Play (공식 Help Center)
- Create and set up your app  
  https://support.google.com/googleplay/android-developer/answer/9859152
- Add preview assets to showcase your app  
  https://support.google.com/googleplay/android-developer/answer/9866151
- Provide information for Google Play's Data safety section  
  https://support.google.com/googleplay/android-developer/answer/10787469
- Prepare your app for review  
  https://support.google.com/googleplay/android-developer/answer/9859455

## Apple App Store Connect (공식 Help)
- App information  
  https://developer.apple.com/help/app-store-connect/reference/app-information/app-information/
- Required, localizable, and editable properties  
  https://developer.apple.com/help/app-store-connect/reference/app-information/required-localizable-and-editable-properties/
- Platform version information  
  https://developer.apple.com/help/app-store-connect/reference/app-information/platform-version-information/
- Screenshot specifications  
  https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/


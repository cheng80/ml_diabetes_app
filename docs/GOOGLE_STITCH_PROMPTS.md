# GlucoInsight 앱 아이콘 & 스플래시 - Google Stitch용 프롬프트

---

## 앱 아이콘 (App Icon)

### 프롬프트 1 (혈당 곡선 + 방패)
```
Minimal flat app icon for a diabetes risk insight app named GlucoInsight. Abstract shield shape with a smooth glucose trend line inside. Primary blue (#1976D2), optional soft mint accent (#4CAF50). Clean medical-tech feel, friendly and trustworthy, no fear or emergency style. No text, no numbers. iOS and Android compatible icon style. Square 1024x1024.
```

### 프롬프트 2 (물방울 + 그래프)
```
Modern app icon for a health app focused on diabetes risk estimation. Simple blood drop symbol combined with an upward/downward soft curve (risk trend concept). Use blue (#1976D2) with light blue highlight (#64B5F6). Optional tiny green accent (#4CAF50). Flat, minimal, rounded, professional. No text. Square 1024x1024.
```

### 프롬프트 3 (초미니멀)
```
Ultra-minimal healthcare app icon. White rounded square background with a single blue glucose line symbol and a tiny shield notch. Primary color #1976D2 only, very subtle shadow, no gradient-heavy effects. Calm, clinical, trustworthy. No text. 1024x1024 square.
```

### 프롬프트 4 (양손 보호 컨셉)
```
Flat icon concept for GlucoInsight: two abstract curved shapes (like protective hands) around a central dot and short glucose line. Blue (#1976D2) dominant, soft neutral background, very clean composition. Health guidance 느낌, not diagnostic equipment style. No text, no medical cross. Square 1024x1024.
```

---

## 스플래시 이미지 (Splash Screen)

> **중요**: `flutter_native_splash`는 이미지 + 배경색만 지원합니다.  
> 스플래시에 앱명이 보이게 하려면 텍스트를 이미지에 포함해야 합니다.

### 프롬프트 1 (라이트 + 텍스트) ← 흰 배경 권장
```
App splash screen for "GlucoInsight". Minimal healthcare style. Center: simple blue glucose line + shield icon, with "GlucoInsight" text below. Background pure white (#FFFFFF) or very light gray (#F5F5F5). Optional tiny mint accent (#4CAF50). Clean sans-serif typography, premium and calm. Portrait 9:19.5. Single image with icon + text together. IMPORTANT: keep background bright, not dark.
```

### 프롬프트 2 (다크 + 텍스트)
```
Splash screen for "GlucoInsight" diabetes risk insight app. Dark charcoal background (#1A1A1A). Centered white or light-blue glucose-line shield icon with "GlucoInsight" text below in white. Optional accent #64B5F6. Minimal, premium, medical-tech mood. Single combined image. Portrait 9:19.5.
```

### 프롬프트 3 (범용 + 텍스트)
```
Minimal splash screen for mobile app. Centered "GlucoInsight" text and a simple blue (#1976D2) health insight icon (glucose curve + shield). Soft neutral background, clean and professional, no extra objects. Single combined image (logo + text). Portrait smartphone format.
```

### 프롬프트 4 (로고만 - 배경색 분리)
```
Splash center asset only for GlucoInsight. Blue (#1976D2) icon based on glucose trend line and protective shield, with optional "GlucoInsight" text below. Transparent or white background. Minimal and clean. Asset will be placed over solid color by flutter_native_splash. Square 1:1 preferred.
```

---

## 참고 사항

| 항목 | 값 |
|------|-----|
| 앱명 | GlucoInsight |
| 콘셉트 | 성인 당뇨 위험도 참고 예측, 건강 인사이트, 병원 찾기 |
| 프라이머리 | 파란색 #1976D2 |
| 보조색 | 라이트 블루 #64B5F6 |
| 액센트 | 민트/그린 #4CAF50 (긍정/안정) |
| 스타일 | Flat + Minimalism + Soft UI |

### 아이콘 규격
- iOS: 1024x1024 (App Store)
- Android: 512x512 이상 (adaptive icon용 foreground 추천)

### 스플래시 규격
- **전체 이미지**: 1242x2688 (iPhone) 또는 1080x1920 (Android) - 아이콘+텍스트 포함
- **중앙 에셋만**: 512x512~1024x1024 - 배경색은 pubspec에서 별도 지정, 이미지엔 로고(+앱명 선택)

### 적용 방법 (이미지 생성 후)
1. 이미지를 `images/splash.png` 등에 저장
2. `pubspec.yaml`에 `flutter_native_splash` 설정 추가:
```yaml
flutter_native_splash:
  color: "#F5F5F5"
  image: images/splash.png
  # 또는 image_dark, color_dark 등으로 다크 모드 지원
```
3. `dart run flutter_native_splash:create` 실행

---

## 프롬프트 작성 팁 (이 앱 전용)

- "medical diagnosis app" 대신 "risk insight app for self-care reference" 표현 사용
- 공포/응급 느낌(빨간 경고, ECG 경보) 과도 사용 금지
- "not for diagnosis" 문구는 스토어 설명에는 넣고, 아이콘/스플래시 이미지에는 넣지 않기
- 텍스트 포함 이미지 생성 시 앱명 철자 고정: `GlucoInsight`

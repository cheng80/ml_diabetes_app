# kpostal 패키지 적용 가이드 (remedi_kopo 대체)

한글 주소 검색 + 좌표 변환을 위해 `remedi_kopo` 대신 `kpostal`을 사용하는 방법입니다.

## 왜 kpostal?

| 구분 | remedi_kopo | kpostal |
|------|-------------|---------|
| API 키 | 불필요 | 불필요 |
| WebView | webview_flutter (구버전, AGP8 비호환) | flutter_inappwebview (AGP8 호환) |
| Android 빌드 | pub-cache 패치 필요 | 패치 없이 빌드 가능 |
| 유지보수 | 3년 전 업데이트 | 16개월 전 업데이트 |

---

## 1. pubspec.yaml 수정

```yaml
dependencies:
  # 제거
  # remedi_kopo: ^0.0.2

  # 추가
  kpostal: ^1.1.0
```

---

## 2. 코드 수정

### import 변경

```dart
// 제거
import 'package:remedi_kopo/remedi_kopo.dart';

// 추가
import 'package:kpostal/kpostal.dart';
```

### 주소 검색 호출부 변경

**Before (remedi_kopo)**

```dart
final KopoModel? model = await Navigator.push(
  context,
  CupertinoPageRoute(
    builder: (context) => RemediKopo(),
  ),
);

if (model != null && mounted) {
  setState(() {
    _postcodeController.text = model.zonecode ?? '';
    _addressController.text = model.address ?? '';
    _addressDetailController.text = model.buildingName ?? '';
  });
}
```

**After (kpostal)**

```dart
final Kpostal? result = await Navigator.push<Kpostal>(
  context,
  MaterialPageRoute(
    builder: (context) => KpostalView(),
  ),
);

if (result != null && mounted) {
  setState(() {
    _postcodeController.text = result.postCode;
    _addressController.text = result.userSelectedAddress;
    _addressDetailController.text = result.buildingName;
  });
}
```

### 필드 매핑표

| remedi_kopo (KopoModel) | kpostal (Kpostal) |
|------------------------|-------------------|
| `zonecode` | `postCode` |
| `address` | `userSelectedAddress` (도로명/지번 중 사용자 선택값) |
| `buildingName` | `buildingName` |

### 추가 필드 (kpostal)

필요 시 아래 필드도 사용 가능합니다.

- `roadAddress` / `jibunAddress` : 도로명 / 지번 주소
- `latitude` / `longitude` : 플랫폼 geocoding 좌표 (비동기 `latLng` getter로 설정됨)
- `kakaoLatitude` / `kakaoLongitude` : 카카오 API 좌표 (`kakaoKey` 설정 시)

---

## 3. 빌드 및 확인

```bash
flutter pub get
flutter build apk --debug   # 또는 --release
```

패치 스크립트 없이 빌드됩니다.

---

## 4. 참고

- **디버그 로그**: kpostal은 `dart:developer`의 `dev.log()`를 사용합니다. 디버그 콘솔에 출력되며, 릴리즈 빌드에서는 IDE 디버그 콘솔에는 표시되지 않습니다.
- **카카오 좌표**: `KpostalView(kakaoKey: '...')`로 카카오 JS 키를 넘기면 `kakaoLatitude`, `kakaoLongitude`를 사용할 수 있습니다. 기본값은 플랫폼 geocoding입니다.
- **로컬 서버**: `useLocalServer: true`로 설정하면 외부 호스팅 문제 시에도 동작합니다. 이 경우 Android `usesCleartextTraffic`, iOS `NSAppTransportSecurity` 설정이 필요할 수 있습니다.

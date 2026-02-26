/// 앱 전역 상수 (API 키, URL 등)
class AppConfig {
  AppConfig._();

  // ─── 공공데이터 API (병원) ─────────────────
  /// 병원정보서비스 API 서비스키
  static const String dataGoKrHospitalServiceKey =
      '0d03508ebb5909e22ed3fc1e267969327c6fb623294c05a7f878c5c5b174bbdc';

  /// 병원정보서비스 API 베이스 URL
  static const String dataGoKrHospitalBaseUrl =
      'https://apis.data.go.kr/B552657/HsptlAsembySearchService/getHsptlMdcncLcinfoInqire';

  // ─── FastAPI ───────────────────────────────
  /// 앱 최초 실행 시 사용할 FastAPI URL
  /// - null이면 플랫폼 기본값(Android: 10.0.2.2, iOS/기타: 127.0.0.1) 사용
  /// - 사용자가 드로워에서 저장한 값이 있으면 그 값을 우선 사용
  static const String? fastApiBaseUrl = 'http://cheng80.myqnapcloud.com:18002';

  /// config.fastApiBaseUrl 이 null일 때의 플랫폼 기본값
  static const String fastApiBaseUrlIosDefault = 'http://127.0.0.1:8000'; // iOS/Windows/macOS
  static const String fastApiBaseUrlAndroidDefault = 'http://10.0.2.2:8000'; // Android 에뮬

  // ─── 인앱 리뷰 ───────────────────────────────
  /// Apple App Store ID (App Store Connect > General > App Information > Apple ID)
  /// 출시 후 실제 ID로 교체 필요
  static const String appStoreId = ''; // TODO: 실제 App Store ID 입력

  /// 인앱 리뷰 요청 기준 예측 완료 횟수
  static const int reviewPromptThreshold = 3;
}

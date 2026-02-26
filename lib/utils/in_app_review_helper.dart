import 'package:glucoinsight/config.dart';
import 'package:glucoinsight/utils/app_storage.dart';
import 'package:in_app_review/in_app_review.dart';

/// 인앱 리뷰 요청 및 스토어 리스팅 오픈 헬퍼
///
/// - [requestReviewIfEligible]: 예측 완료 횟수 기반 조건부 인앱 리뷰 팝업
/// - [openStoreListing]: Drawer '평점 남기기' 버튼용 (횟수 제한 없음)
class InAppReviewHelper {
  InAppReviewHelper._();

  static final InAppReview _inAppReview = InAppReview.instance;

  /// 예측 완료 후 호출 — 조건 충족 시 인앱 리뷰 팝업을 띄운다.
  ///
  /// 조건:
  /// 1. 예측 완료 횟수가 [AppConfig.reviewPromptThreshold] 이상
  /// 2. 아직 리뷰를 요청한 적 없음
  /// 3. 플랫폼에서 리뷰 API가 사용 가능
  static Future<void> requestReviewIfEligible() async {
    await AppStorage.incrementPredictCount();

    final count = AppStorage.getPredictCount();
    if (count < AppConfig.reviewPromptThreshold) return;
    if (AppStorage.isReviewRequested()) return;

    if (await _inAppReview.isAvailable()) {
      await _inAppReview.requestReview();
      await AppStorage.markReviewRequested();
    }
  }

  /// Drawer/설정의 '평점 남기기' 버튼에서 호출 — 스토어 리뷰 화면으로 이동
  static Future<void> openStoreListing() async {
    await _inAppReview.openStoreListing(
      appStoreId: AppConfig.appStoreId,
    );
  }
}

import 'package:flutter/material.dart';

/// 예측 화면 공통 텍스트 스타일 (동일 레벨 = 동일 크기·두께)
class PredictStyles {
  PredictStyles._();

  /// 입력 섹션 라벨 (성별, 나이, 키·몸무게, 혈당, 허리둘레)
  static TextStyle sectionLabel(BuildContext context) =>
      (Theme.of(context).textTheme.titleMedium ?? const TextStyle()).copyWith(
        fontWeight: FontWeight.w500,
      );

  /// 입력 카드 내부 라벨 (키, 몸무게, BMI, 허리둘레 등)
  static TextStyle cardLabel(BuildContext context) => sectionLabel(context);

  /// 입력 카드 내부 값
  static TextStyle cardValue(BuildContext context) =>
      (Theme.of(context).textTheme.titleMedium ?? const TextStyle());
}

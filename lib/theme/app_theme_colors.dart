import 'package:flutter/material.dart';

/// 앱 전용 테마 색상 (Brightness 기반)
///
/// hivetodo 테마 톤과 통일. Theme.of(context).brightness로 라이트/다크 판별.
///
/// 사용 예시:
/// ```dart
/// Container(color: AppThemeColors.background(context))
/// Text('제목', style: TextStyle(color: AppThemeColors.textPrimary(context)))
/// final p = context.appTheme;
/// Container(color: p.background)
/// ```
class AppThemeColors {
  AppThemeColors._();

  static bool _isDark(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark;

  // ThemeData 정의용 상수 (main.dart 등에서 사용)
  static const Color lightBackground = Color(0xFFF5F5F5);
  static const Color darkBackground = Color.fromRGBO(26, 26, 26, 1);

  /// 전체 배경 색
  static Color background(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(26, 26, 26, 1)
          : const Color(0xFFF5F5F5);

  /// 카드/패널 배경 색
  static Color cardBackground(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(36, 36, 36, 1)
          : Colors.white;

  /// 시트 배경 색
  static Color sheetBackground(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(44, 44, 44, 1)
          : Colors.white;

  /// 주요 포인트 색
  static Color primary(BuildContext context) =>
      _isDark(context)
          ? Colors.white
          : const Color(0xFF1976D2);

  /// 보조 포인트 색 (당뇨 위험 등 강조)
  static Color accent(BuildContext context) =>
      Colors.red;

  /// 기본 텍스트 색
  static Color textPrimary(BuildContext context) =>
      _isDark(context)
          ? Colors.white
          : const Color(0xFF212121);

  /// 보조 텍스트 색
  static Color textSecondary(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(115, 115, 115, 1)
          : const Color(0xFF616161);

  /// 메타 텍스트 (날짜, 부가 정보)
  static Color textMeta(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(215, 215, 215, 1)
          : const Color(0xFF616161);

  /// Primary 배경 위 텍스트 색
  static Color textOnPrimary(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(26, 26, 26, 1)
          : Colors.white;

  /// BottomSheet 위 텍스트 색
  static Color textOnSheet(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(240, 240, 240, 1)
          : const Color(0xFF212121);

  /// 구분선 색
  static Color divider(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(60, 60, 60, 1)
          : const Color(0xFFE0E0E0);

  /// 아이콘 기본 색
  static Color icon(BuildContext context) =>
      _isDark(context)
          ? Colors.white
          : const Color(0xFF212121);

  /// BottomSheet 위 아이콘 색
  static Color iconOnSheet(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(180, 180, 180, 1)
          : const Color(0xFF424242);

  /// 칩 선택 배경 색
  static Color chipSelectedBg(BuildContext context) =>
      _isDark(context)
          ? Colors.white
          : const Color(0xFF212121);

  /// 칩 선택 텍스트 색
  static Color chipSelectedText(BuildContext context) =>
      _isDark(context)
          ? Colors.black
          : Colors.white;

  /// 칩 비선택 배경 색
  static Color chipUnselectedBg(BuildContext context) =>
      _isDark(context)
          ? const Color.fromRGBO(50, 50, 50, 1)
          : const Color(0xFFE0E0E0);

  /// 칩 비선택 텍스트 색
  static Color chipUnselectedText(BuildContext context) =>
      _isDark(context)
          ? Colors.white
          : const Color(0xFF212121);

  /// 당뇨 위험 강조 (예측 결과)
  static Color dangerAccent(BuildContext context) =>
      Colors.red.shade600;

  /// 정상 범위 강조 (예측 결과)
  static Color successAccent(BuildContext context) =>
      Colors.green.shade600;

  /// 경고/주의 (입력 안내 등, 흰 배경에서 가시성 확보)
  static Color warningAccent(BuildContext context) =>
      Colors.orange.shade700;
}

/// BuildContext 확장 - context.appTheme.xxx 로 접근
extension AppThemeContext on BuildContext {
  AppThemeColorsHelper get appTheme => AppThemeColorsHelper(this);
}

/// context.appTheme 접근용 헬퍼
class AppThemeColorsHelper {
  final BuildContext _context;

  AppThemeColorsHelper(this._context);

  Color get background => AppThemeColors.background(_context);
  Color get cardBackground => AppThemeColors.cardBackground(_context);
  Color get sheetBackground => AppThemeColors.sheetBackground(_context);
  Color get primary => AppThemeColors.primary(_context);
  Color get accent => AppThemeColors.accent(_context);
  Color get textPrimary => AppThemeColors.textPrimary(_context);
  Color get textSecondary => AppThemeColors.textSecondary(_context);
  Color get textMeta => AppThemeColors.textMeta(_context);
  Color get textOnPrimary => AppThemeColors.textOnPrimary(_context);
  Color get textOnSheet => AppThemeColors.textOnSheet(_context);
  Color get divider => AppThemeColors.divider(_context);
  Color get icon => AppThemeColors.icon(_context);
  Color get iconOnSheet => AppThemeColors.iconOnSheet(_context);
  Color get chipSelectedBg => AppThemeColors.chipSelectedBg(_context);
  Color get chipSelectedText => AppThemeColors.chipSelectedText(_context);
  Color get chipUnselectedBg => AppThemeColors.chipUnselectedBg(_context);
  Color get chipUnselectedText => AppThemeColors.chipUnselectedText(_context);
  Color get dangerAccent => AppThemeColors.dangerAccent(_context);
  Color get successAccent => AppThemeColors.successAccent(_context);
  Color get warningAccent => AppThemeColors.warningAccent(_context);
}

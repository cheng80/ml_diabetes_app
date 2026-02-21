import 'package:diabetes_app/constants/config_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class DiabetesInfoPage extends StatelessWidget {
  const DiabetesInfoPage({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('당뇨 건강정보'),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(ConfigUI.screenPaddingH),
          children: [
            _HeroHeaderCard(
              title: 'GlucoInsight 건강 가이드',
              subtitle:
                  '당뇨 예방과 관리에 필요한 핵심 정보를 제공합니다.\n(본 앱은 의학앱이 아니며 건강 정보만을 다룹니다.)',
            ),
            const SizedBox(height: 12),
            _InfoSectionCard(
              icon: Icons.analytics_outlined,
              title: '당뇨병 평가 참고 기준',
              children: const [
                _BulletText('당화혈색소(HbA1c) 6.5% 이상'),
                _BulletText('8시간 공복 혈당 126 mg/dL 이상'),
                _BulletText('75g 경구당부하검사 2시간 혈당 200 mg/dL 이상'),
                _BulletText('다뇨/다음/체중감소 증상 + 무작위 혈당 200 mg/dL 이상'),
              ],
              footnote: '한 가지 이상 해당되면 위험 신호에 해당할 수 있습니다.',
            ),
            const SizedBox(height: 12),
            _InfoSectionCard(
              icon: Icons.warning_amber_rounded,
              title: '이런 증상은 확인이 필요합니다',
              children: const [
                _BulletText('물을 많이 마시는데도 갈증이 계속 남'),
                _BulletText('소변 횟수/양이 갑자기 늘어남'),
                _BulletText('배고픔이 심한데 체중이 줄어듦'),
                _BulletText('피로감, 시야 흐림, 손발 저림이 지속됨'),
              ],
              footnote: '증상이 없어도 진행될 수 있으므로 정기 검진이 중요합니다.',
            ),
            const SizedBox(height: 12),
            _InfoSectionCard(
              icon: Icons.favorite_border,
              title: '예방·관리 5대 생활수칙',
              children: const [
                _BulletText('적정 체중과 허리둘레를 유지하기'),
                _BulletText('규칙적으로 운동하고 일상 활동량 늘리기'),
                _BulletText('균형 잡힌 식단으로 제때 식사하기'),
                _BulletText('금연, 절주, 숙면, 스트레스 관리'),
                _BulletText('정기 검진으로 위험 인자 확인하기'),
              ],
              footnote: '작은 습관 변화가 혈당과 합병증 위험을 크게 줄입니다.',
            ),
            const SizedBox(height: 12),
            _InfoSectionCard(
              icon: Icons.emergency_outlined,
              title: '응급 상황 간단 대응',
              children: const [
                _BulletText('저혈당 의심(식은땀, 떨림, 어지럼): 의식이 있으면 당 15g 섭취'),
                _BulletText('15분 후에도 지속되면 다시 15g 섭취'),
                _BulletText('의식 저하/구토/호흡 이상은 즉시 119 또는 응급실'),
              ],
              footnote: '이 안내는 일반 정보이며, 개인 치료 계획은 담당 의료진 지시에 따르세요.',
            ),
            const SizedBox(height: 12),
            _InfoSectionCard(
              icon: Icons.info_outline,
              title: '이 앱의 안내 범위',
              children: const [
                _BulletText('본 앱은 의학적 진단·치료를 대체하지 않습니다.'),
                _BulletText('예측 결과와 건강정보는 생활관리 참고용입니다.'),
                _BulletText('증상 또는 수치 이상 시 의료진 상담을 권장합니다.'),
              ],
              footnote: '안전한 건강관리를 위해 개인 상태에 맞는 전문의 진료를 받으세요.',
            ),
            const SizedBox(height: 16),
            Card(
              elevation: 0,
              color: colorScheme.surfaceContainerLowest,
              shape: RoundedRectangleBorder(
        borderRadius: ConfigUI.cardRadius,
        side: BorderSide(color: colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(ConfigUI.screenPaddingH),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '출처',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    const SizedBox(height: 10),
                    const _SourceItem(
                      title: '질병관리청/정책브리핑 - 당뇨병 예방·관리 5대 생활수칙',
                      url: 'https://www.korea.kr/news/policyNewsView.do?newsId=148880007',
                    ),
                    const SizedBox(height: 8),
                    const _SourceItem(
                      title: '대한당뇨병학회 - 당뇨병 기준·증상 정보',
                      url: 'https://www.diabetes.or.kr/general/info/info_01.php?con=5',
                    ),
                    const SizedBox(height: 8),
                    const _SourceItem(
                      title: 'NHS - Type 2 diabetes: food and keeping active',
                      url: 'https://www.nhs.uk/conditions/type-2-diabetes/food-and-keeping-active/',
                    ),
                    const SizedBox(height: 10),
                    Text(
                      '확인일: 2026-02-21',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HeroHeaderCard extends StatelessWidget {
  const _HeroHeaderCard({
    required this.title,
    required this.subtitle,
  });

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    // 다크모드: 밝은 그라데이션 시 글자 가림 → 진한 민트/틸 계열로 변경
    final gradientColors = isDark
        ? [
            const Color(0xFF1B3D3D),
            const Color(0xFF2A5C5C),
          ]
        : [
            colorScheme.primaryContainer,
            colorScheme.tertiaryContainer,
          ];
    final textColor = isDark ? Colors.white : colorScheme.onSurface;

    return Container(
      padding: const EdgeInsets.all(ConfigUI.screenPaddingH),
      decoration: BoxDecoration(
        borderRadius: ConfigUI.cardRadius,
        gradient: LinearGradient(
          colors: gradientColors,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                  color: textColor,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            subtitle,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: textColor,
                ),
          ),
        ],
      ),
    );
  }
}

class _InfoSectionCard extends StatelessWidget {
  const _InfoSectionCard({
    required this.icon,
    required this.title,
    required this.children,
    required this.footnote,
  });

  final IconData icon;
  final String title;
  final List<Widget> children;
  final String footnote;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: ConfigUI.cardRadius,
        side: BorderSide(color: colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(ConfigUI.screenPaddingH),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 20, color: colorScheme.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            ...children,
            const SizedBox(height: 8),
            Text(
              footnote,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _BulletText extends StatelessWidget {
  const _BulletText(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '• ',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          Expanded(
            child: Text(
              text,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}

class _SourceItem extends StatelessWidget {
  const _SourceItem({
    required this.title,
    required this.url,
  });

  final String title;
  final String url;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: ConfigUI.inputPaddingH,
        vertical: ConfigUI.inputPaddingV,
      ),
      decoration: BoxDecoration(
        borderRadius: ConfigUI.inputRadius,
        color: colorScheme.surface,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              Expanded(
                child: SelectionArea(
                  child: Text(
                    url,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: colorScheme.primary,
                        ),
                  ),
                ),
              ),
              IconButton(
                tooltip: '링크 복사',
                icon: const Icon(Icons.copy_rounded, size: 18),
                onPressed: () async {
                  await Clipboard.setData(ClipboardData(text: url));
                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context)
                    ..hideCurrentSnackBar()
                    ..showSnackBar(
                      const SnackBar(
                        content: Text('출처 링크를 복사했습니다.'),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}

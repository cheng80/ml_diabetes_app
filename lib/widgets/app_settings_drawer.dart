import 'package:diabetes_app/constants/config_ui.dart';
import 'package:diabetes_app/theme/theme_provider.dart';
import 'package:diabetes_app/utils/app_storage.dart';
import 'package:diabetes_app/utils/custom_common_util.dart';
import 'package:diabetes_app/view/address_search_page.dart';
import 'package:diabetes_app/view/diabetes_info_page.dart';
import 'package:diabetes_app/view/hospital_search_page.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';

// 세팅 드로워 (테마, API주소, 주소찾기, 병원찾기)
class AppSettingsDrawer extends StatefulWidget {
  const AppSettingsDrawer({super.key});

  @override
  State<AppSettingsDrawer> createState() => _AppSettingsDrawerState();
}

class _AppSettingsDrawerState extends State<AppSettingsDrawer> {
  bool _showApiServerTile = false;

  void _onApiUrlTap(BuildContext context) {
    final ctrl = TextEditingController(
      text: AppStorage.getApiBaseUrl() ?? '',
    );
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('API 서버 주소'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '비우면 config 초기값(없으면 플랫폼 기본값) 사용\n예: http://192.168.0.10:8000',
              style: Theme.of(ctx).textTheme.bodySmall?.copyWith(
                color: Theme.of(ctx).colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ctrl,
              decoration: const InputDecoration(
                hintText: 'http://...',
              ),
              keyboardType: TextInputType.url,
              autofocus: true,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('취소'),
          ),
          FilledButton(
            onPressed: () async {
              await AppStorage.saveApiBaseUrl(ctrl.text);
              if (ctx.mounted) Navigator.pop(ctx);
            },
            child: const Text('저장'),
          ),
        ],
      ),
    );
  }

  void _onHospitalSearchTap(BuildContext context) {
    final hasAddress = AppStorage.getAddress() != null &&
        AppStorage.getLat() != null &&
        AppStorage.getLng() != null;

    if (hasAddress) {
      final lat = double.tryParse(AppStorage.getLat() ?? '') ?? 0.0;
      final lng = double.tryParse(AppStorage.getLng() ?? '') ?? 0.0;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => HospitalSearchPage(lat: lat, lng: lng),
        ),
      );
    } else {
      showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('주소 정보 없음'),
          content: const Text('주소 정보가 없습니다.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('취소'),
            ),
            FilledButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const AddressSearchPage(),
                  ),
                );
              },
              child: const Text('확인'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 헤더: 기어 아이콘 + 세팅
            GestureDetector(
              behavior: HitTestBehavior.opaque,
              onLongPress: () {
                // 릴리즈 모드에서는 숨김 메뉴(서버 주소) 토글 비활성화
                if (kReleaseMode) return;
                setState(() => _showApiServerTile = !_showApiServerTile);
              },
              child: Padding(
                padding: const EdgeInsets.fromLTRB(
                  ConfigUI.screenPaddingH, 24, ConfigUI.screenPaddingH, 16,
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.settings,
                      size: 32,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 12),
                    Text(
                      '세팅',
                      style:
                          Theme.of(context).textTheme.headlineMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ) ??
                              const TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                              ),
                    ),
                  ],
                ),
              ),
            ),
            const Divider(height: 1),

            // 바디: 테마 변경 스위치
            SwitchListTile(
              title: const Text('다크 모드'),
              subtitle: const Text('라이트/다크 테마 전환'),
              value: context.isDarkMode,
              onChanged: (_) => context.toggleTheme(),
            ),
            const Divider(height: 1),

            if (_showApiServerTile) ...[
              // API 서버 주소 (상단 세팅 롱프레스 시 표시)
              ListTile(
                leading: const Icon(Icons.api_outlined),
                title: const Text('API 서버 주소'),
                subtitle: Text(
                  CustomCommonUtil.getApiBaseUrlSync(),
                  style: Theme.of(context).textTheme.bodySmall,
                  overflow: TextOverflow.ellipsis,
                ),
                onTap: () {
                  Navigator.pop(context);
                  _onApiUrlTap(context);
                },
              ),
              const Divider(height: 1),
            ],

            // 주소 찾기 메뉴
            ListTile(
              leading: const Icon(Icons.location_on_outlined),
              title: const Text('주소 찾기'),
              subtitle: const Text('주소 검색 후 좌표 저장'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const AddressSearchPage(),
                  ),
                );
              },
            ),
            const Divider(height: 1),

            ListTile(
              leading: const Icon(Icons.menu_book_outlined),
              title: const Text('당뇨 건강정보'),
              subtitle: const Text('평가 참고기준, 생활수칙, 응급 안내'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const DiabetesInfoPage(),
                  ),
                );
              },
            ),

            // 병원 찾기 메뉴
            ListTile(
              leading: const Icon(Icons.local_hospital_outlined),
              title: const Text('병원 찾기'),
              subtitle: const Text('근처 병원 검색'),
              onTap: () {
                Navigator.pop(context);
                _onHospitalSearchTap(context);
              },
            ),

            const Spacer(),

            // 푸터: 앱 버전 (package_info_plus)
            Padding(
              padding: const EdgeInsets.all(ConfigUI.screenPaddingH),
              child: Align(
                alignment: Alignment.center,
                child: FutureBuilder<PackageInfo>(
                  future: PackageInfo.fromPlatform(),
                  builder: (context, snapshot) {
                    final info = snapshot.data;
                    final versionText = info != null
                        ? 'v${info.version}+${info.buildNumber}'
                        : '버전 정보 확인 중...';
                    return Text(
                      versionText,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context).colorScheme.onSurfaceVariant,
                          ) ??
                          TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                    );
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

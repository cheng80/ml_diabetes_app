import 'dart:convert';

import 'package:diabetes_app/models/predict_input_profile.dart';
import 'package:diabetes_app/utils/app_storage.dart';
import 'package:diabetes_app/utils/custom_common_util.dart';
import 'package:diabetes_app/utils/in_app_review_helper.dart';
import 'package:diabetes_app/view/address_search_page.dart';
import 'package:diabetes_app/view/hospital_search_page.dart';
import 'package:diabetes_app/widgets/age_picker.dart';
import 'package:diabetes_app/widgets/height_weight_picker.dart';
import 'package:diabetes_app/widgets/sex_picker.dart';
import 'package:diabetes_app/constants/config_ui.dart';
import 'package:diabetes_app/constants/predict_styles.dart';
import 'package:diabetes_app/theme/app_theme_colors.dart';
import 'package:diabetes_app/widgets/waist_circumference_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

// 피커·텍스트박스로 입력하는 상세 예측 (허리둘레 피커, 혈당 직접입력)
class DetailPredictPage extends StatefulWidget {
  const DetailPredictPage({super.key});

  @override
  State<DetailPredictPage> createState() => _DetailPredictPageState();
}

class _DetailPredictPageState extends State<DetailPredictPage> {
  double _bmi = 0;
  int _heightCm = 170;
  int _weightKg = 70;
  int _age = 30;
  int _sex = 1;
  double _waistCm = 85;
  int _familyHistoryDm = -1; // 1=예, 0=아니오, -1=잘 모르겠음
  int _htnOrMed = -1; // 1=예, 0=아니오, -1=잘 모르겠음

  static const int _sugarMin = 44;
  static const int _sugarMax = 199;

  final _sugarCtrl = TextEditingController();
  VoidCallback? _unlistenProfile;

  @override
  void initState() {
    super.initState();
    _applyProfile(PredictInputProfile.load());
    _unlistenProfile = AppStorage.rawStorage.listenKey(
      PredictInputProfile.storageKey,
      (_) {
        if (!mounted) return;
        setState(() => _applyProfile(PredictInputProfile.load()));
      },
    );
  }

  @override
  void dispose() {
    _unlistenProfile?.call();
    _sugarCtrl.dispose();
    super.dispose();
  }

  bool _isSugarOut() {
    final text = _sugarCtrl.text.trim();
    if (text.isEmpty) return false; // 혈당 선택사항
    final v = int.tryParse(text);
    return v == null || v < _sugarMin || v > _sugarMax;
  }

  bool get _ok => _bmi > 0 && _waistCm > 0 && !_isSugarOut();

  bool get _hasSugarInput => _sugarCtrl.text.trim().isNotEmpty;
  bool get _useF1InModel => !_hasSugarInput;
  bool get _useF2InModel => true;

  void _applyProfile(PredictInputProfile profile) {
    _sex = profile.sex;
    _age = profile.age;
    _heightCm = profile.heightCm;
    _weightKg = profile.weightKg;
    _waistCm = profile.waistCm;
    _bmi = profile.bmi;
  }

  Future<void> _saveProfile() {
    return PredictInputProfile(
      sex: _sex,
      age: _age,
      heightCm: _heightCm,
      weightKg: _weightKg,
      waistCm: _waistCm,
    ).save();
  }

  Future<void> _onPredict() async {
    CustomCommonUtil.showLoadingOverlay(context, message: '당뇨 위험도를 분석 중입니다...');

    try {
      final url = '${CustomCommonUtil.getApiBaseUrlSync()}/predict';

      final body = {
        '나이': _age,
        'BMI': _bmi,
        '키': _heightCm,
        '성별': _sex,
        '허리둘레': _waistCm,
      };

      if (_hasSugarInput) {
        body['혈당'] = int.parse(_sugarCtrl.text.trim());
      }
      // F2는 우선 반영, F1은 혈당 미입력 경로에서만 조건부 반영.
      if (_useF2InModel && _htnOrMed != -1) {
        body['고혈압/혈압약'] = _htnOrMed;
      }
      if (_useF1InModel && _familyHistoryDm != -1) {
        body['가족력'] = _familyHistoryDm;
      }

      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      if (!mounted) return;
      CustomCommonUtil.hideLoadingOverlay(context);

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        _showResultDialog(data);
        InAppReviewHelper.requestReviewIfEligible();
      } else {
        CustomCommonUtil.showErrorSnackbar(
          context: context,
          message: '예측 실패: 상태 코드 ${response.statusCode}',
          position: SnackbarPosition.top,
        );
      }
    } catch (e) {
      if (!mounted) return;
      CustomCommonUtil.hideLoadingOverlay(context);
      CustomCommonUtil.logError(functionName: '_onPredict (Detail)', error: e);
      CustomCommonUtil.showErrorSnackbar(
        context: context,
        message: '서버 연결에 실패했습니다. 네트워크 상태를 확인해주세요.',
        position: SnackbarPosition.top,
      );
    }
  }

  void _showResultDialog(Map<String, dynamic> data) {
    final label = data['label'] as String;
    final probability = (data['probability'] as double) * 100;
    final chartBase64 = data['chart_image_base64'] as String?;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(ConfigUI.radiusSheet),
        ),
      ),
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.9,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          expand: false,
          builder: (context, scrollController) {
            return SafeArea(
              child: Column(
                children: [
                  const Padding(
                    padding: const EdgeInsets.symmetric(
                      vertical: ConfigUI.sheetButtonHeight - 18,
                    ),
                    child: Text(
                      'AI 분석 결과',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const Divider(height: 1),
                  Expanded(
                    child: ListView(
                      controller: scrollController,
                      padding: const EdgeInsets.all(ConfigUI.screenPaddingH),
                      children: [
                        Text(
                          label,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: data['prediction'] == 1
                                ? context.appTheme.dangerAccent
                                : context.appTheme.successAccent,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '당뇨 가능성: ${probability.toStringAsFixed(1)}%',
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontSize: 16),
                        ),
                        if (chartBase64 != null) ...[
                          const SizedBox(height: 24),
                          Image.memory(
                            base64Decode(chartBase64),
                            fit: BoxFit.contain,
                          ),
                        ],
                        const SizedBox(height: 24),
                        const Text(
                          '본 앱은 의료 진단·치료를 제공하지 않습니다.\n예측 결과는 건강관리 참고용이며,\n의학적 판단 및 치료 결정은 의료진 상담이 필요합니다.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 13, color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                  const Divider(height: 1),
                  Padding(
                    padding: const EdgeInsets.all(ConfigUI.screenPaddingH),
                    child: Row(
                      children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => Navigator.pop(context),
                            child: const Text('확인'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: FilledButton(
                            onPressed: () {
                              Navigator.pop(context);
                              final latStr = AppStorage.getLat();
                              final lngStr = AppStorage.getLng();

                              if (latStr != null && lngStr != null) {
                                final lat = double.tryParse(latStr) ?? 0.0;
                                final lng = double.tryParse(lngStr) ?? 0.0;
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) =>
                                        HospitalSearchPage(lat: lat, lng: lng),
                                  ),
                                );
                              } else {
                                CustomCommonUtil.showErrorSnackbar(
                                  context: context,
                                  message: '저장된 주소가 없습니다. 주소를 먼저 설정해주세요.',
                                  position: SnackbarPosition.top,
                                );
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) =>
                                        const AddressSearchPage(),
                                  ),
                                );
                              }
                            },
                            child: const Text('병원 찾기'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      behavior: HitTestBehavior.opaque,
      child: SafeArea(
        child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          spacing: 24,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              spacing: 12,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  spacing: 8,
                  children: [
                    Text('성별', style: PredictStyles.sectionLabel(context)),
                    SexPicker(
                      sex: _sex,
                      onChanged: (s) {
                        setState(() => _sex = s);
                        _saveProfile();
                      },
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  spacing: 12,
                  children: [
                    Text('나이', style: PredictStyles.sectionLabel(context)),
                    AgePicker(
                      initialAge: _age,
                      onChanged: (age) {
                        setState(() => _age = age);
                        _saveProfile();
                      },
                    ),
                  ],
                ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              spacing: 12,
              children: [
                Text(
                  '키·몸무게 (BMI 산출)',
                  style: PredictStyles.sectionLabel(context),
                ),
                HeightWeightPicker(
                  initialHeight: _heightCm,
                  initialWeight: _weightKg,
                  onChanged: (height, weight, bmi) {
                    setState(() {
                      _bmi = bmi;
                      _heightCm = height;
                      _weightKg = weight;
                    });
                    _saveProfile();
                  },
                ),
              ],
            ),
            WaistCircumferencePicker(
              initialCm: _waistCm.round(),
              onChanged: (cm) {
                setState(() => _waistCm = cm);
                _saveProfile();
              },
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              spacing: 8,
              children: [
                Text(
                  '공복 혈당 (mg/dL, 8시간 공복, 선택)',
                  style: PredictStyles.sectionLabel(context),
                ),
                TextFormField(
                  controller: _sugarCtrl,
                  keyboardType: TextInputType.number,
                  inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                  decoration: InputDecoration(
                    hintText: '최소 $_sugarMin, 최대 $_sugarMax (공복 기준)',
                    hintStyle: Theme.of(context).textTheme.bodySmall,
                    errorText:
                        _sugarCtrl.text.trim().isNotEmpty && _isSugarOut()
                        ? '범위를 벗어났습니다 ($_sugarMin~$_sugarMax)'
                        : null,
                    errorBorder: OutlineInputBorder(
                      borderSide: BorderSide(
                        color: context.appTheme.warningAccent,
                      ),
                    ),
                    focusedErrorBorder: OutlineInputBorder(
                      borderSide: BorderSide(
                        color: context.appTheme.warningAccent,
                      ),
                    ),
                    filled: true,
                    fillColor: Theme.of(
                      context,
                    ).colorScheme.surfaceContainerHighest,
                  ),
                  onChanged: (_) => setState(() {}),
                ),
                Text(
                  '공복 혈당 미선택 시에도 예측 가능하나, 정확도가 낮아질 수 있습니다.',
                  style:
                      (Theme.of(context).textTheme.bodySmall ??
                              const TextStyle())
                          .copyWith(color: context.appTheme.warningAccent),
                ),
              ],
            ),
            Container(
                padding: const EdgeInsets.all(ConfigUI.inputPaddingH),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: ConfigUI.inputRadius,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  spacing: 14,
                  children: [
                    Text(
                      '정확도 보강 질문 (선택)',
                      style: PredictStyles.sectionLabel(
                        context,
                      ).copyWith(fontWeight: FontWeight.bold, fontSize: 17),
                    ),
                    Text(
                      '아래 답변은 예측 정확도 보강에 참고됩니다.',
                      style:
                          (Theme.of(context).textTheme.bodyMedium ??
                                  const TextStyle())
                              .copyWith(
                                color: context.appTheme.warningAccent,
                                fontWeight: FontWeight.w600,
                              ),
                    ),
                    _RiskChoice(
                      title: '직계 가족 중 당뇨 진단 이력이 있나요?',
                      value: _familyHistoryDm,
                      onChanged: (v) => setState(() => _familyHistoryDm = v),
                    ),
                    _RiskChoice(
                      title: '고혈압 진단 또는 혈압약 복용 중인가요?',
                      value: _htnOrMed,
                      onChanged: (v) => setState(() => _htnOrMed = v),
                    ),
                  ],
                ),
              ),
            FilledButton(
              onPressed: _ok ? _onPredict : null,
              child: const Text(
                '예측하기',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
      ),
    );
  }
}

class _RiskChoice extends StatelessWidget {
  const _RiskChoice({
    required this.title,
    required this.value,
    required this.onChanged,
  });

  final String title;
  final int value;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      spacing: 10,
      children: [
        Text(
          title,
          style: (Theme.of(context).textTheme.titleSmall ?? const TextStyle())
              .copyWith(fontWeight: FontWeight.w700, fontSize: 15),
        ),
        SegmentedButton<int>(
          showSelectedIcon: false,
          expandedInsets: EdgeInsets.zero,
          style: ButtonStyle(
            textStyle: WidgetStatePropertyAll(
              (Theme.of(context).textTheme.bodyMedium ?? const TextStyle())
                  .copyWith(fontWeight: FontWeight.bold),
            ),
            minimumSize: WidgetStatePropertyAll(const Size(0, 44)),
            padding: WidgetStatePropertyAll(
              const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
            ),
            backgroundColor: WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.selected)) {
                return scheme.primaryContainer;
              }
              return scheme.surfaceContainerHighest;
            }),
            foregroundColor: WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.selected)) {
                return scheme.onPrimaryContainer;
              }
              return scheme.onSurface;
            }),
          ),
          segments: const [
            ButtonSegment(
              value: 1,
              label: Text('예', maxLines: 1, softWrap: false),
            ),
            ButtonSegment(
              value: 0,
              label: Text('아니오', maxLines: 1, softWrap: false),
            ),
            ButtonSegment(
              value: -1,
              label: Text(
                '잘 모르겠음',
                maxLines: 1,
                softWrap: false,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
          selected: {value},
          onSelectionChanged: (s) => onChanged(s.first),
        ),
      ],
    );
  }
}

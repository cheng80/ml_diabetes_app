import 'dart:convert';

import 'package:diabetes_app/utils/app_storage.dart';
import 'package:diabetes_app/utils/custom_common_util.dart';
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
  int _age = 30;
  int _sex = 1;
  double _waistCm = 85;

  static const int _sugarMin = 44;
  static const int _sugarMax = 199;

  final _sugarCtrl = TextEditingController();

  @override
  void dispose() {
    _sugarCtrl.dispose();
    super.dispose();
  }

  bool _isSugarOut() {
    final text = _sugarCtrl.text.trim();
    if (text.isEmpty) return false; // 혈당 선택사항
    final v = int.tryParse(text);
    return v == null || v < _sugarMin || v > _sugarMax;
  }

  bool get _ok =>
      _bmi > 0 && _waistCm > 0 && !_isSugarOut();

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

      if (_sugarCtrl.text.trim().isNotEmpty) {
        body['혈당'] = int.parse(_sugarCtrl.text.trim());
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
                      '분석 결과',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
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
                                    builder: (context) => HospitalSearchPage(lat: lat, lng: lng),
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
                                    builder: (context) => const AddressSearchPage(),
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
      }
    );
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
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
                      Text(
                        '성별',
                        style: PredictStyles.sectionLabel(context),
                      ),
                      SexPicker(
                        sex: _sex,
                        onChanged: (s) => setState(() => _sex = s),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    spacing: 12,
                    children: [
                      Text(
                        '나이',
                        style: PredictStyles.sectionLabel(context),
                      ),
                      AgePicker(
                        initialAge: _age,
                        onChanged: (age) => setState(() => _age = age),
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
                    onChanged: (height, weight, bmi) {
                      setState(() {
                        _bmi = bmi;
                        _heightCm = height;
                      });
                    },
                  ),
                ],
              ),
              WaistCircumferencePicker(
                initialCm: _waistCm.round(),
                onChanged: (cm) => setState(() => _waistCm = cm),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                spacing: 8,
                children: [
                  Text(
                    '공복 혈당 (mg/dL, 8시간 공복)',
                    style: PredictStyles.sectionLabel(context),
                  ),
                  TextFormField(
                    controller: _sugarCtrl,
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                    ],
                    decoration: InputDecoration(
                      hintText: '최소 $_sugarMin, 최대 $_sugarMax (공복 기준, 선택)',
                      hintStyle: Theme.of(context).textTheme.bodySmall,
                      errorText: _sugarCtrl.text.trim().isNotEmpty && _isSugarOut()
                          ? '범위를 벗어났습니다 ($_sugarMin~$_sugarMax)'
                          : null,
                      errorBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: context.appTheme.warningAccent),
                      ),
                      focusedErrorBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: context.appTheme.warningAccent),
                      ),
                      filled: true,
                      fillColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                    ),
                    onChanged: (_) => setState(() {}),
                  ),
                  Text(
                    '공복 혈당 미선택 시에도 예측 가능하나, 정확도가 낮아질 수 있습니다.',
                    style: (Theme.of(context).textTheme.bodySmall ?? const TextStyle()).copyWith(
                      color: context.appTheme.warningAccent,
                    ),
                  ),
                ],
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
    );
  }
}

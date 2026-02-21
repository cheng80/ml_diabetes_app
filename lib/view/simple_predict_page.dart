import 'dart:convert';

import 'package:diabetes_app/utils/app_storage.dart';
import 'package:diabetes_app/utils/custom_common_util.dart';
import 'package:diabetes_app/view/address_search_page.dart';
import 'package:diabetes_app/view/hospital_search_page.dart';
import 'package:diabetes_app/widgets/age_picker.dart';
import 'package:diabetes_app/widgets/height_weight_picker.dart';
import 'package:diabetes_app/widgets/percentile_range_radio.dart';
import 'package:diabetes_app/widgets/sex_picker.dart';
import 'package:diabetes_app/constants/predict_styles.dart';
import 'package:diabetes_app/widgets/waist_circumference_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// 라디오로 혈당 선택, 허리둘레 피커로 선택하는 심플 예측
class SimplePredictPage extends StatefulWidget {
  const SimplePredictPage({super.key});

  @override
  State<SimplePredictPage> createState() => _SimplePredictPageState();
}

class _SimplePredictPageState extends State<SimplePredictPage> {
  double _bmi = 0;
  int _heightCm = 170;
  int _age = 30;
  int _sex = 1;
  double _waistCm = 85;
  int? _sugarIndex;

  bool get _ok => _bmi > 0 && _waistCm > 0;

  Future<void> _onPredict() async {
    CustomCommonUtil.showLoadingOverlay(context, message: '당뇨 위험도를 분석 중입니다...');

    try {
      final url = '${CustomCommonUtil.getApiBaseUrlSync()}/predict';
      
      final sugarRange = _sugarIndex != null ? PercentileRangeRadio.bloodGlucoseRanges[_sugarIndex!] : null;

      final body = {
        '나이': _age,
        'BMI': _bmi,
        '키': _heightCm,
        '성별': _sex,
        '허리둘레': _waistCm,
        if (sugarRange != null) '혈당': (sugarRange.$1 + sugarRange.$2) / 2.0,
      };

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
      CustomCommonUtil.logError(functionName: '_onPredict (Simple)', error: e);
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
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
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
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Text(
                      '분석 결과',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const Divider(height: 1),
                  Expanded(
                    child: ListView(
                      controller: scrollController,
                      padding: const EdgeInsets.all(20),
                      children: [
                        Text(
                          label,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: data['prediction'] == 1 ? Colors.red.shade600 : Colors.green.shade600,
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
                          '본 앱은 의학적 진단·치료용 앱이 아닙니다.\n예측 결과는 참고용이며,\n정확한 판단은 의료진 상담이 필요합니다.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 13, color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                  const Divider(height: 1),
                  Padding(
                    padding: const EdgeInsets.all(16),
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
                  PercentileRangeRadio(
                    label: '공복 혈당 (mg/dL, 8시간 공복)',
                    ranges: PercentileRangeRadio.bloodGlucoseRanges,
                    selectedIndex: _sugarIndex,
                    onChanged: (index) => setState(() => _sugarIndex = index),
                  ),
                  Text(
                    '공복 혈당 미선택 시에도 예측 가능하나, 정확도가 낮아질 수 있습니다.',
                    style: (Theme.of(context).textTheme.bodySmall ?? const TextStyle()).copyWith(
                      color: Colors.red.shade400,
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

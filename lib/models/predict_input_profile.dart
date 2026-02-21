import 'package:get_storage/get_storage.dart';

/// 심플/상세 예측 화면에서 공통으로 사용하는 입력값 저장 모델
class PredictInputProfile {
  const PredictInputProfile({
    required this.sex,
    required this.age,
    required this.heightCm,
    required this.weightKg,
    required this.waistCm,
  });

  static const String storageKey = 'predict_input_profile';

  final int sex;
  final int age;
  final int heightCm;
  final int weightKg;
  final double waistCm;

  double get bmi {
    final h = heightCm / 100.0;
    if (h <= 0) return 0;
    return weightKg / (h * h);
  }

  Map<String, dynamic> toJson() {
    return {
      'sex': sex,
      'age': age,
      'heightCm': heightCm,
      'weightKg': weightKg,
      'waistCm': waistCm,
    };
  }

  factory PredictInputProfile.fromJson(Map<dynamic, dynamic> json) {
    return PredictInputProfile(
      sex: ((json['sex'] as num?)?.toInt() ?? 1).clamp(1, 2),
      age: ((json['age'] as num?)?.toInt() ?? 30).clamp(19, 120),
      heightCm: ((json['heightCm'] as num?)?.toInt() ?? 170).clamp(80, 220),
      weightKg: ((json['weightKg'] as num?)?.toInt() ?? 70).clamp(40, 300),
      waistCm: ((json['waistCm'] as num?)?.toDouble() ?? 85).clamp(50, 150),
    );
  }

  factory PredictInputProfile.defaults() {
    return const PredictInputProfile(
      sex: 1,
      age: 30,
      heightCm: 170,
      weightKg: 70,
      waistCm: 85,
    );
  }

  static PredictInputProfile load() {
    final raw = GetStorage().read(storageKey);
    if (raw is Map) {
      return PredictInputProfile.fromJson(raw);
    }
    return PredictInputProfile.defaults();
  }

  Future<void> save() async {
    await GetStorage().write(storageKey, toJson());
  }
}

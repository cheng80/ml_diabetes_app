import 'package:diabetes_app/constants/predict_styles.dart';
import 'package:flutter/material.dart';

/// 성별 선택 (KNHANES: 1=남, 2=여)
class SexPicker extends StatelessWidget {
  const SexPicker({
    super.key,
    required this.sex,
    this.onChanged,
  });

  final int sex;
  final void Function(int sex)? onChanged;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return SegmentedButton<int>(
      style: ButtonStyle(
        textStyle: WidgetStatePropertyAll(
          PredictStyles.cardValue(context).copyWith(fontWeight: FontWeight.bold),
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
        ButtonSegment(value: 1, label: Text('남성')),
        ButtonSegment(value: 2, label: Text('여성')),
      ],
      selected: {sex.clamp(1, 2)},
      onSelectionChanged: (s) => onChanged?.call(s.first),
    );
  }
}

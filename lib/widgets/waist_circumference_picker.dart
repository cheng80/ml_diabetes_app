import 'package:diabetes_app/constants/predict_styles.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

/// 허리둘레 선택 (cm/inch 스위치, CupertinoPicker)
/// API에는 항상 cm로 전송
class WaistCircumferencePicker extends StatefulWidget {
  const WaistCircumferencePicker({
    super.key,
    this.initialCm = 85,
    this.onChanged,
  });

  final int initialCm;
  final void Function(double cm)? onChanged;

  @override
  State<WaistCircumferencePicker> createState() =>
      _WaistCircumferencePickerState();
}

class _WaistCircumferencePickerState extends State<WaistCircumferencePicker> {
  static const int _cmMin = 50;
  static const int _cmMax = 150;
  static const int _inchMin = 20;
  static const int _inchMax = 60;

  late int _valueCm;
  bool _useCm = true;

  @override
  void initState() {
    super.initState();
    _valueCm = widget.initialCm.clamp(_cmMin, _cmMax);
    WidgetsBinding.instance.addPostFrameCallback((_) => _notifyChanged());
  }

  @override
  void didUpdateWidget(WaistCircumferencePicker oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialCm != widget.initialCm) {
      setState(() {
        _valueCm = widget.initialCm.clamp(_cmMin, _cmMax);
      });
    }
  }

  void _notifyChanged() {
    widget.onChanged?.call(_valueCm.toDouble());
  }

  int get _displayMin => _useCm ? _cmMin : _inchMin;

  int _displayToIndex(int displayVal) => displayVal - _displayMin;

  Future<void> _showPicker() async {
    bool modalUseCm = _useCm;
    int selectedIndex = _useCm
        ? _displayToIndex(_valueCm)
        : _displayToIndex((_valueCm / 2.54).round());

    await showCupertinoModalPopup<void>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) {
          final dispMin = modalUseCm ? _cmMin : _inchMin;
          final dispMax = modalUseCm ? _cmMax : _inchMax;
          final stepCount = dispMax - dispMin + 1;
          final unitLabel = modalUseCm ? 'cm' : 'inch';

          int indexToVal(int i) => dispMin + i;
          int valToIndex(int v) => (v - dispMin).clamp(0, stepCount - 1);

          void onUnitChanged(bool useCm) {
            setModalState(() {
              final val = indexToVal(selectedIndex);
              int newIndex;
              if (useCm) {
                final cm = modalUseCm ? val : (val * 2.54).round();
                newIndex = valToIndex(cm.clamp(_cmMin, _cmMax));
              } else {
                final inch = modalUseCm ? (val / 2.54).round() : val;
                newIndex = valToIndex(inch.clamp(_inchMin, _inchMax));
              }
              modalUseCm = useCm;
              selectedIndex = newIndex;
            });
          }

          return Container(
            height: 300,
            color: CupertinoColors.systemBackground.resolveFrom(context),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    CupertinoButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('취소'),
                    ),
                    CupertinoButton(
                      onPressed: () {
                          final val = indexToVal(selectedIndex);
                          if (modalUseCm) {
                            _valueCm = val.clamp(_cmMin, _cmMax);
                          } else {
                            _valueCm =
                                (val * 2.54).round().clamp(_cmMin, _cmMax);
                          }
                          setState(() {
                            _useCm = modalUseCm;
                            _notifyChanged();
                          });
                          Navigator.pop(context);
                        },
                        child: const Text('확인'),
                      ),
                    ],
                  ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: SegmentedButton<bool>(
                    style: ButtonStyle(
                      padding: MaterialStateProperty.all(
                        const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                      ),
                      textStyle: MaterialStateProperty.all(
                        Theme.of(context).textTheme.titleSmall,
                      ),
                    ),
                    segments: const [
                      ButtonSegment(value: true, label: Text('cm')),
                      ButtonSegment(value: false, label: Text('inch')),
                    ],
                    selected: {modalUseCm},
                    onSelectionChanged: (s) => onUnitChanged(s.first),
                  ),
                ),
                Expanded(
                  child: CupertinoPicker(
                    scrollController: FixedExtentScrollController(
                      initialItem:
                          selectedIndex.clamp(0, stepCount - 1),
                    ),
                    itemExtent: 40,
                    onSelectedItemChanged: (i) =>
                        setModalState(() => selectedIndex = i),
                    children: List.generate(
                      stepCount,
                      (i) => Center(
                        child: Text('${indexToVal(i)} $unitLabel'),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        onTap: _showPicker,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '허리둘레',
                      style: PredictStyles.cardLabel(context),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Text(
                          _useCm ? '$_valueCm cm' : '${(_valueCm / 2.54).round()} inch',
                          style: PredictStyles.cardValue(context),
                        ),
                        const SizedBox(width: 12),
                        FilledButton.tonal(
                          onPressed: () {
                            setState(() {
                              _useCm = !_useCm;
                            });
                          },
                          style: FilledButton.styleFrom(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 10,
                            ),
                            minimumSize: Size.zero,
                            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                          ),
                          child: Text(
                            _useCm ? 'inch로 보기' : 'cm로 보기',
                            style: Theme.of(context).textTheme.labelLarge,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_drop_down,
                size: 24,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

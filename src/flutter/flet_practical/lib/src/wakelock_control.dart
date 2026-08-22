import 'package:flutter/widgets.dart';
import 'package:flet/flet.dart';
import 'package:wakelock_plus/wakelock_plus.dart';

class PracticalWakelockControl extends StatefulWidget {
  final Control? parent;
  final Control control;

  const PracticalWakelockControl({
    super.key,
    required this.parent,
    required this.control,
  });

  @override
  State<PracticalWakelockControl> createState() => _PracticalWakelockControlState();
}

class _PracticalWakelockControlState extends State<PracticalWakelockControl> {
  @override
  void initState() {
    super.initState();
    _registerMethodHandlers();
  }

  void _registerMethodHandlers() {
    widget.control.invoker = (String name, dynamic args) async {
      switch (name) {
        case "enable":
          await WakelockPlus.enable();
          return true;

        case "disable":
          await WakelockPlus.disable();
          return true;

        case "toggle":
          final bool on = args is Map ? (args["on"] as bool? ?? false) : (args == true || args == "true");
          await WakelockPlus.toggle(on: on);
          return true;

        case "is_enabled":
          return await WakelockPlus.enabled;

        default:
          throw Exception("Unknown wakelock method: $name");
      }
    };
  }

  @override
  Widget build(BuildContext context) {
    return const SizedBox.shrink();
  }
}

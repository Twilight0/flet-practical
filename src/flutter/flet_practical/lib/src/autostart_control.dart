import 'package:flutter/widgets.dart';
import 'package:flet/flet.dart';
import 'package:launch_at_startup/launch_at_startup.dart';
import 'package:package_info_plus/package_info_plus.dart';

class PracticalAutostartControl extends StatefulWidget {
  final Control? parent;
  final Control control;

  const PracticalAutostartControl({
    super.key,
    required this.parent,
    required this.control,
  });

  @override
  State<PracticalAutostartControl> createState() => _PracticalAutostartControlState();
}

class _PracticalAutostartControlState extends State<PracticalAutostartControl> {
  static bool _isSetup = false;

  @override
  void initState() {
    super.initState();
    _initAutostart();
    _registerMethodHandlers();
  }

  Future<void> _initAutostart() async {
    if (_isSetup) return;
    try {
      final PackageInfo packageInfo = await PackageInfo.fromPlatform();
      launchAtStartup.setup(
        appName: packageInfo.appName.isNotEmpty ? packageInfo.appName : 'FletApp',
        appPath: '',
      );
      _isSetup = true;
    } catch (_) {
      // Ignored if unsupported on platform
    }
  }

  void _registerMethodHandlers() {
    widget.control.addInvokeMethodListener((String name, dynamic args) async {
      switch (name) {
        case "enable":
          await launchAtStartup.enable();
          return true;

        case "disable":
          await launchAtStartup.disable();
          return true;

        case "is_enabled":
          return await launchAtStartup.isEnabled();

        default:
          throw Exception("Unknown autostart method: $name");
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return const SizedBox.shrink();
  }
}

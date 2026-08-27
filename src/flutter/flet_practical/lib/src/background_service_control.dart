import 'package:flutter/widgets.dart';
import 'package:flet/flet.dart';
import 'package:flutter_foreground_task/flutter_foreground_task.dart';

class PracticalBackgroundServiceControl extends StatefulWidget {
  final Control? parent;
  final Control control;

  const PracticalBackgroundServiceControl({
    super.key,
    required this.parent,
    required this.control,
  });

  @override
  State<PracticalBackgroundServiceControl> createState() =>
      _PracticalBackgroundServiceControlState();
}

class _PracticalBackgroundServiceControlState
    extends State<PracticalBackgroundServiceControl> {
  bool _isInitialized = false;

  void _ensureInitialized() {
    if (_isInitialized) return;
    FlutterForegroundTask.init(
      androidNotificationOptions: AndroidNotificationOptions(
        channelId: 'flet_practical_background',
        channelName: 'Background Service',
        channelDescription: 'Keeps the app running in background',
        channelImportance: NotificationChannelImportance.LOW,
        priority: NotificationPriority.LOW,
      ),
      iosNotificationOptions: const IOSNotificationOptions(
        showNotification: false,
        playSound: false,
      ),
      foregroundTaskOptions: ForegroundTaskOptions(
        eventAction: ForegroundTaskEventAction.repeat(5000),
        autoRunOnBoot: false,
        allowWakeLock: true,
        allowWifiLock: false,
      ),
    );
    _isInitialized = true;
  }

  void _registerMethodHandlers() {
    widget.control.addInvokeMethodListener((String name, dynamic args) async {
      switch (name) {
        case "start":
          _ensureInitialized();
          final String title = args is Map ? (args["title"] as String? ?? "Running in background") : "Running in background";
          final String text = args is Map ? (args["text"] as String? ?? "Tap to return to app") : "Tap to return to app";
          final String channelId = args is Map ? (args["channel_id"] as String? ?? "flet_practical_background") : "flet_practical_background";
          final String channelName = args is Map ? (args["channel_name"] as String? ?? "Background Service") : "Background Service";
          FlutterForegroundTask.init(
            androidNotificationOptions: AndroidNotificationOptions(
              channelId: channelId,
              channelName: channelName,
              channelDescription: 'Keeps the app running in background',
              channelImportance: NotificationChannelImportance.LOW,
              priority: NotificationPriority.LOW,
            ),
            iosNotificationOptions: const IOSNotificationOptions(
              showNotification: false,
              playSound: false,
            ),
            foregroundTaskOptions: ForegroundTaskOptions(
              eventAction: ForegroundTaskEventAction.repeat(5000),
              autoRunOnBoot: false,
              allowWakeLock: true,
              allowWifiLock: false,
            ),
          );
          final ServiceRequestResult result =
              await FlutterForegroundTask.startService(
            notificationTitle: title,
            notificationText: text,
          );
          return result is ServiceRequestSuccess;

        case "stop":
          final ServiceRequestResult result =
              await FlutterForegroundTask.stopService();
          return result is ServiceRequestSuccess;

        case "is_running":
          return await FlutterForegroundTask.isRunningService;

        case "restart":
          if (await FlutterForegroundTask.isRunningService) {
            await FlutterForegroundTask.restartService();
            return true;
          }
          return false;

        case "is_ignoring_battery_optimizations":
          return await FlutterForegroundTask.isIgnoringBatteryOptimizations;

        case "request_ignore_battery_optimization":
          return await FlutterForegroundTask.requestIgnoreBatteryOptimization();

        case "open_ignore_battery_optimization_settings":
          return await FlutterForegroundTask.openIgnoreBatteryOptimizationSettings();

        default:
          throw Exception("Unknown background_service method: $name");
      }
    });
  }

  @override
  void initState() {
    super.initState();
    _ensureInitialized();
    _registerMethodHandlers();
  }

  @override
  Widget build(BuildContext context) {
    return const SizedBox.shrink();
  }
}

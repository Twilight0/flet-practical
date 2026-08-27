import 'package:flutter/widgets.dart';
import 'package:flet/flet.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class PracticalNotificationsControl extends StatefulWidget {
  final Control? parent;
  final Control control;

  const PracticalNotificationsControl({
    super.key,
    required this.parent,
    required this.control,
  });

  @override
  State<PracticalNotificationsControl> createState() => _PracticalNotificationsControlState();
}

class _PracticalNotificationsControlState extends State<PracticalNotificationsControl> {
  static final FlutterLocalNotificationsPlugin _notificationsPlugin = FlutterLocalNotificationsPlugin();
  static bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initPlugin();
    _registerMethodHandlers();
  }

  Future<void> _initPlugin() async {
    if (_isInitialized) return;

    const AndroidInitializationSettings androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const DarwinInitializationSettings darwinSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const LinuxInitializationSettings linuxSettings = LinuxInitializationSettings(
      defaultActionName: 'Open notification',
    );

    const InitializationSettings initSettings = InitializationSettings(
      android: androidSettings,
      iOS: darwinSettings,
      macOS: darwinSettings,
      linux: linuxSettings,
    );

    await _notificationsPlugin.initialize(
      initSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) {
        // Send click event back to Flet Python
        widget.control.triggerEvent("click", response.payload ?? "");
      },
    );

    _isInitialized = true;
  }

  void _registerMethodHandlers() {
    widget.control.invoker = (String name, dynamic args) async {
      switch (name) {
        case "request_permissions":
          bool? result;
          final android = _notificationsPlugin.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();
          if (android != null) {
            result = await android.requestNotificationsPermission();
          }
          final ios = _notificationsPlugin.resolvePlatformSpecificImplementation<
              IOSFlutterLocalNotificationsPlugin>();
          if (ios != null) {
            result = await ios.requestPermissions(alert: true, badge: true, sound: true);
          }
          return result ?? true;

        case "are_notifications_enabled":
          final androidEnabled = _notificationsPlugin.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();
          if (androidEnabled != null) {
            return await androidEnabled.areNotificationsEnabled();
          }
          return true;

        case "show":
          final int id = args["id"] ?? 0;
          final String title = args["title"] ?? "";
          final String body = args["body"] ?? "";
          final String? payload = args["payload"];
          final String channelId = args["channel_id"] ?? "flet_practical_default";
          final String channelName = args["channel_name"] ?? "Default Channel";
          final String channelDescription = args["channel_description"] ?? "";
          final bool ongoing = args["ongoing"] ?? false; // Persistent notification
          final bool autoCancel = args["auto_cancel"] ?? (!ongoing);
          final bool playSound = args["play_sound"] ?? true;
          final bool enableVibration = args["enable_vibration"] ?? true;

          final AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
            channelId,
            channelName,
            channelDescription: channelDescription,
            importance: Importance.max,
            priority: Priority.high,
            ongoing: ongoing, // Persistent in status bar
            autoCancel: autoCancel,
            playSound: playSound,
            enableVibration: enableVibration,
          );

          const DarwinNotificationDetails darwinDetails = DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
          );

          const LinuxNotificationDetails linuxDetails = LinuxNotificationDetails();

          final NotificationDetails notificationDetails = NotificationDetails(
            android: androidDetails,
            iOS: darwinDetails,
            macOS: darwinDetails,
            linux: linuxDetails,
          );

          await _notificationsPlugin.show(
            id,
            title,
            body,
            notificationDetails,
            payload: payload,
          );
          return true;

        case "cancel":
          final int id = args is Map ? (args["id"] ?? 0) : int.parse(args.toString());
          await _notificationsPlugin.cancel(id);
          return true;

        case "cancel_all":
          await _notificationsPlugin.cancelAll();
          return true;

        default:
          throw Exception("Unknown notifications method: $name");
      }
    };
  }

  @override
  Widget build(BuildContext context) {
    return const SizedBox.shrink();
  }
}

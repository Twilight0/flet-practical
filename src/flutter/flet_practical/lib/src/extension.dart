import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';

import 'clipboard_control.dart';
import 'notifications_control.dart';
import 'wakelock_control.dart';
import 'autostart_control.dart';
import 'background_service_control.dart';
import 'receive_share_control.dart';
import 'iap_control.dart';
import 'share_control.dart';

class Extension extends FletExtension {
  @override
  Widget? createWidget(Key? key, Control control) {
    switch (control.type) {
      case "practical_clipboard":
        return PracticalClipboardControl(
          key: key,
          parent: control.parent,
          control: control,
        );
      case "practical_notifications":
        return PracticalNotificationsControl(
          key: key,
          parent: control.parent,
          control: control,
        );
      case "practical_wakelock":
        return PracticalWakelockControl(
          key: key,
          parent: control.parent,
          control: control,
        );
      case "practical_autostart":
        return PracticalAutostartControl(
          key: key,
          parent: control.parent,
          control: control,
        );
      case "practical_background_service":
        return PracticalBackgroundServiceControl(
          key: key,
          parent: control.parent,
          control: control,
        );
      case "practical_receive_share":
        return PracticalReceiveShareControl(
          key: key,
          parent: control.parent,
          control: control,
        );
      case "practical_iap":
        return PracticalIapControl(
          key: key,
          parent: control.parent,
          control: control,
        );
      case "practical_share":
        return PracticalShareControl(
          key: key,
          parent: control.parent,
          control: control,
        );
      default:
        return null;
    }
  }
}

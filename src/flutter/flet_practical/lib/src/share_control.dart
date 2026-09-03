import 'package:flutter/widgets.dart';
import 'package:flet/flet.dart';
import 'package:share_plus/share_plus.dart';
import 'package:open_filex/open_filex.dart';
import 'package:url_launcher/url_launcher.dart';

class PracticalShareControl extends StatefulWidget {
  final Control? parent;
  final Control control;

  const PracticalShareControl({
    super.key,
    required this.parent,
    required this.control,
  });

  @override
  State<PracticalShareControl> createState() => _PracticalShareControlState();
}

class _PracticalShareControlState extends State<PracticalShareControl> {
  @override
  void initState() {
    super.initState();
    _registerMethodHandlers();
  }

  void _registerMethodHandlers() {
    widget.control.addInvokeMethodListener((String name, dynamic args) async {
      switch (name) {
        case "share_text":
          final String text = args is Map ? (args["text"] as String? ?? "") : args.toString();
          final String? subject = args is Map ? args["subject"] as String? : null;
          final ShareResult result = await SharePlus.instance.share(
            ShareParams(
              text: text,
              subject: subject,
            ),
          );
          return {
            "status": result.status.name, // success, dismissed, unavailable
            "raw": result.raw,
          };

        case "share_files":
          final List<String> paths = args is Map && args["paths"] is List
              ? (args["paths"] as List).map((e) => e.toString()).toList()
              : [];
          final String? text = args is Map ? args["text"] as String? : null;
          final String? subject = args is Map ? args["subject"] as String? : null;

          final List<XFile> xfiles = paths.map((p) => XFile(p)).toList();
          final ShareResult result = await SharePlus.instance.share(
            ShareParams(
              files: xfiles,
              text: text,
              subject: subject,
            ),
          );
          return {
            "status": result.status.name,
            "raw": result.raw,
          };

        case "share_uri":
          final String uriStr = args is Map ? (args["uri"] as String? ?? "") : args.toString();
          final Uri? uri = Uri.tryParse(uriStr);
          if (uri == null) {
            return {"status": "error", "error": "Invalid URI format"};
          }
          final ShareResult result = await SharePlus.instance.share(
            ShareParams(uri: uri),
          );
          return {
            "status": result.status.name,
            "raw": result.raw,
          };

        case "open_file":
          final String path = args is Map ? (args["path"] as String? ?? "") : args.toString();
          final OpenResult result = await OpenFilex.open(path);
          return {
            "type": result.type.name,
            "message": result.message,
          };

        case "open_folder":
          final String path = args is Map ? (args["path"] as String? ?? "") : args.toString();
          if (Platform.isAndroid) {
            String uriStr;
            if (path.contains("/storage/emulated/0/")) {
              final rel = path.split("/storage/emulated/0/").last;
              final encoded = Uri.encodeComponent(rel);
              uriStr = "content://com.android.externalstorage.documents/document/primary%3A$encoded";
            } else {
              uriStr = "content://media/external/images/media";
            }
            final Uri uri = Uri.parse(uriStr);
            bool launched = false;
            try {
              launched = await launchUrl(uri, mode: LaunchMode.externalNonBrowserApplication);
            } catch (_) {
              try {
                launched = await launchUrl(uri);
              } catch (_) {}
            }
            if (!launched) {
              final Uri mediaUri = Uri.parse("content://media/external/images/media");
              try {
                await launchUrl(mediaUri, mode: LaunchMode.externalNonBrowserApplication);
              } catch (_) {}
            }
            return {"status": "success"};
          } else if (Platform.isLinux) {
            await Process.run('xdg-open', [path]);
            return {"status": "success"};
          } else if (Platform.isWindows) {
            await Process.run('explorer.exe', [path]);
            return {"status": "success"};
          } else if (Platform.isMacOS) {
            await Process.run('open', [path]);
            return {"status": "success"};
          }
          return {"status": "unsupported"};

        default:
          throw Exception("Unknown share method: $name");
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return const SizedBox.shrink();
  }
}

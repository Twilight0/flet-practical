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
          if (path.isEmpty) return {"status": "error", "error": "empty path"};
          if (Platform.isAndroid) {
            // Android N+ StrictMode forbids file:// Intent.getData() -> FileUriExposedException
            // Use SAF content:// via DocumentsProvider instead of Uri.file
            bool ok = false;
            // Build SAF document URI: primary:Download/Warpinator
            String primaryPath = path;
            if (primaryPath.startsWith('/storage/emulated/0/')) {
              primaryPath = primaryPath.substring('/storage/emulated/0/'.length);
            } else if (primaryPath.startsWith('/sdcard/')) {
              primaryPath = primaryPath.substring('/sdcard/'.length);
            }
            primaryPath = primaryPath.replaceAll(RegExp(r'^/+'), '').replaceAll(RegExp(r'/+$'), '');
            // Try 1: SAF document URI for exact folder
            if (primaryPath.isNotEmpty) {
              final String encoded = Uri.encodeComponent('primary:$primaryPath');
              final Uri safUri = Uri.parse('content://com.android.externalstorage.documents/document/$encoded');
              try {
                if (await canLaunchUrl(safUri)) {
                  ok = await launchUrl(safUri, mode: LaunchMode.externalApplication);
                } else {
                  ok = await launchUrl(safUri, mode: LaunchMode.externalApplication);
                }
              } catch (_) {}
            }
            // Try 2: SAF tree URI
            if (!ok && primaryPath.isNotEmpty) {
              final String encodedTree = Uri.encodeComponent('primary:$primaryPath');
              final Uri treeUri = Uri.parse('content://com.android.externalstorage.documents/tree/$encodedTree/document/$encodedTree');
              try {
                ok = await launchUrl(treeUri, mode: LaunchMode.externalApplication);
              } catch (_) {}
            }
            // Fallback: generic SAF root (opens file manager)
            if (!ok) {
              final Uri fallback = Uri.parse('content://com.android.externalstorage.documents/root/primary');
              try {
                ok = await launchUrl(fallback, mode: LaunchMode.externalApplication);
              } catch (_) {}
            }
            return {"status": ok ? "success" : "no_handler"};
          } else if (Platform.isLinux) {
            try {
              await Process.run('xdg-open', [path]);
              return {"status": "success"};
            } catch (e) {
              return {"status": "error", "error": e.toString()};
            }
          } else if (Platform.isWindows) {
            try {
              await Process.run('explorer', [path]);
              return {"status": "success"};
            } catch (e) {
              return {"status": "error", "error": e.toString()};
            }
          } else if (Platform.isMacOS) {
            try {
              await Process.run('open', [path]);
              return {"status": "success"};
            } catch (e) {
              return {"status": "error", "error": e.toString()};
            }
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

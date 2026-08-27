import 'package:flutter/widgets.dart';
import 'package:flet/flet.dart';
import 'package:share_plus/share_plus.dart';

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

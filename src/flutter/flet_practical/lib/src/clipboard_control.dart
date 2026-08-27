import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/widgets.dart';
import 'package:flet/flet.dart';
import 'package:pasteboard/pasteboard.dart';

class PracticalClipboardControl extends StatefulWidget {
  final Control? parent;
  final Control control;

  const PracticalClipboardControl({
    super.key,
    required this.parent,
    required this.control,
  });

  @override
  State<PracticalClipboardControl> createState() => _PracticalClipboardControlState();
}

class _PracticalClipboardControlState extends State<PracticalClipboardControl> {
  @override
  void initState() {
    super.initState();
    _registerMethodHandlers();
  }

  void _registerMethodHandlers() {
    widget.control.addInvokeMethodListener((String name, dynamic args) async {
      switch (name) {
        case "get_text":
          return await Pasteboard.text;

        case "set_text":
          final text = args is Map ? (args["text"] as String? ?? "") : (args?.toString() ?? "");
          Pasteboard.writeText(text);
          return true;

        case "get_html":
          return await Pasteboard.html;

        case "set_html":
          final html = args is Map ? (args["html"] as String? ?? "") : (args?.toString() ?? "");
          final text = args is Map ? (args["text"] as String? ?? "") : "";
          // pasteboard 0.5.0 removed writeHtml; fallback to plain text
          Pasteboard.writeText(text.isNotEmpty ? text : html);
          return true;

        case "get_image":
          final Uint8List? imageBytes = await Pasteboard.image;
          if (imageBytes != null && imageBytes.isNotEmpty) {
            return base64Encode(imageBytes);
          }
          return null;

        case "set_image":
          if (args is Map && args["image_base64"] != null) {
            final String b64 = args["image_base64"] as String;
            final Uint8List bytes = base64Decode(b64);
            await Pasteboard.writeImage(bytes);
            return true;
          }
          return false;

        case "get_files":
          return await Pasteboard.files();

        case "set_files":
          if (args is Map && args["files"] is List) {
            final List<String> files = (args["files"] as List).map((e) => e.toString()).toList();
            await Pasteboard.writeFiles(files);
            return true;
          }
          return false;

        case "has_text":
          final String? text = await Pasteboard.text;
          return text != null && text.isNotEmpty;

        case "has_image":
          final Uint8List? img = await Pasteboard.image;
          return img != null && img.isNotEmpty;

        case "clear":
          Pasteboard.writeText("");
          return true;

        default:
          throw Exception("Unknown clipboard method: $name");
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return const SizedBox.shrink();
  }
}

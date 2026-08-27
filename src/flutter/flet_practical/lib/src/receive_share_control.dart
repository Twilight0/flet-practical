import 'dart:async';
import 'dart:convert';
import 'package:flutter/widgets.dart';
import 'package:flet/flet.dart';
import 'package:receive_sharing_intent/receive_sharing_intent.dart';

class PracticalReceiveShareControl extends StatefulWidget {
  final Control? parent;
  final Control control;

  const PracticalReceiveShareControl({
    super.key,
    required this.parent,
    required this.control,
  });

  @override
  State<PracticalReceiveShareControl> createState() =>
      _PracticalReceiveShareControlState();
}

class _PracticalReceiveShareControlState
    extends State<PracticalReceiveShareControl> {
  StreamSubscription<List<SharedMediaFile>>? _mediaSubscription;

  @override
  void initState() {
    super.initState();
    _initReceiveShare();
    _registerMethodHandlers();
  }

  Future<void> _initReceiveShare() async {
    try {
      final List<SharedMediaFile> initialMedia =
          await ReceiveSharingIntent.instance.getInitialMedia();
      if (initialMedia.isNotEmpty) {
        _emitShare(initialMedia);
        await ReceiveSharingIntent.instance.reset();
      }
    } catch (_) {}

    _mediaSubscription =
        ReceiveSharingIntent.instance.getMediaStream().listen(
      (List<SharedMediaFile> media) async {
        if (media.isNotEmpty) {
          _emitShare(media);
          await ReceiveSharingIntent.instance.reset();
        }
      },
      onError: (_) {},
    );
  }

  void _emitShare(List<SharedMediaFile> media) {
    final List<Map<String, dynamic>> payload =
        media.map((f) => f.toMap()).toList();
    widget.control.triggerEvent("share", jsonEncode(payload));
  }

  void _registerMethodHandlers() {
    widget.control.addInvokeMethodListener((String name, dynamic args) async {
      switch (name) {
        case "get_initial_share":
          final List<SharedMediaFile> media =
              await ReceiveSharingIntent.instance.getInitialMedia();
          return media.map((f) => f.toMap()).toList();

        case "reset":
          await ReceiveSharingIntent.instance.reset();
          return true;

        default:
          throw Exception("Unknown receive_share method: $name");
      }
    });
  }

  @override
  void dispose() {
    _mediaSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return const SizedBox.shrink();
  }
}

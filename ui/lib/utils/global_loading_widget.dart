import 'package:flutter/material.dart';

/// A top-level widget that can display a loading spinner on top of the entire app.
/// Access it using [GlobalLoadingWidget.show] or [GlobalLoadingWidget.hide].
class GlobalLoadingWidget extends StatefulWidget {
  // The child (usually your MaterialApp or main app widget)
  final Widget child;

  // A global key to access the state from anywhere
  static final GlobalKey<_GlobalLoadingWidgetState> globalKey =
  GlobalKey<_GlobalLoadingWidgetState>();

  GlobalLoadingWidget({Key? key, required this.child}) : super(key: globalKey);

  @override
  _GlobalLoadingWidgetState createState() => _GlobalLoadingWidgetState();

  /// Show the loading spinner
  static void show() {
    globalKey.currentState?._show();
  }

  /// Hide the loading spinner
  static void hide() {
    globalKey.currentState?._hide();
  }
}

class _GlobalLoadingWidgetState extends State<GlobalLoadingWidget> {
  bool _isLoading = false;

  void _show() {
    setState(() {
      _isLoading = true;
    });
  }

  void _hide() {
    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // The main app's content
        widget.child,

        // The loading Widget, visible if _isLoading == true
        if (_isLoading)
          Positioned.fill(
            child: Container(
              color: Colors.black54,
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
          ),
      ],
    );
  }
}

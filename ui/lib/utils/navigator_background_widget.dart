import 'dart:math';
import 'package:flutter/material.dart';
import '../auth_gate.dart';
import '../screens/chat_screen.dart';
import '../screens/custom_profile_screen.dart';
import '../screens/enter_details_screen.dart';
import '../screens/file_upload_screen.dart';


class NavigatorWithBackground extends StatefulWidget {
  const NavigatorWithBackground({Key? key}) : super(key: key);

  @override
  State<NavigatorWithBackground> createState() => _NavigatorWithBackgroundState();
}

class _NavigatorWithBackgroundState extends State<NavigatorWithBackground> {
  final GlobalKey<NavigatorState> _navigatorKey = GlobalKey<NavigatorState>();

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Container(
          color: Colors.green[100], //#Theme.of(context).colorScheme.onPrimary,
        ),
        // 1) The one background image (never changes)
        const BackgroundWidget(),

        // 2) The Navigator on top
        Navigator(
          key: _navigatorKey,
          initialRoute: '/',
          onGenerateRoute: (settings) {
            // Example route logic
            switch (settings.name) {
              case '/':
                return MaterialPageRoute(builder: (context) => const AuthGate());
              case '/file_upload':
                return MaterialPageRoute(builder: (context) => const DocumentUploadScreen());
              case '/profile':
                return MaterialPageRoute(builder: (context) => const CustomProfileScreen());
              case '/enter_details':
                return MaterialPageRoute(builder: (context) => const EnterDetailsScreen());
              case '/chat':
                return MaterialPageRoute(builder: (context) => const ChatScreen());
              default:
                return MaterialPageRoute(builder: (context) => const AuthGate());
            }
          },
        ),
      ],
    );
  }
}

class BackgroundWidget extends StatefulWidget {
  //final Widget child;

  const BackgroundWidget({
    Key? key,
  }) : super(key: key);

  @override
  _BackgroundWidgetState createState() => _BackgroundWidgetState();
}

class _BackgroundWidgetState extends State<BackgroundWidget> {
  final List<String> _backgrounds = [
    "assets/images/black_pattern_01.png",
    "assets/images/black_pattern_02.png",
  ];

  late String _selectedBackground;
  late Alignment _randomAlignment;

  @override
  void initState() {
    super.initState();

    // 1) Pick a random background from the list
    final random = Random();
    _selectedBackground = _backgrounds[random.nextInt(_backgrounds.length)];

    // 2) Choose a random alignment to display a subsection
    // Range -1.0 .. 1.0: negative aligns top/left, positive bottom/right
    double randomX = random.nextDouble() * 2 - 1; // -1 to 1
    double randomY = random.nextDouble() * 2 - 1; // -1 to 1
    _randomAlignment = Alignment(randomX, randomY);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      // The random subsection is determined by `fit: BoxFit.none`
      // plus the chosen random alignment.
      decoration: BoxDecoration(
        image: DecorationImage(
          image: AssetImage(_selectedBackground),
          opacity: .1,
          fit: BoxFit.none,       // Show the image at its native size
          alignment: _randomAlignment,
        ),
      ),
      //child: widget.child,
    );
  }
}
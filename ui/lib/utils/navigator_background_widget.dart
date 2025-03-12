
import 'package:flutter/material.dart';
import 'package:animations/animations.dart';
import 'package:puurlee/utils/assets.dart';

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

  PageRoute _buildSharedAxisRoute(Widget page) {
    return PageRouteBuilder(
      transitionDuration: const Duration(milliseconds: 300),
      reverseTransitionDuration: const Duration(milliseconds: 300),
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return SharedAxisTransition(
          animation: animation,
          secondaryAnimation: secondaryAnimation,
          transitionType: SharedAxisTransitionType.horizontal,
          child: child,
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        backgroundWidget,
        Navigator(
          key: _navigatorKey,
          initialRoute: '/',
          onGenerateRoute: (settings) {
            switch (settings.name) {
              case '/file_upload':
                return _buildSharedAxisRoute(const DocumentUploadScreen());
              case '/profile':
                return _buildSharedAxisRoute(const CustomProfileScreen());
              case '/enter_details':
                return _buildSharedAxisRoute(const EnterDetailsScreen());
              case '/chat':
                return _buildSharedAxisRoute(const ChatScreen());
              case '/':
              default:
                return _buildSharedAxisRoute(const AuthGate());
            }
          },
        ),
      ],
    );
  }
}

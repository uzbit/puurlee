import 'package:firebase_ui_auth/firebase_ui_auth.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../utils/global_loading_widget.dart';
import '../options.dart';

class CustomProfileScreen extends StatefulWidget {
  const CustomProfileScreen({super.key});

  @override
  _CustomProfileScreen createState() => _CustomProfileScreen();
}

class _CustomProfileScreen extends State<CustomProfileScreen> {
  static const String _clearUserDataUrl =
      'https://clear-user-data-286240844421.us-central1.run.app';
      //'http://127.0.0.1:8080';
  final user = FirebaseAuth.instance.currentUser;

  //Clear all user data.
  Future<bool> _clearUserData() async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse(_clearUserDataUrl));
      request.fields['user_id'] = user!.uid;
      request.fields['api_key'] = puurleeServerAPIKey;

      var response = await request.send();

      if (response.statusCode == 200) {
        print('Cleared user data successfully.');
        return true;
      } else {
        print('Clearing user data failed with status: ${response.statusCode}.');
        return false;
      }
    } catch (e) {
      print('An error occurred while uploading file: $e');
      return false;
    }
  }

  void _onClearDataPressed() async {
    GlobalLoadingWidget.show();

    final success = await _clearUserData();

    GlobalLoadingWidget.hide();

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('User data cleared successfully!')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to clear user data.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return ProfileScreen(
      // The actions property lets you add custom items
      // like sign-out or other settings
      actions: [
        SignedOutAction((context) {
          Navigator.of(context).pop(); // or some other flow
        }),
      ],

      // children allows you to insert extra widgets
      // into the bottom of the profile screen
      children: [
        // For example, an ElevatedButton that calls some custom function
        ElevatedButton(
          onPressed: () {
            _onClearDataPressed();
          },
          child: const Text('Clear all personal data.'),
        ),
      ],
    );
  }
}

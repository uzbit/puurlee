import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:auto_size_text/auto_size_text.dart';
import 'enter_details_screen.dart';
import 'chat_screen.dart';
import 'file_upload_screen.dart';
import 'custom_profile_screen.dart';
import '../utils/assets.dart';


class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final user = FirebaseAuth.instance.currentUser;

  @override
  Widget build(BuildContext context) {
    // If displayName is null, redirect to enter name screen
    if (user != null && user!.displayName == null) {
      return const EnterDetailsScreen();
    }

    return Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          //title: const Text('Puurlee'),
          actions: [
            IconButton(
              icon: const Icon(Icons.chat),
              onPressed: () {
                Navigator.of(context).pushNamed('/chat');
              },
            ),
            IconButton(
              icon: const Icon(Icons.person),
              onPressed: () {
                Navigator.of(context).pushNamed('/profile');
              },
            ),
          ],
          automaticallyImplyLeading: false,
      ),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        // Use a Column that fills the available space and
        // pin its children at the bottom.
        child: Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            // Group the logo, hi text, and bottom text together
            Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                puurleeLogo,
                AutoSizeText(
                  'Hi ${user?.displayName ?? "You"}!',
                  style: Theme.of(context).textTheme.displaySmall,
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  minFontSize: 12,
                  overflow: TextOverflow.ellipsis,
                ),
                const Text('Use the + button to upload documents.'),
              ],
            ),
            const SizedBox(height: 20), // Optional padding from the bottom
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        // Change to a plus icon
        onPressed: () {
          Navigator.of(context).pushNamed('/file_upload');
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}

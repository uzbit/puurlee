import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_ui_auth/firebase_ui_auth.dart';

import 'enter_name_screen.dart';
import 'chat_screen.dart';
import 'file_upload_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final user = FirebaseAuth.instance.currentUser;

  @override
  Widget build(BuildContext context) {
    // If displayName is null, redirect to enter name screen
    if (user != null && user!.displayName == null) {
      return EnterNameScreen();
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Puurlee'),
        actions: [
          IconButton(
            icon: const Icon(Icons.chat),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ChatScreen(),
                ),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute<ProfileScreen>(
                  builder: (context) => const ProfileScreen(),
                ),
              );
            },
          ),
        ],
        automaticallyImplyLeading: false,
      ),
      body: Center(
        child: SingleChildScrollView(
          // Display a welcome message, no file preview here anymore
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Image.asset('assets/images/puurlee_logo.png'),
              Text(
                'Welcome ${user?.displayName ?? "You"}!',
                style: Theme.of(context).textTheme.displaySmall,
              ),
              const SizedBox(height: 20),
              const Text('Use the + button to upload documents.'),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        // Change to a plus icon
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => const DocumentUploadScreen(),
            ),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}

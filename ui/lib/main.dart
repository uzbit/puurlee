import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:puurlee/utils/navigator_background_widget.dart';
import 'models/chat_message.dart';
import 'options.dart';
import 'utils/global_loading_widget.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:path_provider/path_provider.dart';

dynamic chatBox;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  if (!kIsWeb) {
    final appDocumentDir = await getApplicationDocumentsDirectory();
    await Hive.initFlutter(appDocumentDir.path);
  } else {
    await Hive.initFlutter();
  }

  Hive.registerAdapter(ChatMessageAdapter()); // Register adapter
  if (!Hive.isBoxOpen('chatBox')) {
    chatBox = await Hive.openBox<List>('chatBox'); // Open only if not already open
  }
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
          // 1) Use the builder callback
          builder: (BuildContext context, Widget? child) {
            // 2) Wrap the child in your GlobalLoadingWidget
            return GlobalLoadingWidget(child: child!);
          },
          //title: 'Puurlee',
          theme: ThemeData(
            colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
            useMaterial3: true,
          ),
          home: const NavigatorWithBackground()
    );
  }
}


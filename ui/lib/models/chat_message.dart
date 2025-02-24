import 'package:hive/hive.dart';
part 'chat_message.g.dart'; // Required for Hive to generate code

@HiveType(typeId: 0)
class ChatMessage {
  @HiveField(0)
  final String text;

  @HiveField(1)
  final bool isUser;

  ChatMessage({required this.text, required this.isUser});
}

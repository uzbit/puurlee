import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:hive/hive.dart';
import 'package:puurlee/main.dart';
import '../services/chat_service.dart';
import '../utils/utils.dart';
import '../models/chat_message.dart';


class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  List<ChatMessage> _messages = [];
  final TextEditingController _textController = TextEditingController();
  final user = FirebaseAuth.instance.currentUser;

  @override
  void initState() {
    super.initState();
    _loadChatHistory();
  }

  void _loadChatHistory() {
    var storedMessages = chatBox.get(user?.uid ?? 'default_user', defaultValue: <ChatMessage>[]);

    if (storedMessages is List<ChatMessage>) {
      setState(() {
        _messages.addAll(storedMessages);
      });
    } else if (storedMessages is List) {
      setState(() {
        _messages.addAll(storedMessages.cast<ChatMessage>());
      });
    }
  }

  /// **Store chat history in Hive**
  void _storeChatHistory() {
   chatBox.put(user!.uid, _messages);
  }

  /// **Send a message and update UI**
  void _handleSendMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    // User message
    ChatMessage userMessage = ChatMessage(text: text, isUser: true);
    setState(() {
      _messages.add(userMessage);
    });
    _storeChatHistory(); // Save message

    _textController.clear();

    // AI response
    final response = await ChatService.postQuery(query: text, userId: user?.uid ?? '');

    ChatMessage botMessage = ChatMessage(text: response, isUser: false);
    setState(() {
      _messages.add(botMessage);
    });

    _storeChatHistory(); // Save response
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Chat")),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                return Align(
                  alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    padding: EdgeInsets.all(10),
                    margin: EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                    decoration: BoxDecoration(
                      color: message.isUser ? Colors.blueAccent : Colors.grey[300],
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      message.text,
                      style: TextStyle(color: message.isUser ? Colors.white : Colors.black),
                    ),
                  ),
                );
              },
            ),
          ),
          _buildMessageInput(),
        ],
      ),
    );
  }

  /// **Message Input Field**
  Widget _buildMessageInput() {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _textController,
              decoration: const InputDecoration(
                hintText: "Type a message...",
                border: OutlineInputBorder(),
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.send),
            onPressed: _handleSendMessage,
          ),
        ],
      ),
    );
  }
}
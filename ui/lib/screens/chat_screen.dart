import 'package:flutter/material.dart';

// A basic message model
class ChatMessage {
  final String text;
  final bool isUser;

  ChatMessage({required this.text, required this.isUser});
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _messages = <ChatMessage>[];
  final _textController = TextEditingController();

  // Replace this with your AI call or backend integration
  Future<String> _getAIResponse(String userMessage) async {
    // Placeholder for AI logic.
    // E.g. call your backend endpoint or a local LLM.
    await Future.delayed(const Duration(seconds: 1));
    return "Echoing back: $userMessage";
  }

  void _handleSendMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    // Add user message to the list
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: true));
    });
    _textController.clear();

    // Get AI response
    final response = await _getAIResponse(text);

    // Add AI response to the list
    setState(() {
      _messages.add(ChatMessage(text: response, isUser: false));
    });
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Widget _buildMessageBubble(ChatMessage message) {
    // Align user messages to the right, AI messages to the left
    final alignment = message.isUser ? Alignment.centerRight : Alignment.centerLeft;
    final bubbleColor = message.isUser ? Colors.blue[100] : Colors.grey[200];
    final textColor = Colors.black;

    return Align(
      alignment: alignment,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 8.0),
        padding: const EdgeInsets.all(12.0),
        decoration: BoxDecoration(
          color: bubbleColor,
          borderRadius: BorderRadius.circular(8.0),
        ),
        child: Text(
          message.text,
          style: TextStyle(color: textColor),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("AI Chat"),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Display messages in a ListView
            Expanded(
              child: ListView.builder(
                reverse: false,      // or true if you want new messages from the bottom
                itemCount: _messages.length,
                itemBuilder: (context, index) {
                  final message = _messages[index];
                  return _buildMessageBubble(message);
                },
              ),
            ),
            // Text input area
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _handleSendMessage(),
                    decoration: const InputDecoration(
                      contentPadding: EdgeInsets.all(12.0),
                      hintText: "Ask puurlee...",
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _handleSendMessage,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

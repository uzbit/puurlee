import 'dart:convert';
import 'package:http/http.dart' as http;

import '../main.dart';
import '../models/chat_message.dart';

const String chatHistoryUrl = "https://your-cloud-function-url/chat-history";

Future<List<ChatMessage>> fetchChatHistoryFromServer(String userId) async {
  try {
    var response = await http.get(Uri.parse('$chatHistoryUrl?user_id=$userId'));

    if (response.statusCode == 200) {
      List<dynamic> chatData = json.decode(response.body);

      // Store in local cache
      chatBox.put('messages', chatData);

      return List<ChatMessage>.from(chatData);
    } else {
      print("Failed to fetch chat history: ${response.statusCode}");
      return [];
    }
  } catch (e) {
    print("Error fetching chat history: $e");
    return [];
  }
}

Future<List<ChatMessage>> loadCachedChatHistory() async {
  var rawMessages = chatBox.get('messages', defaultValue: <ChatMessage>[]);

  // Explicitly cast the dynamic list to a List<ChatMessage>
  if (rawMessages is List<ChatMessage>) {
    return rawMessages;
  } else if (rawMessages is List) {
    return rawMessages.cast<ChatMessage>();
  } else {
    return [];
  }
}

Future<List<ChatMessage>> loadChatHistory(String userId) async {
  List<ChatMessage> cachedChats = await loadCachedChatHistory();

  // Fetch new data and merge with cached chats
  //List<ChatMessage> serverChats = await fetchChatHistoryFromServer(userId);

  // If server returns new messages, update cache
  // if (serverChats.isNotEmpty) {
  //   return serverChats;
  // }

  // Otherwise, return cached history
  return cachedChats;
}
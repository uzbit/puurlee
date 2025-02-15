import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:mime/mime.dart';
import '../utils/global_loading_widget.dart';
import '../options.dart';

class ChatService {
  static const String _chatUrl =
      'https://chat-286240844421.us-central1.run.app';
  // static const String _uploadUrl = 'http://127.0.0.1:8080';

  static Future<String> postQuery({
    required String query,
    required String userId,
  }) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse(_chatUrl));

      request.fields['query'] = query;
      request.fields['user_id'] = userId;
      request.fields['api_key'] = puurleeServerAPIKey;

      var response = await request.send();
      String responseBody = await response.stream.bytesToString(); // Corrected extraction

      if (response.statusCode == 200) {
        print("Chatbot Answer: $responseBody");
        return responseBody;
      } else {
        print('Chatbot query failed with status: ${response.statusCode}. Response: $responseBody');
        return "Error: Failed to get response";
      }
    } catch (e) {
      print('An error occurred while requesting chatbot response: $e');
      return "Error: Something went wrong";
    }
  }
}

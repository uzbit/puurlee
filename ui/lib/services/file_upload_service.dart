import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:mime/mime.dart';

class FileUploadService {
  static const String _uploadUrl =
      'https://us-central1-puurlee.cloudfunctions.net/file_to_nosql';
  // static const String _uploadUrl = 'http://127.0.0.1:8080';

  static Future<void> postFileToDB({
    required Uint8List fileBytes,
    required String fileName,
    required String userId,
  }) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse(_uploadUrl));

      // Determine the MIME type from the fileName
      String? mimeType = lookupMimeType(fileName);

      if (mimeType == null) {
        print('Could not determine MIME type of the file.');
        return;
      }

      final mimeTypeData = mimeType.split('/');

      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          fileBytes,
          filename: fileName,
          contentType: MediaType(mimeTypeData[0], mimeTypeData[1]),
        ),
      );

      request.fields['user_id'] = userId;

      var response = await request.send();

      if (response.statusCode == 200) {
        print('File uploaded successfully.');
      } else {
        print('File upload failed with status: ${response.statusCode}.');
      }
    } catch (e) {
      print('An error occurred while uploading file: $e');
    }
  }
}

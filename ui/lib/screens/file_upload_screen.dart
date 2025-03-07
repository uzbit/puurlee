import 'dart:io';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

import '../services/file_upload_service.dart';
import '../utils/pdf_preview_widget.dart';

class DocumentUploadScreen extends StatefulWidget {
  const DocumentUploadScreen({super.key});

  @override
  _DocumentUploadScreenState createState() => _DocumentUploadScreenState();
}

class _DocumentUploadScreenState extends State<DocumentUploadScreen> {
  Uint8List? _fileBytes;
  String? _fileName;
  String? _filePath;
  final int _maxFileSizeMB = 1;

  final user = FirebaseAuth.instance.currentUser;

  // 1. Helper method to pick a file (camera or file picker depending on platform)
  Future<void> _pickFile() async {
    _fileBytes = null;
    _fileName = null;

    try {
        //Use FilePicker
        final allowedExtensions = ['jpg', 'jpeg', 'png', 'pdf'];
        FilePickerResult? result = await FilePicker.platform.pickFiles(
          type: FileType.custom,
          allowedExtensions: allowedExtensions,
            withData: true,
        );

        if (result != null) {
          _fileBytes = result.files.first.bytes;
          _fileName = result.files.first.name;
          _filePath = result.files.first.path;
        }
        print("$_filePath, ${_fileBytes?.length}, $user, ${user?.uid}");

        setState(() {});
    } catch (e) {
      print('Error picking file: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error picking file: $e')),
      );
    }
  }

  // 2. Upload the file to your backend
  Future<bool> _uploadFile() async {
    if (_fileBytes == null || _fileName == null) {
      print('No file to upload.');
      return false;
    }

    int maxFileSize = _maxFileSizeMB * 1024 * 1024; // 1MB
    if (_fileBytes!.length > maxFileSize){
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('This file is too large, please choose one less than ${_maxFileSizeMB}MB.')),
      );
      return false;
    }

    try {
      await FileUploadService.postFileToDB(
        fileBytes: _fileBytes!,
        fileName: _fileName!,
        userId: user?.uid ?? '',
      );
      return true; // Indicate success
    } catch (e) {
      print('Error uploading file: $e');
      return false; // Indicate failure
    }
  }

  @override
  Widget build(BuildContext context) {
    // Display an image preview if we have image data,
    // or show a small note for other file types (like PDF).
    Widget previewWidget;
    if (_fileBytes != null && _fileName != null) {
      if (_fileName!.toLowerCase().endsWith('.png') ||
          _fileName!.toLowerCase().endsWith('.jpg') ||
          _fileName!.toLowerCase().endsWith('.jpeg')) {
        // Show image preview
        previewWidget = Image.file(File(_filePath!));
      } else if (_fileName!.toLowerCase().endsWith('.pdf')) {
        // Use a PDF viewer
        final pdfData = Uint8List.fromList(_fileBytes!);
        previewWidget = SizedBox(
          height: 400,
          child: PdfPreviewWidget(pdfData: pdfData),
        );
      } else {
        // If it’s not an image, just show a generic label
        previewWidget = Text('Selected file: $_fileName is not valid! Must be an image or a PDF.');
      }
    } else {
      previewWidget = const Text('No file selected.');
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Document Upload'),
      ),
      body: SingleChildScrollView(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                previewWidget,
                const SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: _pickFile,
                  icon: const Icon(Icons.file_upload),
                  label: const Text('Choose Health Document'),
                ),
                const SizedBox(height: 10),
                ElevatedButton(
                  onPressed: () async {
                    // Call the upload function, which returns a success/failure boolean
                    final success = await _uploadFile();

                    if (success) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('File uploaded successfully.'),
                        ),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Error uploading file.'),
                        ),
                      );
                    }
                  },
                  child: const Text('Upload File'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

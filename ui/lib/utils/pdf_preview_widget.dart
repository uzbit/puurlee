import 'package:flutter/material.dart';
import 'package:pdfx/pdfx.dart';
import 'dart:typed_data';

class PdfPreviewWidget extends StatelessWidget {
  final Uint8List pdfData;

  const PdfPreviewWidget({super.key, required this.pdfData});

  @override
  Widget build(BuildContext context) {
    // Create a PdfController for in-memory data
    final pdfController = PdfController(
      document: PdfDocument.openData(pdfData),
    );

    return PdfView(
      controller: pdfController,
    );
  }
}
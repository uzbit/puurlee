import 'dart:math';
import 'package:flutter/material.dart';

Padding puurleeLogo = Padding(
  padding: const EdgeInsets.all(20),
  child: AspectRatio(
    aspectRatio: 1,
    child: Image.asset('assets/images/puurlee_logo.png'),
  ),
);


class BackgroundImage {
  final List<String> _backgrounds = [
    "assets/images/black_pattern_01.png",
    "assets/images/black_pattern_02.png",
  ];

  late String _selectedBackground;
  late Alignment _randomAlignment;
  late BoxDecoration image;

  BackgroundImage() {
    final random = Random();
    _selectedBackground = _backgrounds[random.nextInt(_backgrounds.length)];

    // Random alignment for a subsection of the image.
    double randomX = random.nextDouble() * 2 - 1;
    double randomY = random.nextDouble() * 2 - 1;
    _randomAlignment = Alignment(randomX, randomY);
    image = BoxDecoration(
      image: DecorationImage(
        image: AssetImage(_selectedBackground),
        opacity: .1,
        fit: BoxFit.none,
        alignment: _randomAlignment,
      ),
    );
  }
}

var backgroundImage = BackgroundImage();

import 'dart:math';
import 'package:flutter/material.dart';

Padding puurleeLogo = Padding(
  padding: const EdgeInsets.all(20),
  child: AspectRatio(
    aspectRatio: 1,
    child: Image.asset('assets/images/puurlee_logo.png'),
  ),
);


class BackgroundWidget extends StatefulWidget {
  const BackgroundWidget({Key? key}) : super(key: key);

  @override
  _BackgroundWidgetState createState() => _BackgroundWidgetState();
}

class _BackgroundWidgetState extends State<BackgroundWidget> {
  final List<String> _backgrounds = [
    "assets/images/black_pattern_01.png",
    "assets/images/black_pattern_02.png",
  ];

  late String _selectedBackground;
  late Alignment _randomAlignment;

  @override
  void initState() {
    super.initState();
    final random = Random();
    _selectedBackground = _backgrounds[random.nextInt(_backgrounds.length)];

    // Random alignment for a subsection of the image.
    double randomX = random.nextDouble() * 2 - 1;
    double randomY = random.nextDouble() * 2 - 1;
    _randomAlignment = Alignment(randomX, randomY);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        image: DecorationImage(
          image: AssetImage(_selectedBackground),
          opacity: .1,
          fit: BoxFit.none,
          alignment: _randomAlignment,
        ),
      ),
    );
  }
}

const Widget backgroundWidget = BackgroundWidget();

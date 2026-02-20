import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const BlinkApp());
}

class BlinkApp extends StatelessWidget {
  const BlinkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Blink Quick Commerce',
      theme: ThemeData(primarySwatch: Colors.green),
      home: const LoginScreen(),
    );
  }
}

import 'package:flutter/material.dart';
import '../api_client.dart';

class OrderTrackingScreen extends StatefulWidget {
  final String orderId;
  const OrderTrackingScreen({super.key, required this.orderId});

  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen> {
  String status = 'Loading...';

  @override
  void initState() {
    super.initState();
    loadStatus();
  }

  Future<void> loadStatus() async {
    final data = await ApiClient.trackOrder(widget.orderId);
    setState(() => status = data['current_status']);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Order Tracking')),
      body: Center(child: Text('Current status: $status', style: const TextStyle(fontSize: 20))),
      floatingActionButton: FloatingActionButton(onPressed: loadStatus, child: const Icon(Icons.refresh)),
    );
  }
}

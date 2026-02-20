import 'package:flutter/material.dart';
import 'order_tracking_screen.dart';

class OrderConfirmationScreen extends StatelessWidget {
  final String token;
  final Map<String, dynamic> order;
  const OrderConfirmationScreen({super.key, required this.token, required this.order});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Order Confirmation')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Order ID: ${order['order_id']}'),
          Text('Total: ₹${order['total_amount']}'),
          Text('Reference: ${order['order_reference_id']}'),
          const SizedBox(height: 12),
          ElevatedButton(
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => OrderTrackingScreen(orderId: order['order_id'])),
            ),
            child: const Text('Track order'),
          )
        ]),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import '../api_client.dart';
import 'order_confirmation_screen.dart';

class CartScreen extends StatefulWidget {
  final String token;
  const CartScreen({super.key, required this.token});

  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  List<dynamic> items = [];

  @override
  void initState() {
    super.initState();
    loadCart();
  }

  Future<void> loadCart() async {
    final data = await ApiClient.getCart(widget.token);
    setState(() => items = data['items']);
  }

  Future<void> checkout() async {
    final order = await ApiClient.createOrder(widget.token);
    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => OrderConfirmationScreen(token: widget.token, order: order)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cart')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          Expanded(
            child: ListView(
              children: items
                  .map((i) => ListTile(
                        title: Text(i['product_id']),
                        subtitle: Text('Qty: ${i['quantity']}'),
                      ))
                  .toList(),
            ),
          ),
          ElevatedButton(onPressed: items.isEmpty ? null : checkout, child: const Text('Create order'))
        ]),
      ),
    );
  }
}

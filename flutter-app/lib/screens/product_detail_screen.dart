import 'package:flutter/material.dart';
import '../api_client.dart';

class ProductDetailScreen extends StatefulWidget {
  final String token;
  final String productId;
  const ProductDetailScreen({super.key, required this.token, required this.productId});

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  Map<String, dynamic>? product;
  String? message;

  @override
  void initState() {
    super.initState();
    loadProduct();
  }

  Future<void> loadProduct() async {
    final p = await ApiClient.getProduct(widget.productId);
    setState(() => product = p);
  }

  Future<void> addToCart() async {
    try {
      await ApiClient.addCart(widget.token, widget.productId);
      setState(() => message = 'Added to cart');
    } catch (e) {
      setState(() => message = 'Failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (product == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return Scaffold(
      appBar: AppBar(title: Text(product!['name'])),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(product!['description']),
          const SizedBox(height: 8),
          Text('Price: ₹${product!['price']}'),
          const SizedBox(height: 12),
          ElevatedButton(onPressed: addToCart, child: const Text('Add to cart')),
          if (message != null) Text(message!),
        ]),
      ),
    );
  }
}

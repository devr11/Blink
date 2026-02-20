import 'package:flutter/material.dart';
import '../api_client.dart';
import 'product_detail_screen.dart';
import 'cart_screen.dart';

class HomeScreen extends StatefulWidget {
  final String token;
  const HomeScreen({super.key, required this.token});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> categories = [];
  List<dynamic> products = [];

  @override
  void initState() {
    super.initState();
    loadData();
  }

  Future<void> loadData() async {
    final c = await ApiClient.categories();
    final p = await ApiClient.products();
    setState(() {
      categories = c;
      products = p;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Blink Home'),
        actions: [
          IconButton(
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => CartScreen(token: widget.token))),
              icon: const Icon(Icons.shopping_cart))
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          const Text('Categories', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          Wrap(spacing: 8, children: categories.map((c) => Chip(label: Text(c.toString()))).toList()),
          const SizedBox(height: 16),
          const Text('Products', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ...products.map((p) => Card(
                child: ListTile(
                  title: Text(p['name']),
                  subtitle: Text('₹${p['price']}'),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => ProductDetailScreen(token: widget.token, productId: p['product_id']),
                    ),
                  ),
                ),
              )),
        ],
      ),
    );
  }
}

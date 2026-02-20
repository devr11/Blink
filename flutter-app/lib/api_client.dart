import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  static const userBase = 'http://localhost:8001';
  static const productBase = 'http://localhost:8002';
  static const cartBase = 'http://localhost:8003';
  static const deliveryBase = 'http://localhost:8004';

  static Future<Map<String, dynamic>> signup(
      String name, String email, String password) async {
    final response = await http.post(Uri.parse('$userBase/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'name': name, 'email': email, 'password': password}));
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body);
  }

  static Future<String> login(String email, String password) async {
    final response = await http.post(Uri.parse('$userBase/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}));
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body)['access_token'];
  }

  static Future<List<dynamic>> products() async {
    final response = await http.get(Uri.parse('$productBase/products'));
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body)['products'];
  }

  static Future<List<dynamic>> categories() async {
    final response = await http.get(Uri.parse('$productBase/categories'));
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body)['categories'];
  }

  static Future<Map<String, dynamic>> getProduct(String id) async {
    final response = await http.get(Uri.parse('$productBase/products/$id'));
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body);
  }

  static Future<void> addCart(String token, String productId) async {
    final response = await http.post(Uri.parse('$cartBase/cart/add'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode({'product_id': productId, 'quantity': 1}));
    if (response.statusCode >= 400) throw Exception(response.body);
  }

  static Future<Map<String, dynamic>> getCart(String token) async {
    final response = await http.get(Uri.parse('$cartBase/cart'),
        headers: {'Authorization': 'Bearer $token'});
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body);
  }

  static Future<Map<String, dynamic>> createOrder(String token) async {
    final response = await http.post(Uri.parse('$cartBase/order/create'),
        headers: {'Authorization': 'Bearer $token'});
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body)['order'];
  }

  static Future<Map<String, dynamic>> trackOrder(String orderId) async {
    final response =
        await http.get(Uri.parse('$deliveryBase/order/$orderId/status'));
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body);
  }
}

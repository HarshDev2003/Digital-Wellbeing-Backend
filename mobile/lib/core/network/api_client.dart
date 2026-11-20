import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiException implements Exception {
  final int statusCode;
  final String code;
  final String message;
  final dynamic details;

  ApiException({
    required this.statusCode,
    required this.code,
    required this.message,
    this.details,
  });

  @override
  String toString() => 'ApiException($statusCode, $code): $message';
}

class ApiClient {
  final String baseUrl;
  final http.Client _client;
  String? _authToken;

  ApiClient({
    required this.baseUrl,
    http.Client? client,
  }) : _client = client ?? http.Client();

  void setAuthToken(String? token) {
    _authToken = token;
  }

  String? get authToken => _authToken;

  Map<String, String> _buildHeaders([Map<String, String>? extraHeaders]) {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    if (extraHeaders != null) {
      headers.addAll(extraHeaders);
    }
    return headers;
  }

  Future<dynamic> get(String path, {Map<String, String>? headers, int retries = 2}) async {
    return _sendWithRetry(
      () => _client.get(Uri.parse('$baseUrl$path'), headers: _buildHeaders(headers)),
      retries: retries,
    );
  }

  Future<dynamic> post(String path, {dynamic body, Map<String, String>? headers, int retries = 2}) async {
    final encodedBody = body != null ? jsonEncode(body) : null;
    return _sendWithRetry(
      () => _client.post(Uri.parse('$baseUrl$path'), headers: _buildHeaders(headers), body: encodedBody),
      retries: retries,
    );
  }

  Future<dynamic> put(String path, {dynamic body, Map<String, String>? headers, int retries = 2}) async {
    final encodedBody = body != null ? jsonEncode(body) : null;
    return _sendWithRetry(
      () => _client.put(Uri.parse('$baseUrl$path'), headers: _buildHeaders(headers), body: encodedBody),
      retries: retries,
    );
  }

  Future<dynamic> delete(String path, {Map<String, String>? headers, int retries = 2}) async {
    return _sendWithRetry(
      () => _client.delete(Uri.parse('$baseUrl$path'), headers: _buildHeaders(headers)),
      retries: retries,
    );
  }

  Future<dynamic> _sendWithRetry(Future<http.Response> Function() requestFn, {int retries = 2}) async {
    int attempts = 0;
    while (true) {
      attempts++;
      try {
        final response = await requestFn();
        return _handleResponse(response);
      } on SocketException catch (_) {
        if (attempts > retries) {
          throw ApiException(
            statusCode: 0,
            code: 'NETWORK_ERROR',
            message: 'Unable to reach the server. Please verify your connection.',
          );
        }
        await Future.delayed(Duration(milliseconds: 500 * attempts));
      } on TimeoutException catch (_) {
        if (attempts > retries) {
          throw ApiException(
            statusCode: 408,
            code: 'TIMEOUT',
            message: 'Request timed out after multiple attempts.',
          );
        }
        await Future.delayed(Duration(milliseconds: 500 * attempts));
      }
    }
  }

  dynamic _handleResponse(http.Response response) {
    dynamic decoded;
    try {
      decoded = response.body.isNotEmpty ? jsonDecode(response.body) : null;
    } catch (_) {
      decoded = null;
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded;
    }

    if (decoded is Map<String, dynamic> && decoded.containsKey('error')) {
      final err = decoded['error'];
      throw ApiException(
        statusCode: response.statusCode,
        code: err['code']?.toString() ?? 'ERROR',
        message: err['message']?.toString() ?? 'An error occurred',
        details: err['details'],
      );
    }

    throw ApiException(
      statusCode: response.statusCode,
      code: 'HTTP_${response.statusCode}',
      message: response.body.isNotEmpty ? response.body : 'Request failed with status ${response.statusCode}',
    );
  }

  void close() {
    _client.close();
  }
}

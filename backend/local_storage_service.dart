import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

/// CAREPILL LOCAL OFFLINE PERSISTENCE ENGINE
/// Ensures seniors can view schedules, receive alarms, and track doses
/// offline when internet connectivity is lost, with auto-sync upon reconnection.

class LocalStorageService {
  static const String _keyPatientsData = 'carepill_multiuser_data';
  static const String _keyOfflineDoseQueue = 'carepill_offline_dose_queue';

  /// Save complete multi-patient state locally
  static Future<void> saveLocalState(Map<String, dynamic> stateData) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = jsonEncode(stateData);
    await prefs.setString(_keyPatientsData, jsonStr);
  }

  /// Load cached multi-patient state when offline
  static Future<Map<String, dynamic>?> loadLocalState() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString(_keyPatientsData);
    if (jsonStr == null || jsonStr.isEmpty) return null;

    try {
      return jsonDecode(jsonStr) as Map<String, dynamic>;
    } catch (e) {
      print('[LocalStorage Exception]: $e');
      return null;
    }
  }

  /// Queue an offline dose action for cloud synchronization when reconnected
  static Future<void> queueOfflineDoseAction(Map<String, dynamic> actionData) async {
    final prefs = await SharedPreferences.getInstance();
    List<String> queue = prefs.getStringList(_keyOfflineDoseQueue) ?? [];
    queue.add(jsonEncode(actionData));
    await prefs.setStringList(_keyOfflineDoseQueue, queue);
    print('[Offline Queue]: Dose action cached locally.');
  }

  /// Sync queued offline actions to Cloud Firestore when internet is restored
  static Future<List<Map<String, dynamic>>> getAndClearOfflineQueue() async {
    final prefs = await SharedPreferences.getInstance();
    List<String> queue = prefs.getStringList(_keyOfflineDoseQueue) ?? [];
    await prefs.remove(_keyOfflineDoseQueue);

    return queue.map((str) => jsonDecode(str) as Map<String, dynamic>).toList();
  }
}

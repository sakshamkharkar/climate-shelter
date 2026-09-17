import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

/// CAREPILL NOTIFICATION & ALARM SCHEDULER SERVICE
/// Handles offline local alarms, sound chimes, and FCM background push notifications.

class NotificationService {
  static final FlutterLocalNotificationsPlugin _notificationsPlugin =
      FlutterLocalNotificationsPlugin();
  static final FirebaseMessaging _messaging = FirebaseMessaging.instance;

  /// Initialize Local Alarms and Firebase Push Notifications
  static Future<void> initialize() async {
    // 1. Android & iOS Initialization Settings
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings();
    const settings = InitializationSettings(android: androidSettings, iOS: iosSettings);

    await _notificationsPlugin.initialize(
      settings,
      onDidReceiveNotificationResponse: (response) {
        print('[Notification Clicked] Payload: ${response.payload}');
      },
    );

    // 2. Request FCM Push Permissions
    NotificationSettings fcmSettings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    print('[FCM Authorization Status]: ${fcmSettings.authorizationStatus}');

    // 3. Foreground Push Handler
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('[Foreground FCM Message]: ${message.notification?.title}');
      if (message.notification != null) {
        triggerLocalAlarmChime(
          id: message.hashCode,
          title: message.notification!.title ?? 'Medication Alert',
          body: message.notification!.body ?? 'Time to take scheduled dose',
        );
      }
    });
  }

  /// Sound local high-priority audio chime alarm
  static Future<void> triggerLocalAlarmChime({
    required int id,
    required String title,
    required String body,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      'carepill_alarm_channel',
      'Medication Alarms',
      channelDescription: 'High-priority automatic time-matching medication alarms',
      importance: Importance.max,
      priority: Priority.high,
      playSound: true,
      sound: RawResourceAndroidNotificationSound('alarm_chime'),
      fullScreenIntent: true,
    );

    const iosDetails = DarwinNotificationDetails(
      presentSound: true,
      sound: 'alarm_chime.caf',
    );

    const notificationDetails = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notificationsPlugin.show(id, title, body, notificationDetails);
  }
}

import 'package:cloud_firestore/cloud_firestore.dart';

/// CAREPILL FLUTTER FIRESTORE DATABASE SERVICE
/// Provides real-time reactive streams, multi-patient CRUD operations,
/// and automated adherence calculations.

class DatabaseService {
  final FirebaseFirestore _db = FirebaseFirestore.instance;

  // ----------------------------------------------------
  // PATIENT PROFILES (MULTI-TENANT ROSTER)
  // ----------------------------------------------------

  /// Real-time stream of all patient profiles in the facility
  Stream<List<Map<String, dynamic>>> getPatientsStream() {
    return _db.collection('patients').snapshots().map((snapshot) {
      return snapshot.docs.map((doc) {
        final data = doc.data();
        data['id'] = doc.id;
        return data;
      }).toList();
    });
  }

  /// Register a brand new patient profile
  Future<String> createPatientProfile({
    required String patientName,
    required String category,
    required String docName,
    required String docPhone,
    required String docEmail,
    required String cgName,
    required String cgPhone,
    required String cgEmail,
  }) async {
    final docRef = await _db.collection('patients').add({
      'patientName': patientName,
      'category': category,
      'totalTaken': 0,
      'totalSkipped': 0,
      'totalMissed': 0,
      'adherencePercentage': 100,
      'contacts': {
        'docName': docName,
        'docSpecialty': 'Attending Physician',
        'docPhone': docPhone,
        'docEmail': docEmail,
        'cgName': cgName,
        'cgPhone': cgPhone,
        'cgEmail': cgEmail,
      },
      'createdAt': FieldValue.serverTimestamp(),
    });

    // Add initial activity log
    await docRef.collection('activityLogs').add({
      'text': '🎉 Patient profile created for $patientName ($category)',
      'timestamp': FieldValue.serverTimestamp(),
    });

    return docRef.id;
  }

  // ----------------------------------------------------
  // MEDICINE SCHEDULE CRUD
  // ----------------------------------------------------

  /// Real-time stream of medicines for a specific active patient
  Stream<List<Map<String, dynamic>>> getPatientMedicinesStream(String patientId) {
    return _db
        .collection('patients')
        .doc(patientId)
        .collection('medicines')
        .orderBy('time')
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        final data = doc.data();
        data['id'] = doc.id;
        return data;
      }).toList();
    });
  }

  /// Add a new medication to a patient's schedule
  Future<void> addMedicine({
    required String patientId,
    required String name,
    required String dosage,
    required String form,
    required String time,
    required String instructions,
    required int stock,
  }) async {
    final patientRef = _db.collection('patients').doc(patientId);

    final medRef = await patientRef.collection('medicines').add({
      'name': name,
      'dosage': dosage,
      'form': form,
      'time': time,
      'instructions': instructions,
      'stock': stock,
      'status': 'PENDING',
      'createdAt': FieldValue.serverTimestamp(),
    });

    await patientRef.collection('activityLogs').add({
      'text': '➕ Added new medication "$name ($dosage)" scheduled for $time',
      'timestamp': FieldValue.serverTimestamp(),
    });
  }

  /// Mark a dose as TAKEN or SKIPPED
  Future<void> markDoseStatus({
    required String patientId,
    required String medicineId,
    required String medicineName,
    required String dosage,
    required String time,
    required String status, // 'TAKEN' or 'SKIPPED'
  }) async {
    final patientRef = _db.collection('patients').doc(patientId);
    final medRef = patientRef.collection('medicines').doc(medicineId);

    // Batch write to update med status, decrease stock, and log dose audit
    final batch = _db.batch();

    batch.update(medRef, {
      'status': status,
      'lastTakenTime': FieldValue.serverTimestamp(),
    });

    if (status == 'TAKEN') {
      batch.update(medRef, {'stock': FieldValue.increment(-1)});
    }

    // Add to Dose Audit Logs (Triggers Cloud Function for Adherence & Alerts)
    final logRef = patientRef.collection('doseLogs').doc();
    batch.set(logRef, {
      'medicineId': medicineId,
      'medicineName': medicineName,
      'dosage': dosage,
      'scheduledTime': time,
      'status': status,
      'timestamp': FieldValue.serverTimestamp(),
    });

    final actionText = status == 'TAKEN'
        ? '✅ Patient TOOK $medicineName ($dosage) on schedule'
        : '🚨 Patient SKIPPED $medicineName ($dosage) - Caregiver Alert Dispatched';

    final activityRef = patientRef.collection('activityLogs').doc();
    batch.set(activityRef, {
      'text': actionText,
      'timestamp': FieldValue.serverTimestamp(),
    });

    await batch.commit();
  }

  // ----------------------------------------------------
  // REALTIME AUDIT & MESSAGE LOGS STREAM
  // ----------------------------------------------------

  /// Stream live activity logs for a patient
  Stream<List<Map<String, dynamic>>> getActivityLogsStream(String patientId) {
    return _db
        .collection('patients')
        .doc(patientId)
        .collection('activityLogs')
        .orderBy('timestamp', descending: true)
        .limit(30)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) => doc.data()).toList();
    });
  }
}

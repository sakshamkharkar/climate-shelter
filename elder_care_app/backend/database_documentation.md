# CarePill Elder Care System - Database Schema & Storage Architecture

This document describes the complete multi-tenant Cloud Firestore database schema, Storage rules, and Local Offline Persistence engine for the CarePill Medication Management application.

---

## 🗄️ 1. Cloud Firestore Database Schema

### `patients/{patientId}` (Collection: Patient Master Profiles)
| Field | Type | Description |
| :--- | :--- | :--- |
| `patientName` | `String` | Full name of the patient (e.g. Eleanor Vance, Robert Chen) |
| `category` | `String` | Medical care category (e.g. Cardiology Care, Diabetes Care) |
| `totalTaken` | `Number` | Total count of doses taken on time |
| `totalSkipped` | `Number` | Total count of doses explicitly skipped |
| `totalMissed` | `Number` | Total count of unconsumed missed doses |
| `adherencePercentage` | `Number` | Calculated dynamically: `(totalTaken / (totalTaken + totalSkipped + totalMissed)) * 100` |
| `contacts` | `Map` | Contains `docName`, `docPhone`, `docEmail`, `cgName`, `cgPhone`, `cgEmail` |
| `patientFcmToken` | `String` | FCM Push Token for sounding senior phone alarms |
| `caregiverFcmToken` | `String` | FCM Push Token for nurse/caregiver mobile push alerts |
| `createdAt` | `Timestamp` | Profile creation date |

---

### `patients/{patientId}/medicines/{medicineId}` (Subcollection: Scheduled Medicines)
| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | `String` | Name of medication (e.g. Lisinopril, Metformin, Insulin Glargine) |
| `dosage` | `String` | Dose quantity (e.g. 10mg • 1 Pill, 10 Units) |
| `form` | `String` | Medication form (Pill 💊, Syrup 🧪, Injection 💉) |
| `time` | `String` | Scheduled time formatted (e.g. 08:00 AM, 12:30 PM) |
| `instructions` | `String` | Instructions for senior (e.g. Take after breakfast with water) |
| `stock` | `Number` | Remaining pill stock count (decrements automatically when taken) |
| `status` | `String` | `PENDING`, `TAKEN`, or `SKIPPED` |

---

### `patients/{patientId}/doseLogs/{logId}` (Subcollection: Dose Event Audit Trail)
| Field | Type | Description |
| :--- | :--- | :--- |
| `medicineId` | `String` | Reference ID of the medication |
| `medicineName` | `String` | Name of medication |
| `dosage` | `String` | Dose quantity |
| `scheduledTime` | `String` | Time dose was due |
| `status` | `String` | `TAKEN`, `SKIPPED`, or `MISSED` |
| `timestamp` | `Timestamp` | Exact timestamp dose status was logged |

*Triggers Node.js Cloud Function `onDoseStatusChanged` to recalculate adherence and dispatch Twilio SMS + SendGrid Email alerts if `SKIPPED` or `MISSED`.*

---

### `patients/{patientId}/activityLogs/{activityId}` (Subcollection: Live Activity & Message Telemetry)
| Field | Type | Description |
| :--- | :--- | :--- |
| `text` | `String` | Human-readable activity text (e.g. "✅ Eleanor took Lisinopril", "📲 SMS sent to Nurse Mary") |
| `timestamp` | `Timestamp` | Broadcast timestamp synced live to all devices via `BroadcastChannel` & Firestore `snapshots()` |

---

## 🔒 2. Firebase Storage Rules & Buckets

* **Bucket Path**: `gs://carepill-health.appspot.com/patients/{patientId}/`
* **Allowed File Types**: Profile images (`image/*`) and prescription PDFs (`application/pdf`).
* **Maximum File Size**: 10MB per upload.
* **Access Rules**: Protected by Firebase Auth tokens (`request.auth != null`).

---

## 💾 3. Local Offline Persistence Engine

* **Storage Key**: `carepill_multiuser_data`
* **Offline Queue Key**: `carepill_offline_dose_queue`
* **Mechanism**: When offline, medicine status changes and logs are written to local persistent storage (`SharedPreferences` / `Hive`). Once network connectivity is restored, the `LocalStorageService` flushes the offline queue to Cloud Firestore automatically.

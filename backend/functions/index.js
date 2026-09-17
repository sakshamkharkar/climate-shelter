/**
 * CAREPILL ELDER CARE MEDICATION MANAGEMENT SYSTEM
 * Firebase Cloud Functions (Node.js Backend Engine)
 * 
 * Features:
 * 1. Automatic Dynamic Adherence Percentage Calculation: (Taken / Total) * 100
 * 2. Automated Missed/Skipped Dose Escalation (Twilio SMS + SendGrid Email + FCM Push)
 * 3. Scheduled Time-Based Dose Reminders (Pub/Sub Cron)
 * 4. Emergency SOS Emergency Broadcast Handler
 */

const functions = require('firebase-functions');
const admin = require('firebase-admin');
const twilio = require('twilio');
const sgMail = require('@sendgrid/mail');

admin.initializeApp();
const db = admin.firestore();

// Configure Twilio & SendGrid credentials (from environment configs)
const twilioClient = twilio(
  functions.config().twilio.account_sid,
  functions.config().twilio.auth_token
);
sgMail.setApiKey(functions.config().sendgrid.api_key);

/**
 * 1. FIRESTORE TRIGGER: On Medication Status Changed
 * Triggered when a patient or caregiver marks a dose as TAKEN, SKIPPED, or MISSED.
 */
exports.onDoseStatusChanged = functions.firestore
  .document('patients/{patientId}/doseLogs/{logId}')
  .onWrite(async (change, context) => {
    const { patientId } = context.params;
    const logData = change.after.exists ? change.after.data() : null;

    if (!logData) return null;

    const { status, medicineName, dosage, scheduledTime, patientName } = logData;

    // Fetch patient master record
    const patientRef = db.collection('patients').doc(patientId);
    const patientDoc = await patientRef.get();
    if (!patientDoc.exists) return null;

    const patient = patientDoc.data();

    // Recalculate Dynamic Adherence Percentage
    const logsSnapshot = await patientRef.collection('doseLogs').get();
    let takenCount = 0;
    let skippedCount = 0;
    let missedCount = 0;

    logsSnapshot.forEach(doc => {
      const data = doc.data();
      if (data.status === 'TAKEN') takenCount++;
      else if (data.status === 'SKIPPED') skippedCount++;
      else if (data.status === 'MISSED') missedCount++;
    });

    const notEatenCount = skippedCount + missedCount;
    const totalDoses = takenCount + notEatenCount;
    const adherencePercentage = totalDoses > 0 ? Math.round((takenCount / totalDoses) * 100) : 100;

    // Update Patient Master Document with recalculations
    await patientRef.update({
      totalTaken: takenCount,
      totalSkipped: skippedCount,
      totalMissed: missedCount,
      adherencePercentage: adherencePercentage,
      lastUpdated: admin.firestore.FieldValue.serverTimestamp()
    });

    console.log(`[Adherence Recalculated] Patient: ${patient.patientName} -> Adherence: ${adherencePercentage}% (Taken: ${takenCount}, Not Eaten: ${notEatenCount})`);

    // Escalation: Send automated alerts if dose is SKIPPED or MISSED
    if (status === 'SKIPPED' || status === 'MISSED') {
      const alertMsg = `🚨 CAREPILL ALERT: Patient ${patientName || patient.patientName} has ${status} scheduled medication: ${medicineName} (${dosage}) at ${scheduledTime}. Current adherence rate: ${adherencePercentage}%.`;

      // A. Send FCM Push Notification to Caregiver & Doctor Devices
      const caregiverFcmToken = patient.caregiverFcmToken;
      const doctorFcmToken = patient.doctorFcmToken;

      const fcmTokens = [caregiverFcmToken, doctorFcmToken].filter(Boolean);
      if (fcmTokens.length > 0) {
        await admin.messaging().sendMulticast({
          tokens: fcmTokens,
          notification: {
            title: `⚠️ ${status} Medication Alert!`,
            body: alertMsg
          },
          data: {
            patientId: patientId,
            status: status,
            click_action: 'FLUTTER_NOTIFICATION_CLICK'
          }
        });
        console.log(`[FCM Dispatched] Sent push notification to ${fcmTokens.length} devices.`);
      }

      // B. Send Automated Twilio SMS to Nurse/Caregiver & Doctor
      if (patient.caregiverPhone) {
        try {
          await twilioClient.messages.create({
            body: alertMsg,
            from: functions.config().twilio.phone_number,
            to: patient.caregiverPhone
          });
          console.log(`[Twilio SMS Sent] Dispatched SMS to Caregiver: ${patient.caregiverPhone}`);
        } catch (smsErr) {
          console.error(`[Twilio SMS Error]`, smsErr);
        }
      }

      // C. Send SendGrid Email to Caregiver & Doctor
      if (patient.caregiverEmail || patient.doctorEmail) {
        const recipients = [patient.caregiverEmail, patient.doctorEmail].filter(Boolean);
        try {
          await sgMail.send({
            to: recipients,
            from: 'alerts@carepill.health',
            subject: `⚠️ URGENT: Dose ${status} Notification for ${patient.patientName}`,
            html: `
              <div style="font-family:Arial, sans-serif; padding:20px; border:2px solid #EF4444; border-radius:12px;">
                <h2 style="color:#EF4444;">🚨 Dose ${status} Escalation Notice</h2>
                <p><b>Patient:</b> ${patient.patientName}</p>
                <p><b>Medication:</b> ${medicineName} (${dosage})</p>
                <p><b>Scheduled Time:</b> ${scheduledTime}</p>
                <p><b>Calculated Adherence Rate:</b> <span style="font-size:18px; font-weight:bold; color:#0284C7;">${adherencePercentage}%</span></p>
                <hr>
                <p style="font-size:12px; color:#64748B;">CarePill Automated Health Escalation System</p>
              </div>
            `
          });
          console.log(`[SendGrid Email Sent] Dispatched alert email to ${recipients.join(', ')}`);
        } catch (emailErr) {
          console.error(`[SendGrid Email Error]`, emailErr);
        }
      }

      // Log activity to Firestore feed
      await patientRef.collection('activityLogs').add({
        text: `📲 Auto-SMS & Email Dispatched to Caregiver: "${status} ${medicineName}"`,
        timestamp: admin.firestore.FieldValue.serverTimestamp()
      });
    }

    return null;
  });

/**
 * 2. PUB/SUB CRON TRIGGER: Scheduled Time-Based Alarm Reminders
 * Runs every minute to query pending doses and dispatch alarm triggers.
 */
exports.checkScheduledDoseAlarms = functions.pubsub
  .schedule('every 1 minutes')
  .onRun(async (context) => {
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    const formattedHour = hours < 10 ? `0${hours}` : `${hours}`;
    const formattedMin = minutes < 10 ? `0${minutes}` : `${minutes}`;
    const currentTimeStr = `${formattedHour}:${formattedMin} ${ampm}`;

    console.log(`[Cron Alarm Checker] Checking pending doses for time: ${currentTimeStr}`);

    const patientsSnapshot = await db.collection('patients').get();
    
    for (const patientDoc of patientsSnapshot.docs) {
      const patient = patientDoc.data();
      const patientId = patientDoc.id;

      const pendingMedsSnapshot = await patientDoc.ref
        .collection('medicines')
        .where('status', '==', 'PENDING')
        .where('time', '==', currentTimeStr)
        .get();

      pendingMedsSnapshot.forEach(async (medDoc) => {
        const med = medDoc.data();
        console.log(`[Alarm Triggered] Patient: ${patient.patientName} -> Med: ${med.name} (${med.time})`);

        // Send high-priority FCM Push Notification to sound phone alarm
        if (patient.patientFcmToken) {
          await admin.messaging().send({
            token: patient.patientFcmToken,
            notification: {
              title: `⏰ MEDICATION REMINDER: ${med.name}`,
              body: `Time to take ${med.name} (${med.dosage}). ${med.instructions}`
            },
            data: {
              medId: medDoc.id,
              alarmType: 'AUTOMATIC_TIME_ALARM',
              sound: 'alarm_chime.wav'
            }
          });
        }
      });
    }

    return null;
  });

/**
 * 3. HTTP CALLABLE FUNCTION: Emergency SOS Alert Broadcast
 */
exports.triggerEmergencySOS = functions.https.onCall(async (data, context) => {
  const { patientId, locationStr } = data;
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated.');
  }

  const patientDoc = await db.collection('patients').doc(patientId).get();
  if (!patientDoc.exists) {
    throw new functions.https.HttpsError('not-found', 'Patient record not found.');
  }

  const patient = patientDoc.data();
  const sosMsg = `🚨 EMERGENCY SOS ACTIVATED! Patient ${patient.patientName} triggered emergency alarm. Location: ${locationStr || 'Home Address'}. Contact Doctor (${patient.doctorPhone}) or Caregiver (${patient.caregiverPhone}) immediately!`;

  // Send SMS to Doctor and Caregiver
  const phoneNumbers = [patient.caregiverPhone, patient.doctorPhone].filter(Boolean);
  for (const phone of phoneNumbers) {
    await twilioClient.messages.create({
      body: sosMsg,
      from: functions.config().twilio.phone_number,
      to: phone
    });
  }

  return { success: true, message: 'Emergency SOS Broadcasted successfully.' };
});

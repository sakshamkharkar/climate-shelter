// CAREPILL MULTI-USER & REALTIME CLOUD SYNC ENGINE

const syncChannel = new BroadcastChannel('carepill_multiuser_sync');

let appState = {
  isLoggedIn: false,
  currentUserEmail: 'eleanor@patient.com',
  activeRole: 'patient',
  activePatientId: 'pat_1',
  highContrast: false,
  voiceReadEnabled: false,
  securityPin: '1234',
  pendingPinAction: null,
  lastTriggeredAlarmMinute: '',

  // Multi-Patient Tenant Database
  patients: {
    pat_1: {
      id: 'pat_1',
      patientName: 'Eleanor Vance',
      category: 'Cardiology Care',
      totalTaken: 28,
      totalSkipped: 2,
      totalMissed: 1,
      contacts: {
        docName: 'Dr. Sarah Jenkins',
        docSpecialty: 'Cardiology Specialist',
        docPhone: '+1 (555) 234-5678',
        docEmail: 'dr.jenkins@health.org',
        cgName: 'Mary Higgins (Nurse)',
        cgPhone: '+1 (555) 876-5432',
        cgEmail: 'mary.higgins@care.org'
      },
      medicines: [
        {
          id: 'med_101',
          name: 'Lisinopril',
          dosage: '10mg • 1 Pill',
          form: 'Pill 💊',
          time: '08:00 AM',
          instructions: 'Take after breakfast with full glass of water',
          stock: 24,
          status: 'PENDING'
        },
        {
          id: 'med_102',
          name: 'Metformin',
          dosage: '500mg • 1 Tablet',
          form: 'Pill 💊',
          time: '12:30 PM',
          instructions: 'Take with lunch',
          stock: 45,
          status: 'PENDING'
        },
        {
          id: 'med_103',
          name: 'Atorvastatin',
          dosage: '20mg • 1 Pill',
          form: 'Pill 💊',
          time: '08:00 PM',
          instructions: 'Take before bedtime',
          stock: 12,
          status: 'PENDING'
        }
      ],
      activityFeed: [
        { time: 'Today 08:30 AM', text: '✉️ Auto-SMS Sent to Nurse Mary: "Eleanor took morning Lisinopril"' },
        { time: 'Yesterday 08:00 PM', text: 'Eleanor took Atorvastatin 20mg (On Time)' },
        { time: 'Yesterday 12:30 PM', text: '🚨 Auto-SMS Alert Sent to Dr. Jenkins & Mary: "Eleanor SKIPPED Metformin 500mg"' }
      ]
    },

    pat_2: {
      id: 'pat_2',
      patientName: 'Robert Chen',
      category: 'Diabetes Care',
      totalTaken: 40,
      totalSkipped: 1,
      totalMissed: 0,
      contacts: {
        docName: 'Dr. Michael Chang',
        docSpecialty: 'Endocrinology Specialist',
        docPhone: '+1 (555) 999-1122',
        docEmail: 'dr.chang@diabeteshealth.org',
        cgName: 'Sarah Adams (Nurse)',
        cgPhone: '+1 (555) 333-4455',
        cgEmail: 'sarah.adams@care.org'
      },
      medicines: [
        {
          id: 'med_201',
          name: 'Insulin Glargine',
          dosage: '10 Units',
          form: 'Injection 💉',
          time: '07:30 AM',
          instructions: 'Inject subcutaneously before breakfast',
          stock: 15,
          status: 'PENDING'
        },
        {
          id: 'med_202',
          name: 'Glipizide',
          dosage: '5mg • 1 Tablet',
          form: 'Pill 💊',
          time: '12:00 PM',
          instructions: 'Take 30 minutes before meal',
          stock: 30,
          status: 'PENDING'
        }
      ],
      activityFeed: [
        { time: 'Today 07:30 AM', text: '✅ Robert injected 10 Units Insulin Glargine on schedule.' }
      ]
    },

    pat_3: {
      id: 'pat_3',
      patientName: 'Margaret Taylor',
      category: 'Hypertension Care',
      totalTaken: 19,
      totalSkipped: 3,
      totalMissed: 2,
      contacts: {
        docName: 'Dr. David Miller',
        docSpecialty: 'Geriatric Specialist',
        docPhone: '+1 (555) 444-7788',
        docEmail: 'dr.miller@geriatrics.org',
        cgName: 'Emily Watson (Nurse)',
        cgPhone: '+1 (555) 222-6611',
        cgEmail: 'emily.watson@care.org'
      },
      medicines: [
        {
          id: 'med_301',
          name: 'Amlodipine',
          dosage: '5mg • 1 Pill',
          form: 'Pill 💊',
          time: '09:00 AM',
          instructions: 'Take in morning with water',
          stock: 20,
          status: 'PENDING'
        },
        {
          id: 'med_302',
          name: 'Aspirin Low Dose',
          dosage: '81mg • 1 Pill',
          form: 'Pill 💊',
          time: '01:00 PM',
          instructions: 'Take after lunch',
          stock: 50,
          status: 'PENDING'
        }
      ],
      activityFeed: [
        { time: 'Yesterday 09:00 AM', text: '⚠️ Margaret missed Amlodipine 5mg morning dose.' }
      ]
    }
  },

  currentAlarmMedId: null
};

// Helper: Get Current Active Patient Profile
function getActivePatient() {
  return appState.patients[appState.activePatientId] || appState.patients['pat_1'];
}

// PERSIST & BROADCAST STATE ACROSS ALL CONNECTED PHONES/TABS
function persistAppState() {
  localStorage.setItem('carepill_multiuser_data', JSON.stringify({
    patients: appState.patients,
    activePatientId: appState.activePatientId,
    securityPin: appState.securityPin,
    isLoggedIn: appState.isLoggedIn,
    activeRole: appState.activeRole,
    currentUserEmail: appState.currentUserEmail
  }));

  try {
    syncChannel.postMessage({ type: 'STATE_UPDATE', timestamp: Date.now() });
  } catch(e) {
    console.log('BroadcastChannel error:', e);
  }
}

// LISTEN FOR CROSS-DEVICE / MULTI-TAB SYNC UPDATES
syncChannel.onmessage = (event) => {
  if (event.data && event.data.type === 'STATE_UPDATE') {
    loadAppStateFromStorage();
    renderAllViews();
    showSyncFlashIndicator();
  }
};

window.addEventListener('storage', (e) => {
  if (e.key === 'carepill_multiuser_data') {
    loadAppStateFromStorage();
    renderAllViews();
    showSyncFlashIndicator();
  }
});

function showSyncFlashIndicator() {
  const pill = document.getElementById('syncStatusPill');
  if (pill) {
    pill.style.background = '#34D399';
    pill.style.color = '#FFFFFF';
    setTimeout(() => {
      pill.style.background = '#ECFDF5';
      pill.style.color = '#065F46';
    }, 1500);
  }
}

// LOAD STATE FROM STORAGE AT STARTUP
function loadAppStateFromStorage() {
  const savedData = localStorage.getItem('carepill_multiuser_data');
  if (savedData) {
    try {
      const parsed = JSON.parse(savedData);
      if (parsed.patients) appState.patients = parsed.patients;
      if (parsed.activePatientId) appState.activePatientId = parsed.activePatientId;
      if (parsed.securityPin) appState.securityPin = parsed.securityPin;
      if (parsed.isLoggedIn !== undefined) appState.isLoggedIn = parsed.isLoggedIn;
      if (parsed.activeRole) appState.activeRole = parsed.activeRole;
      if (parsed.currentUserEmail) appState.currentUserEmail = parsed.currentUserEmail;
    } catch (e) {
      console.log('Error reading storage data:', e);
    }
  }
}

function checkInitialSetup() {
  loadAppStateFromStorage();
  if (appState.isLoggedIn) {
    document.getElementById('loginModal').classList.remove('active');
    switchRole(appState.activeRole);
  } else {
    document.getElementById('loginModal').classList.add('active');
  }
  updatePatientSelectDropdowns();
}

// DYNAMICALLY SWITCH ACTIVE PATIENT ACCOUNT AND RE-RENDER ALL MEDICINE INFO
function changeActivePatient(patientId, targetRole = null) {
  if (appState.patients[patientId]) {
    appState.activePatientId = patientId;
    persistAppState();
    updatePatientSelectDropdowns();

    if (targetRole) {
      switchRole(targetRole);
    }

    renderAllViews();
    const activePatient = getActivePatient();
    showSyncFlashIndicator();
  }
}

function updatePatientSelectDropdowns() {
  const activeSel = document.getElementById('activePatientSelect');
  const loginSel = document.getElementById('loginPatientSelect');

  const optionsHtml = Object.values(appState.patients).map(p => `
    <option value="${p.id}">${p.patientName} (${p.category})</option>
  `).join('');

  if (activeSel) {
    activeSel.innerHTML = optionsHtml;
    activeSel.value = appState.activePatientId;
  }
  if (loginSel) {
    loginSel.innerHTML = optionsHtml;
    loginSel.value = appState.activePatientId;
  }
}

// REGISTER NEW PATIENT ACCOUNT PROFILE
function openAddPatientModal() {
  document.getElementById('addPatientModal').classList.add('active');
}

function closeAddPatientModal() {
  document.getElementById('addPatientModal').classList.remove('active');
}

function saveNewPatient(e) {
  e.preventDefault();
  const name = document.getElementById('newPatientName').value;
  const category = document.getElementById('newPatientCategory').value;
  const docName = document.getElementById('newPatientDocName').value;
  const docPhone = document.getElementById('newPatientDocPhone').value;
  const cgName = document.getElementById('newPatientCgName').value;
  const cgPhone = document.getElementById('newPatientCgPhone').value;

  const newId = `pat_${Date.now()}`;
  appState.patients[newId] = {
    id: newId,
    patientName: name,
    category: category,
    totalTaken: 0,
    totalSkipped: 0,
    totalMissed: 0,
    contacts: {
      docName: docName,
      docSpecialty: 'Attending Physician',
      docPhone: docPhone,
      docEmail: 'doctor@carenet.org',
      cgName: cgName,
      cgPhone: cgPhone,
      cgEmail: 'caregiver@carenet.org'
    },
    medicines: [],
    activityFeed: [
      { time: 'Just Now', text: `🎉 Patient profile created for ${name} (${category})` }
    ]
  };

  appState.activePatientId = newId;
  persistAppState();
  updatePatientSelectDropdowns();
  renderAllViews();
  closeAddPatientModal();
  document.getElementById('addPatientForm').reset();
  alert(`🎉 Registered new patient profile for ${name}! Add their medicines to the schedule.`);
}

// AUTOMATIC TIME-BASED ALARM SCHEDULER
function startAutomaticAlarmClock() {
  setInterval(() => {
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    const formattedHour = hours < 10 ? `0${hours}` : `${hours}`;
    const formattedMin = minutes < 10 ? `0${minutes}` : `${minutes}`;
    const currentTimeStr = `${formattedHour}:${formattedMin} ${ampm}`;

    const clockEl = document.getElementById('currentTimeDisplay');
    if (clockEl) clockEl.innerText = currentTimeStr;

    if (appState.lastTriggeredAlarmMinute !== currentTimeStr) {
      const activePatient = getActivePatient();
      const matchingMed = activePatient.medicines.find(m => m.status === 'PENDING' && m.time.toUpperCase() === currentTimeStr.toUpperCase());
      if (matchingMed) {
        appState.lastTriggeredAlarmMinute = currentTimeStr;
        triggerAlarmForMed(matchingMed.id);
      }
    }
  }, 1000);
}

function triggerAlarmForMed(medId) {
  const activePatient = getActivePatient();
  const med = activePatient.medicines.find(m => m.id === medId) || activePatient.medicines.find(m => m.status === 'PENDING') || activePatient.medicines[0];
  if (!med) return;

  appState.currentAlarmMedId = med.id;

  document.getElementById('alarmMedName').innerText = med.name;
  document.getElementById('alarmDosage').innerText = `${med.dosage} • ${med.instructions}`;
  document.getElementById('alarmClock').innerText = med.time;

  document.getElementById('alarmModal').classList.add('active');
  playAlarmChime();
}

function triggerTestAutoAlarmNow() {
  const activePatient = getActivePatient();
  const pendingMed = activePatient.medicines.find(m => m.status === 'PENDING') || activePatient.medicines[0];
  if (pendingMed) {
    triggerAlarmForMed(pendingMed.id);
  } else {
    alert(`All doses for ${activePatient.patientName} have been completed!`);
  }
}

// LOGIN MODAL ENGINE
function openStartingLoginModal() {
  updatePatientSelectDropdowns();
  document.getElementById('loginModal').classList.add('active');
}

function closeStartingLoginModal() {
  document.getElementById('loginModal').classList.remove('active');
}

function setDemoLogin(role) {
  const roleSelect = document.getElementById('loginRole');
  const userField = document.getElementById('loginUsername');
  
  if (role === 'patient') {
    userField.value = 'patient@carepill.com';
    roleSelect.value = 'patient';
  } else if (role === 'caregiver') {
    userField.value = 'nurse.mary@caregiver.org';
    roleSelect.value = 'caregiver';
  } else if (role === 'family') {
    userField.value = 'family.daughter@care.org';
    roleSelect.value = 'family';
  } else if (role === 'manager') {
    userField.value = 'admin@elderfacility.org';
    roleSelect.value = 'manager';
  }
}

function handleUserLogin(e) {
  e.preventDefault();
  const selectedPatId = document.getElementById('loginPatientSelect').value;
  const username = document.getElementById('loginUsername').value;
  const role = document.getElementById('loginRole').value;

  appState.isLoggedIn = true;
  appState.currentUserEmail = username;
  appState.activeRole = role;
  if (selectedPatId) appState.activePatientId = selectedPatId;

  persistAppState();
  closeStartingLoginModal();

  switchRole(role);
  renderAllViews();
  alert(`🔓 Login Successful! Connected to ${getActivePatient().patientName}'s medicine schedule.`);
}

function updateSessionPillLabel() {
  const label = document.getElementById('sessionUserLabel');
  if (!label) return;
  const activePatient = getActivePatient();
  const roleTitle = appState.activeRole.charAt(0).toUpperCase() + appState.activeRole.slice(1);

  if (appState.activeRole === 'patient') {
    label.innerText = `${activePatient.patientName} (Patient)`;
  } else if (appState.activeRole === 'caregiver') {
    label.innerText = `${activePatient.contacts.cgName} (Caregiver)`;
  } else if (appState.activeRole === 'manager') {
    label.innerText = `Facility Admin (Manager)`;
  } else {
    label.innerText = `Family Member (${roleTitle})`;
  }
}

function calculateAdherencePercentage() {
  const activePatient = getActivePatient();
  const notEaten = activePatient.totalSkipped + activePatient.totalMissed;
  const total = activePatient.totalTaken + notEaten;
  if (total === 0) return 100;
  return Math.round((activePatient.totalTaken / total) * 100);
}

function playAlarmChime() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();

    const notes = [523.25, 659.25, 783.99, 1046.50];
    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'square';
      osc.frequency.value = freq;

      gain.gain.setValueAtTime(0.2, ctx.currentTime + idx * 0.2);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.2 + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(ctx.currentTime + idx * 0.2);
      osc.stop(ctx.currentTime + idx * 0.2 + 0.4);
    });
  } catch (e) {
    console.log('Audio playback error:', e);
  }
}

// RENDER ALL VIEWS ACCORDING TO ACTIVE PATIENT
function renderAllViews() {
  const activePatient = getActivePatient();
  
  document.getElementById('greetingPatientName').innerText = activePatient.patientName;
  document.getElementById('cgProfilePatientName').innerText = activePatient.patientName;
  document.getElementById('sosPatientName').innerText = activePatient.patientName;

  document.querySelectorAll('.active-patient-title-name').forEach(el => {
    el.innerText = activePatient.patientName;
  });

  updateSessionPillLabel();
  renderContacts();
  renderSchedule();
  renderActivityFeed();
  renderManagerRoster();
}

function renderContacts() {
  const activePatient = getActivePatient();
  const c = activePatient.contacts;

  document.getElementById('docName').innerText = c.docName;
  document.getElementById('docSpecialty').innerText = c.docSpecialty;
  document.getElementById('docPhoneLink').innerText = c.docPhone;
  document.getElementById('docEmailLink').innerText = c.docEmail;

  document.getElementById('cgName').innerText = c.cgName;
  document.getElementById('cgPhoneLink').innerText = c.cgPhone;
  document.getElementById('cgEmailLink').innerText = c.cgEmail;

  document.getElementById('sosContacts').innerText = `${c.docName} (${c.docPhone}) & ${c.cgName} (${c.cgPhone})`;
}

function openPinModal(action) {
  appState.pendingPinAction = action;
  document.getElementById('pinInput').value = '';
  document.getElementById('pinErrorMsg').style.display = 'none';
  document.getElementById('pinModal').classList.add('active');
}

function closePinModal() {
  document.getElementById('pinModal').classList.remove('active');
  appState.pendingPinAction = null;
}

function verifyPin() {
  const enteredPin = document.getElementById('pinInput').value;
  if (enteredPin === appState.securityPin) {
    closePinModal();
    const action = appState.pendingPinAction;

    if (action === 'editContacts') {
      openEditContactsModal();
    } else if (action === 'security') {
      alert('🔒 Security Authentication Successful: AES-256 Vault unlocked.');
    }
  } else {
    document.getElementById('pinErrorMsg').style.display = 'block';
  }
}

function openEditContactsModal() {
  const activePatient = getActivePatient();
  const c = activePatient.contacts;
  document.getElementById('editDocName').value = c.docName;
  document.getElementById('editDocPhone').value = c.docPhone;
  document.getElementById('editDocEmail').value = c.docEmail;

  document.getElementById('editCgName').value = c.cgName;
  document.getElementById('editCgPhone').value = c.cgPhone;
  document.getElementById('editCgEmail').value = c.cgEmail;

  document.getElementById('editContactsModal').classList.add('active');
}

function closeEditContactsModal() {
  document.getElementById('editContactsModal').classList.remove('active');
}

function saveContacts(e) {
  e.preventDefault();
  const activePatient = getActivePatient();

  activePatient.contacts.docName = document.getElementById('editDocName').value;
  activePatient.contacts.docPhone = document.getElementById('editDocPhone').value;
  activePatient.contacts.docEmail = document.getElementById('editDocEmail').value;

  activePatient.contacts.cgName = document.getElementById('editCgName').value;
  activePatient.contacts.cgPhone = document.getElementById('editCgPhone').value;
  activePatient.contacts.cgEmail = document.getElementById('editCgEmail').value;

  persistAppState();
  renderContacts();
  closeEditContactsModal();
  alert('✅ Contacts updated and synced across all devices!');
}

function openSendMessageModal(recipient) {
  document.getElementById('msgRecipient').value = recipient;
  document.getElementById('msgBody').value = '';
  document.getElementById('sendMessageModal').classList.add('active');
}

function closeSendMessageModal() {
  document.getElementById('sendMessageModal').classList.remove('active');
}

function applyMsgTemplate(type) {
  const body = document.getElementById('msgBody');
  const activePatient = getActivePatient();
  if (type === 'MISSED') {
    body.value = `⚠️ URGENT: Patient ${activePatient.patientName} skipped/missed a scheduled medication dose. Please check adherence logs.`;
  } else if (type === 'REFILL') {
    body.value = `📦 REFILL REQUEST: Medicine inventory is low for ${activePatient.patientName}. Requesting prescription refill.`;
  } else if (type === 'UPDATE') {
    body.value = `📋 HEALTH UPDATE: ${activePatient.patientName}'s adherence rate is currently ${calculateAdherencePercentage()}%. All morning doses taken on time.`;
  }
}

function dispatchMessage(e) {
  e.preventDefault();
  const recipient = document.getElementById('msgRecipient').value;
  const channel = document.getElementById('msgChannel').value;
  const messageText = document.getElementById('msgBody').value;
  const activePatient = getActivePatient();

  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  activePatient.activityFeed.unshift({
    time: `Today ${timeStr}`,
    text: `📲 ${channel} Sent to ${recipient}: "${messageText.substring(0, 45)}..."`
  });

  persistAppState();
  closeSendMessageModal();
  renderActivityFeed();
  alert(`🚀 Message dispatched via ${channel} to ${recipient} successfully!`);
}

function markDoseDirectly(medId, responseType) {
  const activePatient = getActivePatient();
  const med = activePatient.medicines.find(m => m.id === medId);
  if (!med) return;

  med.status = responseType;
  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  if (responseType === 'TAKEN') {
    activePatient.totalTaken += 1;
    if (med.stock > 0) med.stock -= 1;

    activePatient.activityFeed.unshift({
      time: `Today ${timeStr}`,
      text: `✅ ${activePatient.patientName} TOOK ${med.name} (${med.dosage}) — Adherence updated live!`
    });
  } else if (responseType === 'SKIPPED') {
    activePatient.totalSkipped += 1;

    const autoAlertMsg = `🚨 AUTOMATED ALERT: ${activePatient.patientName} SKIPPED ${med.name} (${med.dosage}) scheduled for ${med.time}.`;
    activePatient.activityFeed.unshift({
      time: `Today ${timeStr}`,
      text: `📲 Auto-SMS & Push Dispatched to ${activePatient.contacts.docName} & ${activePatient.contacts.cgName}: "${autoAlertMsg}"`
    });
  }

  persistAppState();
  renderSchedule();
  renderActivityFeed();
}

// RENDER MEDICINE BOX SCHEDULE (DYNAMIC PER ACTIVE PATIENT)
function renderSchedule() {
  const activePatient = getActivePatient();
  const container = document.getElementById('scheduleList');
  if (!container) return;

  if (activePatient.medicines.length === 0) {
    container.innerHTML = `
      <div style="text-align:center; padding:30px; background:#F8FAFC; border:2px dashed var(--card-border); border-radius:16px;">
        <p style="font-size:16px; font-weight:700; color:var(--primary-navy);">No medicine schedule box found for ${activePatient.patientName}.</p>
        <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">Click the button below to add the first medication dose!</p>
        <button class="btn btn-primary btn-sm" style="margin-top:14px;" onclick="openAddMedicineModal()">➕ Add First Medicine</button>
      </div>
    `;
  } else {
    container.innerHTML = activePatient.medicines.map(med => {
      let statusClass = '';
      let statusLabel = '';

      if (med.status === 'TAKEN') {
        statusClass = 'status-taken';
        statusLabel = '✓ TAKEN (Eaten)';
      } else if (med.status === 'SKIPPED') {
        statusClass = 'status-skipped';
        statusLabel = '❌ NOT EATEN (Skipped)';
      }

      return `
        <div class="med-card ${statusClass}">
          <div class="med-time-badge">${med.time}</div>
          <div class="med-info">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
              <span style="font-size:10px; background:#E0F2FE; color:var(--accent-blue); padding:2px 8px; border-radius:10px; font-weight:800;">👤 ${activePatient.patientName}</span>
              <span style="font-size:10px; background:#F1F5F9; color:var(--text-muted); padding:2px 8px; border-radius:10px;">${med.form}</span>
            </div>
            <h4>${med.name}</h4>
            <p>Dosage: <b>${med.dosage}</b></p>
            <p style="font-style:italic;">"${med.instructions}"</p>
          </div>
          <div class="med-actions">
            ${med.status === 'PENDING' 
              ? `<button class="btn btn-success btn-sm" onclick="markDoseDirectly('${med.id}', 'TAKEN')">Take Now</button>
                 <button class="btn btn-danger btn-sm" onclick="markDoseDirectly('${med.id}', 'SKIPPED')">Skip</button>`
              : `<span class="badge ${med.status === 'TAKEN' ? 'badge-success' : 'badge-warning'}">${statusLabel}</span>`
            }
          </div>
        </div>
      `;
    }).join('');
  }

  const pending = activePatient.medicines.filter(m => m.status === 'PENDING').length;
  const pendingEl = document.getElementById('pendingCount');
  if (pendingEl) pendingEl.innerText = pending;

  renderInventory();
  updateAdherenceMetricsUI();
}

function updateAdherenceMetricsUI() {
  const activePatient = getActivePatient();
  const notEatenCount = activePatient.totalSkipped + activePatient.totalMissed;
  const adherencePct = calculateAdherencePercentage();

  const patientAdhEl = document.getElementById('patientAdherence');
  if (patientAdhEl) {
    patientAdhEl.innerText = `${adherencePct}%`;
    patientAdhEl.style.color = adherencePct >= 90 ? '#34D399' : (adherencePct >= 80 ? '#FBBF24' : '#F87171');
  }

  const patientMissedEl = document.getElementById('patientMissedCount');
  if (patientMissedEl) patientMissedEl.innerText = `${notEatenCount} Times`;

  const cgAdhEl = document.getElementById('cgAdherence');
  if (cgAdhEl) cgAdhEl.innerText = `${adherencePct}%`;

  const cgTakenEl = document.getElementById('cgTaken');
  if (cgTakenEl) cgTakenEl.innerText = activePatient.totalTaken;

  const cgMissedEl = document.getElementById('cgMissed');
  if (cgMissedEl) cgMissedEl.innerText = `${notEatenCount} Times`;

  const familyStatusEl = document.getElementById('familyStatusText');
  if (familyStatusEl) {
    familyStatusEl.innerHTML = `
      ${activePatient.patientName} has taken <b>${activePatient.totalTaken} doses</b> and 
      <b style="color:var(--rose-red);">skipped / missed ${notEatenCount} doses</b>. 
      Calculated real-time adherence rate is <b style="color:var(--accent-blue);">${adherencePct}%</b>.
    `;
  }
}

function renderInventory() {
  const activePatient = getActivePatient();
  const container = document.getElementById('inventoryList');
  if (!container) return;

  if (activePatient.medicines.length === 0) {
    container.innerHTML = `<div style="font-size:12px; color:var(--text-muted); padding:10px 0;">No pill stock logged for ${activePatient.patientName}.</div>`;
    return;
  }

  container.innerHTML = activePatient.medicines.map(med => {
    const isLow = med.stock <= 15;
    return `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid var(--card-border);">
        <div>
          <b style="font-size:14px;">${med.name}</b>
          <div style="font-size:11px; color:var(--text-muted);">${med.dosage}</div>
        </div>
        <div>
          <span class="badge ${isLow ? 'badge-warning' : 'badge-info'}">${med.stock} left</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderActivityFeed() {
  const activePatient = getActivePatient();
  const cgFeed = document.getElementById('activityFeed');
  const patientFeed = document.getElementById('patientActivityFeed');

  const logsHtml = activePatient.activityFeed.map(item => `
    <div class="activity-item">
      <div class="time">${item.time}</div>
      <div>${item.text}</div>
    </div>
  `).join('');

  if (cgFeed) cgFeed.innerHTML = logsHtml;
  if (patientFeed) patientFeed.innerHTML = logsHtml;
}

// RENDER COMPLETE MANAGER FACILITY PATIENT ROSTER TABLE & OVERVIEW STATS
function renderManagerRoster() {
  const tbody = document.getElementById('managerRosterTableBody');
  if (!tbody) return;

  const allPatients = Object.values(appState.patients);

  // Update Manager Overview Stats
  const totalCountEl = document.getElementById('mgrTotalPatientCount');
  if (totalCountEl) totalCountEl.innerText = allPatients.length;

  let totalMedsCount = 0;
  let totalAdhSum = 0;

  allPatients.forEach(p => {
    totalMedsCount += p.medicines.length;
    const notEaten = p.totalSkipped + p.totalMissed;
    const total = p.totalTaken + notEaten;
    const adhPct = total === 0 ? 100 : Math.round((p.totalTaken / total) * 100);
    totalAdhSum += adhPct;
  });

  const avgAdherence = allPatients.length > 0 ? Math.round(totalAdhSum / allPatients.length) : 100;
  const avgAdhEl = document.getElementById('mgrAvgAdherence');
  if (avgAdhEl) avgAdhEl.innerText = `${avgAdherence}%`;

  const totalMedsEl = document.getElementById('mgrTotalMedsCount');
  if (totalMedsEl) totalMedsEl.innerText = totalMedsCount;

  // Render Table Rows for ALL Patients in the Facility Roster
  tbody.innerHTML = allPatients.map(p => {
    const notEaten = p.totalSkipped + p.totalMissed;
    const total = p.totalTaken + notEaten;
    const adhPct = total === 0 ? 100 : Math.round((p.totalTaken / total) * 100);

    const medNamesList = p.medicines.length > 0 
      ? p.medicines.map(m => `<b>${m.name}</b> (${m.time})`).join(', ') 
      : '<span style="color:var(--text-muted);">No medicines scheduled</span>';

    return `
      <tr style="${p.id === appState.activePatientId ? 'background:#EFF6FF; border-left:4px solid var(--accent-blue);' : ''}">
        <td>
          <div style="font-weight:800; font-size:14px; color:var(--primary-navy);">👤 ${p.patientName}</div>
          <span style="font-size:11px; background:#F1F5F9; color:var(--accent-blue); padding:2px 8px; border-radius:10px; font-weight:700;">${p.category}</span>
        </td>
        <td style="font-size:12px;">${medNamesList}</td>
        <td>
          <b style="font-size:15px; color:${adhPct >= 90 ? '#10B981' : (adhPct >= 80 ? '#F59E0B' : '#EF4444')}">${adhPct}%</b>
          <div style="font-size:10px; color:var(--text-muted);">${p.totalTaken} Taken / ${notEaten} Skipped</div>
        </td>
        <td style="font-size:12px;">
          <b>${p.contacts.docName}</b><br>
          <span style="font-size:11px; color:var(--text-muted);">${p.contacts.docPhone}</span>
        </td>
        <td style="font-size:12px;">
          <b>${p.contacts.cgName}</b><br>
          <span style="font-size:11px; color:var(--text-muted);">${p.contacts.cgPhone}</span>
        </td>
        <td>
          <button class="btn btn-primary btn-sm" onclick="changeActivePatient('${p.id}', 'patient')">👁️ View Dashboard</button>
        </td>
      </tr>
    `;
  }).join('');
}

function switchRole(role) {
  appState.activeRole = role;
  document.querySelectorAll('.role-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.role === role);
  });

  document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
  const activeView = document.getElementById(`${role}View`);
  if (activeView) activeView.classList.add('active');

  updateSessionPillLabel();
}

function respondToAlarm(responseType) {
  document.getElementById('alarmModal').classList.remove('active');
  const medId = appState.currentAlarmMedId;

  if (medId) {
    markDoseDirectly(medId, responseType);
  }
}

function openAddMedicineModal() {
  document.getElementById('inputPassword').value = '';
  document.getElementById('addMedErrorMsg').style.display = 'none';
  document.getElementById('addMedModal').classList.add('active');
}

function closeAddMedicineModal() {
  document.getElementById('addMedModal').classList.remove('active');
}

function saveNewMedicine(e) {
  e.preventDefault();

  const passwordInput = document.getElementById('inputPassword').value;
  if (passwordInput !== appState.securityPin) {
    document.getElementById('addMedErrorMsg').style.display = 'block';
    return;
  }

  const activePatient = getActivePatient();
  const name = document.getElementById('inputMedName').value;
  const dosage = document.getElementById('inputDosage').value;
  const form = document.getElementById('inputForm').value;
  const rawTime = document.getElementById('inputTime').value;
  const stock = parseInt(document.getElementById('inputStock').value, 10) || 30;
  const instructions = document.getElementById('inputInstructions').value || 'Take as prescribed';

  const [h, m] = rawTime.split(':');
  const hourNum = parseInt(h, 10);
  const ampm = hourNum >= 12 ? 'PM' : 'AM';
  const displayHour = hourNum % 12 || 12;
  const formattedTime = `${displayHour}:${m} ${ampm}`;

  const newMed = {
    id: `med_${Date.now()}`,
    name,
    dosage,
    form,
    time: formattedTime,
    instructions,
    stock,
    status: 'PENDING'
  };

  activePatient.medicines.unshift(newMed);
  activePatient.activityFeed.unshift({
    time: 'Just Now',
    text: `➕ Added new medication "${name} (${dosage})" to ${activePatient.patientName}'s schedule.`
  });

  persistAppState();
  renderSchedule();
  renderActivityFeed();
  closeAddMedicineModal();
  document.getElementById('medForm').reset();
  alert(`🎉 Success! New Medication "${name} (${dosage})" added for ${activePatient.patientName} & synced across devices!`);
}

function toggleSeniorHighContrast() {
  appState.highContrast = !appState.highContrast;
  document.body.classList.toggle('high-contrast', appState.highContrast);
  const badge = document.getElementById('contrastBadge');
  if (badge) {
    badge.innerText = appState.highContrast ? 'ON' : 'OFF';
    badge.classList.toggle('on', appState.highContrast);
  }
}

function toggleVoiceReadSchedule() {
  appState.voiceReadEnabled = !appState.voiceReadEnabled;
  const badge = document.getElementById('voiceBadge');

  if (badge) {
    badge.innerText = appState.voiceReadEnabled ? 'ON' : 'OFF';
    badge.classList.toggle('on', appState.voiceReadEnabled);
  }

  if (appState.voiceReadEnabled) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const activePatient = getActivePatient();
      const pendingMeds = activePatient.medicines.filter(m => m.status === 'PENDING').map(m => `${m.name} ${m.dosage} at ${m.time}`).join(', ');
      const adhPct = calculateAdherencePercentage();
      
      const speechText = `Voice Read Schedule Activated. Good morning ${activePatient.patientName}. Your primary doctor is ${activePatient.contacts.docName}. Primary caregiver is ${activePatient.contacts.cgName}. Your current adherence rate is ${adhPct} percent. You have ${pendingMeds ? 'pending medicines: ' + pendingMeds : 'no pending medicines left for today'}.`;
      
      const utterance = new SpeechSynthesisUtterance(speechText);
      utterance.rate = 0.88;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    } else {
      alert('Voice synthesis is not supported on this browser.');
    }
  } else {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }
}

function triggerEmergencySOS() {
  const activePatient = getActivePatient();
  document.getElementById('sosModal').classList.add('active');
  playAlarmChime();

  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  activePatient.activityFeed.unshift({
    time: `Today ${timeStr}`,
    text: `🚨 EMERGENCY SOS BROADCAST: SMS & Voice Alerts sent to ${activePatient.contacts.docName} & ${activePatient.contacts.cgName}`
  });
  persistAppState();
  renderActivityFeed();
}

function closeSOSModal() {
  document.getElementById('sosModal').classList.remove('active');
}

// Initialize on Load & Start Automatic Alarm Clock
document.addEventListener('DOMContentLoaded', () => {
  checkInitialSetup();
  renderAllViews();
  startAutomaticAlarmClock();
});

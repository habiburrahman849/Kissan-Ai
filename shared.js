// Kissan AI - Shared JavaScript

// ===== THEME =====
function toggleTheme() {
  const body = document.body;
  const icon = document.getElementById('themeIcon');
  const headerIcon = document.getElementById('headerThemeIcon');
  const toggle = document.getElementById('darkModeToggle');

  if (body.getAttribute('data-theme') === 'dark') {
    body.removeAttribute('data-theme');
    if (icon) icon.className = 'fas fa-moon';
    if (headerIcon) headerIcon.className = 'fas fa-moon';
    if (toggle) toggle.checked = false;
    showToast('Switched to light mode', 'success');
  } else {
    body.setAttribute('data-theme', 'dark');
    if (icon) icon.className = 'fas fa-sun';
    if (headerIcon) headerIcon.className = 'fas fa-sun';
    if (toggle) toggle.checked = true;
    showToast('Switched to dark mode', 'success');
  }
}

// ===== SIDEBAR =====
var SIDEBAR_W = 280;

function toggleSidebar() {
  var sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  if (sidebar.classList.contains('open')) {
    closeSidebar();
  } else {
    openSidebar();
  }
}

function openSidebar() {
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  var mainContent = document.getElementById('mainContent');
  var arrowIcon = document.getElementById('sidebarArrowIcon');
  if (!sidebar) return;
  // Clear any inline transform from drag
  sidebar.style.transform = '';
  sidebar.classList.add('open');
  if (overlay) overlay.classList.add('active');
  if (mainContent) mainContent.classList.remove('sidebar-closed');
  if (arrowIcon) arrowIcon.className = 'fas fa-chevron-left';
}

// Close sidebar
function closeSidebar() {
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  var mainContent = document.getElementById('mainContent');
  var arrowIcon = document.getElementById('sidebarArrowIcon');
  if (!sidebar) return;
  // Clear any inline transform from drag
  sidebar.style.transform = '';
  sidebar.classList.remove('open');
  if (overlay) overlay.classList.remove('active');
  if (mainContent) mainContent.classList.add('sidebar-closed');
  if (arrowIcon) arrowIcon.className = 'fas fa-chevron-right';
}

// ===== SIDEBAR DRAG (mouse + touch on handle) =====
(function() {
  var dragging = false;
  var startX = 0;
  var currentTranslate = -SIDEBAR_W;
  var sidebar, overlay, mainContent, handle;

  function initDrag() {
    sidebar = document.getElementById('sidebar');
    overlay = document.getElementById('sidebarOverlay');
    mainContent = document.getElementById('mainContent');
    handle = document.getElementById('sidebarDragHandle');
    if (!handle || !sidebar) return;
    // Mouse events on handle
    handle.addEventListener('mousedown', onDragStart);
    // Touch events on handle
    handle.addEventListener('touchstart', onDragStart, {passive: true});
  }

  function onDragStart(e) {
    // Don't start drag if clicking the arrow button
    var target = e.target || e.srcElement;
    if (target && target.closest && target.closest('.sidebar-arrow')) return;
    e.preventDefault && e.preventDefault();
    sidebar = sidebar || document.getElementById('sidebar');
    overlay = overlay || document.getElementById('sidebarOverlay');
    mainContent = mainContent || document.getElementById('mainContent');
    if (!sidebar) return;
    dragging = true;
    startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
    var isOpen = sidebar.classList.contains('open');
    currentTranslate = isOpen ? 0 : -SIDEBAR_W;
    sidebar.classList.add('dragging');
    document.addEventListener('mousemove', onDragMove);
    document.addEventListener('mouseup', onDragEnd);
    document.addEventListener('touchmove', onDragMove, {passive: false});
    document.addEventListener('touchend', onDragEnd);
  }

  function onDragMove(e) {
    if (!dragging || !sidebar) return;
    if (e.type === 'touchmove') e.preventDefault && e.preventDefault();
    var clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
    var diff = clientX - startX;
    var translate = currentTranslate + diff;
    // Clamp between -SIDEBAR_W and 0
    translate = Math.max(-SIDEBAR_W, Math.min(0, translate));
    sidebar.style.transform = 'translateX(' + translate + 'px)';
    // Show overlay when past halfway
    if (overlay) {
      if (translate > -SIDEBAR_W / 2) {
        overlay.classList.add('active');
      } else {
        overlay.classList.remove('active');
      }
    }
  }

  function onDragEnd(e) {
    if (!dragging || !sidebar) return;
    dragging = false;
    sidebar.classList.remove('dragging');
    var clientX = e.type === 'touchend' ? (e.changedTouches ? e.changedTouches[0].clientX : startX) : e.clientX;
    var diff = clientX - startX;
    var translate = currentTranslate + diff;
    translate = Math.max(-SIDEBAR_W, Math.min(0, translate));
    // Snap: if past 50% open, snap open; else snap closed
    sidebar.style.transform = '';
    if (translate > -SIDEBAR_W / 2) {
      openSidebar();
    } else {
      closeSidebar();
    }
    // Remove listeners
    document.removeEventListener('mousemove', onDragMove);
    document.removeEventListener('mouseup', onDragEnd);
    document.removeEventListener('touchmove', onDragMove);
    document.removeEventListener('touchend', onDragEnd);
  }

  // Init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDrag);
  } else {
    initDrag();
  }
})();

// Swipe from left screen edge to open sidebar (fallback for touch devices)
(function() {
  var touchStartX = 0;
  var touchStartY = 0;
  document.addEventListener('touchstart', function(e) {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
  }, {passive: true});
  document.addEventListener('touchend', function(e) {
    var touchEndX = e.changedTouches[0].clientX;
    var touchEndY = e.changedTouches[0].clientY;
    var diffX = touchEndX - touchStartX;
    var diffY = Math.abs(touchEndY - touchStartY);
    if (touchStartX < 20 && diffX > 60 && diffY < 80) {
      var sidebar = document.getElementById('sidebar');
      if (sidebar && !sidebar.classList.contains('open')) {
        openSidebar();
      }
    }
  }, {passive: true});
})();

// ===== CHAT =====
function handleChatInput() {
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const voiceBtn = document.getElementById('voiceBtn');
  if (input.value.trim().length > 0) { sendBtn.classList.add('show'); voiceBtn.classList.add('hide'); }
  else { sendBtn.classList.remove('show'); voiceBtn.classList.remove('hide'); }
}

function handleChatKeyPress(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChatMessage(); }
}

async function sendChatMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, true);
  input.value = '';
  handleChatInput();
  showTyping();
  try {
    const response = await fetch('/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ farmer_id: 1, message: text })
    });
    if (!response.ok) throw new Error('Chat request failed');
    const data = await response.json();
    hideTyping();
    addMessage(data.answer || 'جواب تیار نہیں ہو سکا۔ براہ کرم دوبارہ کوشش کریں۔', false);
  } catch (error) {
    hideTyping();
    addMessage('Backend سے رابطہ نہیں ہو سکا۔ براہ کرم server چلا کر دوبارہ کوشش کریں۔', false);
  }
  return;
  setTimeout(() => {
    hideTyping();
    const responses = [
      "🌾 Based on your query, I recommend checking soil moisture levels. Current conditions suggest 65% is ideal for your crops.",
      "🔍 I've analyzed your question. For best results, apply NPK fertilizer in a 20:20:20 ratio after the first monsoon shower.",
      "💰 Market update: Wheat prices are up 5% at Multan mandi. Good time to sell if your crop is ready!",
      "🌦️ Weather alert: Light showers expected tomorrow evening. Perfect for your rice transplanting schedule.",
      "🐛 Pest alert: Watch out for aphids on cotton. Spray neem oil (5ml/L) as a preventive measure."
    ];
    addMessage(responses[Math.floor(Math.random() * responses.length)], false);
  }, 1500 + Math.random() * 1000);
}

function sendSuggested(text) {
  document.getElementById('chatInput').value = text;
  handleChatInput();
  sendChatMessage();
}

function addMessage(text, isUser, isAudio, audioDuration) {
  var chatArea = document.getElementById('chatArea');
  var msg = document.createElement('div');
  msg.className = 'message ' + (isUser ? 'user' : 'bot');
  msg.setAttribute('data-sender', isUser ? 'user' : 'bot');
  var time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  var content = '';
  if (isAudio) {
    content = buildAudioPlayerHTML(audioDuration || voiceState.seconds || 5);
  } else {
    content = '<div class="message-text">' + text + '</div>';
  }
  msg.innerHTML = content + '<div class="message-reactions-container"></div><div class="message-time">' + time + (isUser ? '<i class="fas fa-check-double message-status"></i>' : '') + '</div>';
  attachMsgListeners(msg);
  chatArea.appendChild(msg);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function buildAudioPlayerHTML(durationSec) {
  var bars = '';
  var numBars = 28;
  for (var i = 0; i < numBars; i++) {
    var h = Math.floor(Math.random() * 20 + 6);
    bars += '<div class="audio-wave-bar" style="height:' + h + 'px" data-idx="' + i + '"></div>';
  }
  var dur = formatTime(durationSec);
  return '<div class="audio-message">' +
    '<button class="audio-play-btn" onclick="toggleAudioPlay(this)"><i class="fas fa-play"></i></button>' +
    '<div class="audio-waveform">' + bars + '</div>' +
    '<div class="audio-duration">' + dur + '</div>' +
    '</div>';
}

function toggleAudioPlay(btn) {
  var icon = btn.querySelector('i');
  var waveform = btn.nextElementSibling;
  var bars = waveform.querySelectorAll('.audio-wave-bar');
  if (icon.classList.contains('fa-play')) {
    icon.classList.remove('fa-play');
    icon.classList.add('fa-pause');
    var idx = 0;
    var interval = setInterval(function() {
      if (idx < bars.length) {
        bars[idx].classList.add('played');
        idx++;
      } else {
        clearInterval(interval);
        icon.classList.remove('fa-pause');
        icon.classList.add('fa-play');
        for (var j = 0; j < bars.length; j++) bars[j].classList.remove('played');
      }
    }, 100);
    btn._interval = interval;
  } else {
    icon.classList.remove('fa-pause');
    icon.classList.add('fa-play');
    clearInterval(btn._interval);
  }
}

function showTyping() { document.getElementById('typingIndicator').classList.add('active'); }
function hideTyping() { document.getElementById('typingIndicator').classList.remove('active'); }

function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    addMessage('<img src="' + e.target.result + '" class="message-image">Photo uploaded', true);
    showTyping();
    setTimeout(() => {
      hideTyping();
      addMessage('Main ne aapki tasveer dekh li hai. Crop disease detect karne ka feature jald aa raha hai. Abhi aap apni fasl ke baare mein bataein, main madad karunga.', false);
    }, 2000);
  };
  reader.readAsDataURL(file);
}

// ===== CHAT DROPDOWN MENU =====
function toggleChatMenu() {
  var dropdown = document.getElementById('chatDropdown');
  if (dropdown) dropdown.classList.toggle('active');
}
// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
  var dropdown = document.getElementById('chatDropdown');
  var btn = document.getElementById('chatMenuBtn');
  if (dropdown && btn && !btn.contains(e.target) && !dropdown.contains(e.target)) {
    dropdown.classList.remove('active');
  }
  // Close message context menu
  var ctxMenu = document.getElementById('msgContextMenu');
  if (ctxMenu && !ctxMenu.contains(e.target)) {
    ctxMenu.classList.remove('active');
  }
  // Close reaction picker
  var picker = document.getElementById('reactionPicker');
  if (picker && !picker.contains(e.target)) {
    picker.classList.remove('active');
  }
});

function clearChat() {
  var chatArea = document.getElementById('chatArea');
  if (chatArea) {
    chatArea.innerHTML = '<div class="date-separator"><span>Today</span></div>';
    addMessage('\u2705 Chat cleared. How can I help you?', false);
  }
  var dropdown = document.getElementById('chatDropdown');
  if (dropdown) dropdown.classList.remove('active');
  showToast('Chat cleared', 'success');
}

function shareChat() {
  var dropdown = document.getElementById('chatDropdown');
  if (dropdown) dropdown.classList.remove('active');
  if (navigator.share) {
    navigator.share({ title: 'Kissan AI Chat', text: 'Check out my Kissan AI conversation!', url: window.location.href });
  } else {
    navigator.clipboard.writeText(window.location.href);
    showToast('Chat link copied to clipboard!', 'success');
  }
}

function reportChat() {
  var dropdown = document.getElementById('chatDropdown');
  if (dropdown) dropdown.classList.remove('active');
  showToast('Report submitted. We will review shortly.', 'success');
}

// ===== VOICE RECORDING =====
var voiceState = { isRecording: false, isPaused: false, timer: null, seconds: 0, animFrame: null, freqBars: [] };

function startVoiceRecording() {
  var bar = document.getElementById('voiceRecordingBar');
  var inputArea = document.getElementById('chatInputArea');
  var freqContainer = document.getElementById('voiceFrequency');
  if (!bar) return;

  voiceState.isRecording = true;
  voiceState.isPaused = false;
  voiceState.seconds = 0;

  // Create frequency bars
  freqContainer.innerHTML = '';
  voiceState.freqBars = [];
  for (var i = 0; i < 32; i++) {
    var b = document.createElement('div');
    b.className = 'voice-freq-bar';
    b.style.height = '4px';
    freqContainer.appendChild(b);
    voiceState.freqBars.push(b);
  }

  // Show recording bar, hide input area
  bar.style.display = 'block';
  if (inputArea) inputArea.style.display = 'none';

  // Start timer
  updateTimerDisplay();
  voiceState.timer = setInterval(function() {
    if (!voiceState.isPaused) {
      voiceState.seconds++;
      updateTimerDisplay();
    }
  }, 1000);

  // Start frequency animation
  animateFrequency();
}

function updateTimerDisplay() {
  var el = document.getElementById('voiceTimer');
  if (!el) return;
  var m = Math.floor(voiceState.seconds / 60);
  var s = voiceState.seconds % 60;
  el.textContent = (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
}

function animateFrequency() {
  if (!voiceState.isRecording) return;
  voiceState.animFrame = requestAnimationFrame(function() {
    for (var i = 0; i < voiceState.freqBars.length; i++) {
      if (!voiceState.isPaused) {
        var h = voiceState.isPaused ? 4 : (Math.random() * 28 + 4);
        voiceState.freqBars[i].style.height = h + 'px';
        voiceState.freqBars[i].classList.toggle('active', h > 16);
      }
    }
    animateFrequency();
  });
}

function resumePauseVoice() {
  var btn = document.getElementById('voiceResumeBtn');
  if (!btn) return;
  voiceState.isPaused = !voiceState.isPaused;
  if (voiceState.isPaused) {
    btn.innerHTML = '<i class="fas fa-play"></i>';
    btn.classList.add('paused');
    // Freeze bars
    for (var i = 0; i < voiceState.freqBars.length; i++) {
      voiceState.freqBars[i].style.opacity = '0.4';
    }
  } else {
    btn.innerHTML = '<i class="fas fa-pause"></i>';
    btn.classList.remove('paused');
    for (var i = 0; i < voiceState.freqBars.length; i++) {
      voiceState.freqBars[i].style.opacity = '';
    }
  }
}

function stopVoiceRecording() {
  var bar = document.getElementById('voiceRecordingBar');
  var inputArea = document.getElementById('chatInputArea');
  var duration = voiceState.seconds;

  voiceState.isRecording = false;
  voiceState.isPaused = false;
  clearInterval(voiceState.timer);
  if (voiceState.animFrame) cancelAnimationFrame(voiceState.animFrame);

  // Hide recording bar, show input area
  if (bar) bar.style.display = 'none';
  if (inputArea) inputArea.style.display = '';

  // Add audio message to chat
  addMessage('', true, true, duration || 5);
  showToast('Voice message sent (' + formatTime(duration) + ')', 'success');
  voiceState.seconds = 0;
}

function formatTime(sec) {
  var m = Math.floor(sec / 60);
  var s = sec % 60;
  return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
}

// ===== MESSAGE CONTEXT MENU =====
var activeMsgEl = null;

function showMsgContextMenu(e, msgEl) {
  activeMsgEl = msgEl;
  var menu = document.getElementById('msgContextMenu');
  var deleteBtn = document.getElementById('deleteMsgBtn');
  if (!menu || !msgEl) return;
  // Only allow delete on own (user) messages
  var isUser = msgEl.getAttribute('data-sender') === 'user';
  if (deleteBtn) deleteBtn.style.display = isUser ? 'flex' : 'none';
  if (isUser) { deleteBtn.classList.add('danger'); }
  // Position menu
  var x = e.clientX || e.pageX || 0;
  var y = e.clientY || e.pageY || 0;
  menu.style.left = Math.min(x, window.innerWidth - 180) + 'px';
  menu.style.top = Math.min(y, window.innerHeight - 150) + 'px';
  menu.classList.add('active');
}

function hideMsgContextMenu() {
  var menu = document.getElementById('msgContextMenu');
  if (menu) menu.classList.remove('active');
}

function copyMessage() {
  hideMsgContextMenu();
  if (!activeMsgEl) return;
  var textEl = activeMsgEl.querySelector('.message-text');
  var text = textEl ? textEl.innerText : '';
  if (navigator.clipboard && text) {
    navigator.clipboard.writeText(text);
    showToast('Message copied!', 'success');
  } else {
    showToast('Nothing to copy', 'error');
  }
}

function deleteMessage() {
  hideMsgContextMenu();
  if (!activeMsgEl) return;
  if (activeMsgEl.getAttribute('data-sender') !== 'user') {
    showToast('You can only delete your own messages', 'error');
    return;
  }
  activeMsgEl.style.transition = 'all 0.3s ease';
  activeMsgEl.style.opacity = '0';
  activeMsgEl.style.transform = 'translateX(100%)';
  setTimeout(function() { activeMsgEl.remove(); }, 300);
  showToast('Message deleted', 'success');
}

function reactToMessage() {
  hideMsgContextMenu();
  if (!activeMsgEl) return;
  var picker = document.getElementById('reactionPicker');
  if (!picker) return;
  var rect = activeMsgEl.getBoundingClientRect();
  picker.style.left = Math.min(rect.left, window.innerWidth - 260) + 'px';
  picker.style.top = (rect.bottom + 4) + 'px';
  picker.classList.add('active');
}

function addReaction(emoji) {
  var picker = document.getElementById('reactionPicker');
  if (picker) picker.classList.remove('active');
  if (!activeMsgEl) return;
  var container = activeMsgEl.querySelector('.message-reactions-container');
  if (!container) return;
  // Check if reaction already exists
  var existing = container.querySelectorAll('.reaction-badge');
  var found = false;
  for (var i = 0; i < existing.length; i++) {
    if (existing[i].getAttribute('data-emoji') === emoji) {
      var countEl = existing[i].querySelector('.reaction-count');
      var count = parseInt(countEl.textContent) + 1;
      countEl.textContent = count;
      found = true;
      break;
    }
  }
  if (!found) {
    var badge = document.createElement('span');
    badge.className = 'reaction-badge';
    badge.setAttribute('data-emoji', emoji);
    badge.innerHTML = emoji + '<span class="reaction-count">1</span>';
    badge.onclick = function() {
      var c = parseInt(this.querySelector('.reaction-count').textContent);
      if (c > 1) { this.querySelector('.reaction-count').textContent = c - 1; }
      else { this.remove(); }
    };
    container.appendChild(badge);
  }
}

// ===== TOAST =====
function showToast(message, type) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = '<i class="fas fa-' + (type === 'success' ? 'check-circle' : 'exclamation-circle') + '" style="color:' + (type === 'success' ? 'var(--success)' : 'var(--error)') + ';font-size:18px"></i><span style="font-size:14px;color:var(--text-primary);font-weight:500">' + message + '</span>';
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; setTimeout(() => toast.remove(), 300); }, 3000);
}

// ===== INIT =====
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) { toggleTheme(); }

// Attach long-press handlers to existing static messages on page load
document.addEventListener('DOMContentLoaded', function() {
  var existingMsgs = document.querySelectorAll('.message:not([data-listeners])');
  for (var i = 0; i < existingMsgs.length; i++) {
    attachMsgListeners(existingMsgs[i]);
  }
});

function attachMsgListeners(msgEl) {
  if (msgEl.getAttribute('data-listeners')) return;
  msgEl.setAttribute('data-listeners', 'true');
  var pressTimer = null;
  msgEl.addEventListener('mousedown', function(e) {
    if (e.button === 2) return;
    pressTimer = setTimeout(function() { showMsgContextMenu(e, msgEl); }, 500);
  });
  msgEl.addEventListener('mouseup', function() { clearTimeout(pressTimer); });
  msgEl.addEventListener('mouseleave', function() { clearTimeout(pressTimer); });
  msgEl.addEventListener('touchstart', function(e) {
    pressTimer = setTimeout(function() { showMsgContextMenu(e.touches[0], msgEl); }, 500);
  }, {passive: true});
  msgEl.addEventListener('touchend', function() { clearTimeout(pressTimer); });
  msgEl.addEventListener('touchmove', function() { clearTimeout(pressTimer); });
  msgEl.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    showMsgContextMenu(e, msgEl);
  });
}

// ===== KISSAN AI API INTEGRATIONS =====

// Global profile cache
let currentFarmerProfile = null;

async function fetchFarmerProfile() {
  try {
    const response = await fetch('/api/farmers/me?farmer_id=1');
    if (!response.ok) throw new Error('Failed to fetch farmer profile');
    currentFarmerProfile = await response.json();
    
    // Global profile completeness enforcement
    const isLoginPage = window.location.pathname === '/' || window.location.pathname.endsWith('/index.html') || window.location.pathname.endsWith('/login.html');
    if (!currentFarmerProfile.is_complete && !isLoginPage) {
      window.location.href = 'index.html';
      return;
    }
    
    updateSidebarUI(currentFarmerProfile);
    
    // If on profile page, populate fields
    if (window.location.pathname.includes('profile.html')) {
      populateProfileFields(currentFarmerProfile);
    }
    // If on weather page, load weather using farmer district
    if (window.location.pathname.includes('weather.html')) {
      fetchWeatherForFarmer(currentFarmerProfile.district || 'Mardan');
    }
    // If on settings page, load language
    if (window.location.pathname.includes('settings.html')) {
      populateSettings(currentFarmerProfile);
    }
    return currentFarmerProfile;
  } catch (error) {
    console.error('Error fetching farmer profile:', error);
  }
}

function updateSidebarUI(profile) {
  const nameEl = document.querySelector('.user-mini-name');
  const roleEl = document.querySelector('.user-mini-role');
  if (nameEl) nameEl.textContent = profile.name || 'Demo Farmer';
  if (roleEl) roleEl.textContent = (profile.farming_type || 'Premium') + ' Farmer';
}

function populateProfileFields(profile) {
  // Update header summary card
  const profNameEl = document.querySelector('.profile-name');
  const profLocEl = document.querySelector('.profile-location');
  const avatarImg = document.querySelector('.profile-avatar-large');
  if (profNameEl) profNameEl.textContent = profile.name || '';
  if (avatarImg) avatarImg.alt = profile.name || 'Farmer';
  if (profLocEl) {
    const locText = (profile.village && profile.district)
      ? `Village ${profile.village}, District ${profile.district}`
      : (profile.district || profile.village || '');
    profLocEl.innerHTML = `<i class="fas fa-map-marker-alt"></i>${locText}`;
  }

  // Views
  const personalRows = document.querySelectorAll('#personalView .info-row .info-value');
  if (personalRows.length >= 4) {
    personalRows[0].textContent = profile.name || '';
    personalRows[1].textContent = profile.phone || '';
    personalRows[2].textContent = profile.email || '';
    personalRows[3].textContent = (profile.village && profile.district) 
      ? `${profile.village}, ${profile.district}` 
      : (profile.district || profile.village || '');
  }

  const farmRows = document.querySelectorAll('#farmView .info-row .info-value');
  if (farmRows.length >= 5) {
    farmRows[0].textContent = profile.land_size || '';
    farmRows[1].textContent = profile.primary_crops || '';
    farmRows[2].textContent = profile.soil_type || '';
    farmRows[3].textContent = profile.irrigation || '';
    farmRows[4].textContent = profile.farming_type || '';
  }

  // Inputs
  const nameInput = document.getElementById('personalName');
  const phoneInput = document.getElementById('personalPhone');
  const emailInput = document.getElementById('personalEmail');
  const locInput = document.getElementById('personalLocation');
  if (nameInput) nameInput.value = profile.name || '';
  if (phoneInput) phoneInput.value = profile.phone || '';
  if (emailInput) emailInput.value = profile.email || '';
  if (locInput) locInput.value = (profile.village && profile.district) 
    ? `${profile.village}, ${profile.district}` 
    : (profile.district || profile.village || '');

  const landInput = document.getElementById('farmLandSize');
  const cropsInput = document.getElementById('farmCrops');
  const soilInput = document.getElementById('farmSoil');
  const irrSelect = document.getElementById('farmIrrigation');
  const typeSelect = document.getElementById('farmType');
  if (landInput) landInput.value = profile.land_size || '';
  if (cropsInput) cropsInput.value = profile.primary_crops || '';
  if (soilInput) soilInput.value = profile.soil_type || '';
  if (irrSelect) irrSelect.value = profile.irrigation || 'Drip System';
  if (typeSelect) typeSelect.value = profile.farming_type || 'Organic';
}

async function saveFarmerProfile(type) {
  let payload = {};
  if (type === 'personal') {
    const name = document.getElementById('personalName').value;
    const phone = document.getElementById('personalPhone').value;
    const email = document.getElementById('personalEmail').value;
    const location = document.getElementById('personalLocation').value;
    
    // Parse location into village and district
    let village = '';
    let district = '';
    if (location.includes(',')) {
      const parts = location.split(',');
      village = parts[0].trim();
      district = parts[1].trim();
    } else {
      district = location.trim();
    }

    payload = { name, phone, email, village, district };
  } else if (type === 'farm') {
    const land_size = document.getElementById('farmLandSize').value;
    const primary_crops = document.getElementById('farmCrops').value;
    const soil_type = document.getElementById('farmSoil').value;
    const irrigation = document.getElementById('farmIrrigation').value;
    const farming_type = document.getElementById('farmType').value;

    payload = { land_size, primary_crops, soil_type, irrigation, farming_type };
  }

  try {
    const response = await fetch('/api/farmers/me?farmer_id=1', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('Failed to update profile');
    const updated = await response.json();
    currentFarmerProfile = updated;
    updateSidebarUI(updated);
    populateProfileFields(updated);
    showToast(type === 'personal' ? 'Personal information saved!' : 'Farm details saved!', 'success');
  } catch (error) {
    console.error('Error saving profile:', error);
    showToast('Failed to save profile on backend', 'error');
  }
}

async function fetchChatHistory() {
  const chatArea = document.getElementById('chatArea');
  if (!chatArea) return;

  try {
    const response = await fetch('/api/chat/history?farmer_id=1');
    if (!response.ok) throw new Error('Failed to fetch chat history');
    const messages = await response.json();
    
    if (messages.length > 0) {
      // Clear default messages and populate history
      chatArea.innerHTML = '<div class="date-separator"><span>Today</span></div>';
      messages.forEach(msg => {
        addMessage(msg.content, msg.role === 'user', false);
      });
    }
  } catch (error) {
    console.error('Error loading chat history:', error);
  }
}

async function fetchWeatherForFarmer(city) {
  try {
    const response = await fetch(`/api/weather/current?city=${encodeURIComponent(city)}`);
    if (!response.ok) throw new Error('Failed to fetch weather');
    const data = await response.json();
    updateWeatherUI(data);
  } catch (error) {
    console.error('Error fetching weather:', error);
  }
}

function updateWeatherUI(data) {
  const tempEl = document.querySelector('.weather-temp');
  const condEl = document.querySelector('.weather-condition');
  const locEl = document.querySelector('.weather-location');
  const iconParent = document.querySelector('.weather-main div:first-child');
  
  if (tempEl) tempEl.textContent = `${data.temperature}°C`;
  if (condEl) condEl.textContent = data.condition;
  if (locEl) locEl.innerHTML = `<i class="fas fa-map-marker-alt"></i>${data.location}`;
  
  if (iconParent && data.icon) {
    iconParent.innerHTML = `<img src="https://openweathermap.org/img/wn/${data.icon}@2x.png" style="width:64px;height:64px;">`;
  }

  const detailValues = document.querySelectorAll('.weather-detail-value');
  if (detailValues.length >= 4) {
    detailValues[0].textContent = `${data.humidity}%`;
    detailValues[1].textContent = `${data.wind_kmh}km/h`;
    detailValues[2].textContent = `${data.rain_mm}mm`;
    detailValues[3].textContent = `${data.pressure}hPa`;
  }

  const forecastGrid = document.querySelector('.forecast-grid');
  if (forecastGrid && data.forecast) {
    forecastGrid.innerHTML = '';
    data.forecast.forEach(day => {
      const card = document.createElement('div');
      card.className = 'forecast-card';
      
      let iconHtml = '☀️';
      if (day.icon) {
        iconHtml = `<img src="https://openweathermap.org/img/wn/${day.icon}.png" style="width:36px;height:36px;">`;
      }
      
      card.innerHTML = `
        <div class="forecast-day">${day.day}</div>
        <div class="forecast-icon" style="height:36px;display:flex;align-items:center;justify-content:center;">${iconHtml}</div>
        <div class="forecast-temp">${day.temp}°</div>
        <div class="forecast-range">${day.min}° / ${day.max}°</div>
        <div class="forecast-rain"><i class="fas fa-tint"></i>${day.rain_percent}%</div>
      `;
      forecastGrid.appendChild(card);
    });
  }

  const advisoryList = document.querySelector('.advisory-list');
  if (advisoryList && data.advisories) {
    advisoryList.innerHTML = '';
    data.advisories.forEach(adv => {
      const card = document.createElement('div');
      card.className = 'advisory-card';
      
      let iconClass = 'fa-leaf';
      if (adv.type === 'water') iconClass = 'fa-tint';
      if (adv.type === 'spray') iconClass = 'fa-exclamation-triangle';
      if (adv.type === 'disease') iconClass = 'fa-bug';
      
      card.innerHTML = `
        <div class="advisory-icon ${adv.tone}"><i class="fas ${iconClass}"></i></div>
        <div class="advisory-content">
          <div class="advisory-title">${adv.title}</div>
          <div class="advisory-text">${adv.text}</div>
          <div class="advisory-time">Updated recently</div>
        </div>
      `;
      advisoryList.appendChild(card);
    });
  }
}

function populateSettings(profile) {
  const selects = document.querySelectorAll('.setting-row select');
  if (selects.length > 0) {
    const langSelect = selects[0];
    if (profile.preferred_language === 'ur') langSelect.value = 'Urdu';
    else if (profile.preferred_language === 'hinglish') langSelect.value = 'Hinglish';
    else langSelect.value = 'English';
  }
}

async function saveLanguagePreference(lang) {
  let code = 'en';
  if (lang === 'Urdu') code = 'ur';
  else if (lang === 'Hinglish') code = 'hinglish';
  
  try {
    const response = await fetch('/api/farmers/me?farmer_id=1', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preferred_language: code })
    });
    if (response.ok) {
      showToast(`Language preference saved: ${lang}`, 'success');
    }
  } catch (error) {
    console.error('Error saving language:', error);
  }
}

// Auto-run on load
window.addEventListener('DOMContentLoaded', () => {
  fetchFarmerProfile();
  if (window.location.pathname.includes('chat.html')) {
    fetchChatHistory();
  }
});

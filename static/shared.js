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
  sidebar.style.transform = '';
  sidebar.classList.add('open');
  if (overlay) overlay.classList.add('active');
  if (mainContent) mainContent.classList.remove('sidebar-closed');
  if (arrowIcon) arrowIcon.className = 'fas fa-chevron-left';
}

function closeSidebar() {
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  var mainContent = document.getElementById('mainContent');
  var arrowIcon = document.getElementById('sidebarArrowIcon');
  if (!sidebar) return;
  sidebar.style.transform = '';
  sidebar.classList.remove('open');
  if (overlay) overlay.classList.remove('active');
  if (mainContent) mainContent.classList.add('sidebar-closed');
  if (arrowIcon) arrowIcon.className = 'fas fa-chevron-right';
}

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type) {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.style.cssText = 'display:flex;align-items:center;gap:10px;padding:12px 18px;background:rgba(30,41,59,0.9);border:1px solid rgba(255,255,255,0.1);border-radius:14px;backdrop-filter:blur(10px);box-shadow:0 10px 25px rgba(0,0,0,0.4);margin-top:8px;transition:all 0.3s ease;';
  
  const iconClass = type === 'success' ? 'check-circle' : 'exclamation-circle';
  const iconColor = type === 'success' ? '#37d366' : '#ef4444';
  toast.innerHTML = '<i class="fas fa-' + iconClass + '" style="color:' + iconColor + ';font-size:18px"></i><span style="font-size:13px;color:#ffffff;font-weight:500">' + message + '</span>';
  
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ===== CHAT FUNCTIONALITY =====
function handleChatInput() {
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const voiceBtn = document.getElementById('voiceBtn');
  if (!input) return;
  if (input.value.trim().length > 0) {
    if (sendBtn) sendBtn.classList.add('show');
    if (voiceBtn) voiceBtn.classList.add('hide');
  } else {
    if (sendBtn) sendBtn.classList.remove('show');
    if (voiceBtn) voiceBtn.classList.remove('hide');
  }
}

function handleChatKeyPress(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSendChatMessage(); }
}

async function sendChatMessage() {
  const input = document.getElementById('chatInput');
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, true);
  input.value = '';
  handleChatInput();
  showTyping();

  try {
    // Qwen + RAG can take 15–60s on free tiers — do not use the 5s default
    const response = await apiFetch('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({
        message: text,
        user_id: getStoredUserId(),
        session_id: 'default_session'
      })
    }, 1, 90000);
    if (!response || !response.ok) throw new Error('Chat failed');
    const data = await response.json();
    hideTyping();
    addMessage(data.response || 'No response generated.', false, false, 0, null, data.agents_used);
  } catch (error) {
    hideTyping();
    addMessage('Unable to connect to assistant. Offline safety fallback active.', false);
  }
}

function sendSuggested(text) {
  const input = document.getElementById('chatInput');
  if (!input) return;
  input.value = text;
  handleChatInput();
  onSendChatMessage();
}

function addMessage(text, isUser, isAudio, audioDuration, citations, agentsUsed) {
  var chatArea = document.getElementById('chatArea');
  if (!chatArea) return;
  var msg = document.createElement('div');
  msg.className = 'message ' + (isUser ? 'user' : 'bot');
  var time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  var content = '<div class="message-text">' + text + '</div>';

  var agentsHtml = '';
  if (!isUser && agentsUsed && agentsUsed.length > 0) {
    agentsHtml = '<div style="font-size:10px;color:var(--text-muted);margin-top:4px;display:flex;align-items:center;gap:4px;">' +
      '<i class="fas fa-network-wired"></i> Agents: ' + agentsUsed.join(', ') +
    '</div>';
  }

  msg.innerHTML = content + agentsHtml + '<div class="message-reactions-container"></div><div class="message-time">' + time + (isUser ? '<i class="fas fa-check-double message-status"></i>' : '') + '</div>';
  chatArea.appendChild(msg);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function showTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.classList.add('active');
}

function hideTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.classList.remove('active');
}

// ===== KISSAN AI AUTH & API INTEGRATIONS =====
const AUTH_TOKEN_KEY = 'kissan_access_token';
const AUTH_FARMER_KEY = 'kissan_farmer';
const AUTH_USER_ID_KEY = 'kissan_user_id';
const DEFAULT_AVATAR = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face';

function hostIsLocal() {
  const host = window.location.hostname;
  return window.location.protocol === 'file:' || host === 'localhost' || host === '127.0.0.1';
}

function getApiBaseUrl() {
  // Local static open (file://) or pure localhost frontend → hit local FastAPI
  if (hostIsLocal()) {
    return 'http://127.0.0.1:8000';
  }
  // Production (Render etc.): same-origin — frontend is served by FastAPI
  return '';
}

function isLoginPage() {
  const path = window.location.pathname || '';
  return path === '/' || path.endsWith('/') || path.endsWith('/index.html') || path.endsWith('/login.html');
}

function getAccessToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY) || '';
}

function getStoredUserId() {
  return localStorage.getItem(AUTH_USER_ID_KEY) || '';
}

function getStoredFarmer() {
  try {
    return JSON.parse(localStorage.getItem(AUTH_FARMER_KEY) || 'null');
  } catch (e) {
    return null;
  }
}

function setAuthSession(accessToken, farmer, userId) {
  if (accessToken) localStorage.setItem(AUTH_TOKEN_KEY, accessToken);
  if (farmer) localStorage.setItem(AUTH_FARMER_KEY, JSON.stringify(farmer));
  if (userId) localStorage.setItem(AUTH_USER_ID_KEY, String(userId));
}

function clearAuthSession() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_FARMER_KEY);
  localStorage.removeItem(AUTH_USER_ID_KEY);
}

function authHeaders(extra) {
  const headers = Object.assign({ 'Content-Type': 'application/json' }, extra || {});
  const token = getAccessToken();
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

async function apiFetch(url, options, retries = 2, timeoutMs = 5000) {
  options = options || {};
  const fullUrl = url.startsWith('/') ? getApiBaseUrl() + url : url;
  const headers = authHeaders(options.headers || {});

  for (let attempt = 1; attempt <= retries + 1; attempt++) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(fullUrl, Object.assign({}, options, {
        headers: headers,
        signal: controller.signal
      }));
      clearTimeout(timeoutId);

      if (response.status === 401 && !isLoginPage()) {
        clearAuthSession();
        window.location.href = 'index.html';
      }
      return response;
    } catch (err) {
      clearTimeout(timeoutId);
      console.warn(`[apiFetch] Attempt ${attempt}/${retries + 1} failed for ${url}:`, err);

      if (attempt <= retries) {
        await new Promise(res => setTimeout(res, attempt * 500));
      } else {
        console.error('[apiFetch] All retries exhausted:', fullUrl);
        const isLocal = hostIsLocal();
        showToast(
          isLocal
            ? 'Please start backend: cd backend && uvicorn app.main:app --reload --port 8000'
            : 'Server is waking up or unreachable. Retry in a few seconds.',
          'error'
        );
        throw err;
      }
    }
  }
}

function updateSidebarUI(profile) {
  if (!profile) return;
  const nameEl = document.querySelector('.user-mini-name');
  const roleEl = document.querySelector('.user-mini-role');
  const avatarEl = document.querySelector('.user-mini img');
  if (nameEl) nameEl.textContent = profile.full_name || (profile.is_guest ? 'Guest Farmer' : 'Farmer');
  if (roleEl) {
    if (profile.is_guest) roleEl.textContent = 'Guest Mode';
    else roleEl.textContent = 'Registered Farmer';
  }
  if (avatarEl) {
    avatarEl.src = DEFAULT_AVATAR;
  }
}

async function fetchFarmerProfile() {
  let token = getAccessToken();
  if (!token && !isLoginPage()) {
    try {
      const res = await apiFetch('/api/auth/guest', { method: 'POST' });
      if (res && res.ok) {
        const data = await res.json();
        setAuthSession(data.access_token, { user_id: data.user_id, is_guest: true, full_name: 'Guest Farmer' }, data.user_id);
        token = data.access_token;
      }
    } catch (e) {
      console.warn('Auto guest bootstrap warning:', e);
      setAuthSession('guest_dev_token', { user_id: 'guest_dev', is_guest: true, full_name: 'Guest Farmer' }, 'guest_dev');
      token = 'guest_dev_token';
    }
  }

  if (!token) return null;

  try {
    const response = await apiFetch('/api/auth/me');
    if (!response || !response.ok) throw new Error('Failed to fetch profile');
    const profile = await response.json();
    localStorage.setItem(AUTH_FARMER_KEY, JSON.stringify(profile));
    updateSidebarUI(profile);
    return profile;
  } catch (error) {
    console.error('Error fetching farmer profile:', error);
    const cached = getStoredFarmer();
    if (cached) updateSidebarUI(cached);
  }
}

window.addEventListener('DOMContentLoaded', function() {
  if (isLoginPage()) return;
  fetchFarmerProfile();
});

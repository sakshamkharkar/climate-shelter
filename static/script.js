/**
 * Antigravity AI Chatbot Frontend JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- State Variables ---
    let currentConvId = null;
    let currentPersona = 'general';
    let conversations = [];
    let settings = JSON.parse(localStorage.getItem('ai_bot_settings')) || {
        provider: 'builtin',
        apiKey: '',
        model: '',
        endpoint: 'http://localhost:11434'
    };

    // --- DOM Elements ---
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const conversationsList = document.getElementById('conversations-list');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const openSettingsBtn = document.getElementById('open-settings-btn');
    
    const chatTitle = document.getElementById('chat-title');
    const personaSelect = document.getElementById('persona-select');
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    
    const chatMessages = document.getElementById('chat-messages');
    const welcomeBanner = document.getElementById('welcome-banner');
    const typingIndicator = document.getElementById('typing-indicator');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    
    const settingsModal = document.getElementById('settings-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const cancelSettingsBtn = document.getElementById('cancel-settings-btn');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const providerSelect = document.getElementById('provider-select');
    const apiKeyInput = document.getElementById('api-key-input');
    const modelNameInput = document.getElementById('model-name-input');
    const endpointInput = document.getElementById('endpoint-input');
    const apiKeyGroup = document.getElementById('api-key-group');
    const modelGroup = document.getElementById('model-group');
    const endpointGroup = document.getElementById('endpoint-group');

    // --- Theme Init ---
    const savedTheme = localStorage.getItem('ai_bot_theme') || 'dark';
    setTheme(savedTheme);

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('ai_bot_theme', theme);
        if (theme === 'dark') {
            themeIcon.className = 'fa-solid fa-moon';
        } else {
            themeIcon.className = 'fa-solid fa-sun';
        }
    }

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });

    // --- Sidebar & Mobile Drawer ---
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.add('open');
        sidebarOverlay.classList.add('open');
    });

    const closeSidebar = () => {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
    };

    closeSidebarBtn.addEventListener('click', closeSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);

    // --- Settings Modal ---
    function updateSettingsFields() {
        const provider = providerSelect.value;
        if (provider === 'builtin') {
            apiKeyGroup.classList.add('hidden');
            modelGroup.classList.add('hidden');
            endpointGroup.classList.add('hidden');
        } else if (provider === 'gemini' || provider === 'openai') {
            apiKeyGroup.classList.remove('hidden');
            modelGroup.classList.remove('hidden');
            endpointGroup.classList.add('hidden');
        } else if (provider === 'ollama') {
            apiKeyGroup.classList.add('hidden');
            modelGroup.classList.remove('hidden');
            endpointGroup.classList.remove('hidden');
        }
    }

    providerSelect.addEventListener('change', updateSettingsFields);

    openSettingsBtn.addEventListener('click', () => {
        providerSelect.value = settings.provider || 'builtin';
        apiKeyInput.value = settings.apiKey || '';
        modelNameInput.value = settings.model || '';
        endpointInput.value = settings.endpoint || 'http://localhost:11434';
        updateSettingsFields();
        settingsModal.classList.remove('hidden');
    });

    const closeSettings = () => settingsModal.classList.add('hidden');
    closeModalBtn.addEventListener('click', closeSettings);
    cancelSettingsBtn.addEventListener('click', closeSettings);

    saveSettingsBtn.addEventListener('click', () => {
        settings = {
            provider: providerSelect.value,
            apiKey: apiKeyInput.value.trim(),
            model: modelNameInput.value.trim(),
            endpoint: endpointInput.value.trim()
        };
        localStorage.setItem('ai_bot_settings', JSON.stringify(settings));
        closeSettings();
        alert('Settings saved successfully!');
    });

    // --- Auto-resize Textarea ---
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
    });

    // --- Persona Selector ---
    personaSelect.addEventListener('change', (e) => {
        currentPersona = e.target.value;
    });

    // --- Load Conversations List ---
    async function loadConversations() {
        try {
            const res = await fetch('/api/conversations');
            const data = await res.json();
            conversations = data.conversations || [];
            renderConversationsList();
        } catch (err) {
            console.error('Error fetching conversations:', err);
        }
    }

    function renderConversationsList() {
        conversationsList.innerHTML = '';
        if (conversations.length === 0) {
            conversationsList.innerHTML = '<div style="padding: 10px; color: var(--text-muted); font-size: 0.85rem; text-align: center;">No past conversations</div>';
            return;
        }

        conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = `conv-item ${conv.id === currentConvId ? 'active' : ''}`;
            item.innerHTML = `
                <div class="conv-info">
                    <i class="fa-regular fa-message"></i>
                    <span class="conv-title">${escapeHtml(conv.title)}</span>
                </div>
                <button class="delete-conv-btn" title="Delete Chat" data-id="${conv.id}">
                    <i class="fa-solid fa-trash"></i>
                </button>
            `;

            item.addEventListener('click', (e) => {
                if (e.target.closest('.delete-conv-btn')) return;
                switchConversation(conv.id, conv.title);
                closeSidebar();
            });

            const delBtn = item.querySelector('.delete-conv-btn');
            delBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                if (confirm(`Delete conversation "${conv.title}"?`)) {
                    await deleteConversation(conv.id);
                }
            });

            conversationsList.appendChild(item);
        });
    }

    // --- Switch Conversation ---
    async function switchConversation(id, title) {
        currentConvId = id;
        chatTitle.textContent = title || 'Chat';
        renderConversationsList();

        try {
            const res = await fetch(`/api/conversations/${id}`);
            const data = await res.json();
            renderMessages(data.messages || []);
        } catch (err) {
            console.error('Error loading conversation messages:', err);
        }
    }

    // --- Delete Conversation ---
    async function deleteConversation(id) {
        try {
            await fetch(`/api/conversations/${id}`, { method: 'DELETE' });
            if (currentConvId === id) {
                startNewChat();
            } else {
                await loadConversations();
            }
        } catch (err) {
            console.error('Error deleting conversation:', err);
        }
    }

    // --- Clear All History ---
    clearHistoryBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to delete ALL chat history?')) {
            for (const conv of conversations) {
                await fetch(`/api/conversations/${conv.id}`, { method: 'DELETE' });
            }
            startNewChat();
        }
    });

    // --- Start New Chat ---
    function startNewChat() {
        currentConvId = null;
        chatTitle.textContent = 'New Chat';
        chatMessages.innerHTML = '';
        chatMessages.appendChild(welcomeBanner);
        welcomeBanner.classList.remove('hidden');
        loadConversations();
    }

    newChatBtn.addEventListener('click', () => {
        startNewChat();
        closeSidebar();
    });

    // --- Render Messages ---
    function renderMessages(messages) {
        chatMessages.innerHTML = '';
        if (messages.length === 0) {
            chatMessages.appendChild(welcomeBanner);
            welcomeBanner.classList.remove('hidden');
            return;
        }
        welcomeBanner.classList.add('hidden');

        messages.forEach(msg => {
            appendMessageUI(msg.sender, msg.text, msg.timestamp, false);
        });

        scrollToBottom();
    }

    // --- Append Single Message to UI ---
    function appendMessageUI(sender, text, timeStr, animate = false) {
        welcomeBanner.classList.add('hidden');

        const row = document.createElement('div');
        row.className = `msg-row ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

        const content = document.createElement('div');
        content.className = 'msg-content';

        const bubble = document.createElement('div');
        bubble.className = 'msg-bubble';

        if (animate && sender === 'bot') {
            bubble.innerHTML = '';
            content.appendChild(bubble);
            row.appendChild(avatar);
            row.appendChild(content);
            chatMessages.appendChild(row);
            typeWriterEffect(bubble, text, timeStr, content);
            return;
        }

        bubble.innerHTML = formatMarkdown(text);

        const time = document.createElement('div');
        time.className = 'msg-time';
        time.textContent = timeStr || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        content.appendChild(bubble);
        content.appendChild(time);

        row.appendChild(avatar);
        row.appendChild(content);

        chatMessages.appendChild(row);
        scrollToBottom();
        attachCopyEvents();
    }

    // --- Typewriter Streaming Effect ---
    function typeWriterEffect(bubbleElem, text, timeStr, contentContainer) {
        let index = 0;
        const formattedFull = formatMarkdown(text);
        
        // Render formatted text progressively
        const interval = setInterval(() => {
            index += 3;
            if (index >= text.length) {
                bubbleElem.innerHTML = formattedFull;
                clearInterval(interval);
                
                const time = document.createElement('div');
                time.className = 'msg-time';
                time.textContent = timeStr || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                contentContainer.appendChild(time);
                
                scrollToBottom();
                attachCopyEvents();
            } else {
                bubbleElem.innerHTML = formatMarkdown(text.slice(0, index)) + '<span class="cursor">|</span>';
                scrollToBottom();
            }
        }, 15);
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- Handle Sending Message ---
    async function handleSend() {
        const text = userInput.value.trim();
        if (!text) return;

        userInput.value = '';
        userInput.style.height = 'auto';

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        appendMessageUI('user', text, timeStr, false);

        // Show typing indicator
        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: currentConvId,
                    message: text,
                    persona: currentPersona,
                    provider: settings.provider,
                    api_key: settings.apiKey,
                    model: settings.model,
                    endpoint: settings.endpoint
                })
            });

            const data = await response.json();
            typingIndicator.classList.add('hidden');

            if (data.error) {
                appendMessageUI('bot', `⚠️ **Error:** ${data.error}`, timeStr, false);
            } else {
                if (!currentConvId) {
                    currentConvId = data.conversation_id;
                    await loadConversations();
                }
                appendMessageUI('bot', data.reply, data.timestamp, true);
            }
        } catch (err) {
            typingIndicator.classList.add('hidden');
            appendMessageUI('bot', '❌ **Network Error:** Could not connect to chatbot backend server.', timeStr, false);
            console.error('Send message error:', err);
        }
    }

    sendBtn.addEventListener('click', handleSend);

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    // --- Chips Suggestion Click ---
    document.querySelectorAll('.chip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const promptText = btn.getAttribute('data-prompt');
            if (promptText) {
                userInput.value = promptText;
                handleSend();
            }
        });
    });

    // --- Markdown Formatter & Code Highlight Parser ---
    function formatMarkdown(str) {
        if (!str) return '';

        // Code block replacement ```lang ... ```
        let html = str.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
            const language = lang || 'code';
            return `
                <div class="code-block">
                    <div class="code-header">
                        <span>${escapeHtml(language)}</span>
                        <button class="copy-btn"><i class="fa-regular fa-copy"></i> Copy</button>
                    </div>
                    <pre><code>${escapeHtml(code.trim())}</code></pre>
                </div>
            `;
        });

        // Inline code `code`
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Bold **text**
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

        // Italic *text*
        html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

        // Line breaks to <br> outside code blocks
        html = html.replace(/\n/g, '<br>');

        return html;
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function attachCopyEvents() {
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.onclick = () => {
                const codeBlock = btn.closest('.code-block').querySelector('code').innerText;
                navigator.clipboard.writeText(codeBlock).then(() => {
                    btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
                    setTimeout(() => {
                        btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
                    }, 2000);
                });
            };
        });
    }

    // --- Initial Load ---
    loadConversations();
});

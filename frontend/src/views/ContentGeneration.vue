<template>
  <div class="generate-page">
    <!-- Template Header -->
    <div class="template-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回
        </button>
        <div class="template-info">
          <div class="template-icon">{{ currentTemplate.icon }}</div>
          <div>
            <h1 class="template-name">{{ currentTemplate.name }}</h1>
            <p class="template-category">{{ currentTemplate.category }}</p>
          </div>
        </div>
        <div class="header-actions">
          <button class="action-btn" @click="showSettings = !showSettings">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6m0 6v6M1 12h6m6 0h6"/>
            </svg>
          </button>
          <button class="action-btn" @click="shareTemplate">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="18" cy="5" r="3"/>
              <circle cx="6" cy="12" r="3"/>
              <circle cx="18" cy="19" r="3"/>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="content-layout">
      <!-- Sidebar -->
      <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline :points="sidebarCollapsed ? '15 18 9 12 15 6' : '9 18 15 12 9 6'"/>
          </svg>
        </button>

        <div class="sidebar-content" v-if="!sidebarCollapsed">
          <div class="session-header">
            <h3>对话历史</h3>
            <button class="new-session-btn" @click="createNewSession">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
          </div>

          <div class="session-list">
            <div
              v-for="session in sessions"
              :key="session.id"
              :class="['session-item', { active: currentSessionId === session.id }]"
              @click="switchSession(session.id)"
            >
              <div class="session-info">
                <span class="session-title">{{ session.title }}</span>
                <span class="session-time">{{ formatTime(session.time) }}</span>
              </div>
              <button class="delete-session-btn" @click.stop="deleteSession(session.id)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </aside>

      <!-- Chat Area -->
      <main class="chat-container">
        <div class="chat-wrapper">
          <!-- Empty State -->
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">{{ currentTemplate.icon }}</div>
            <h2>开始使用 {{ currentTemplate.name }}</h2>
            <p>{{ currentTemplate.description }}</p>

            <div class="suggestions">
              <div class="suggestions-title">试试这些问题：</div>
              <div class="suggestion-grid">
                <button
                  v-for="(suggestion, index) in suggestions"
                  :key="index"
                  class="suggestion-card"
                  @click="sendSuggestion(suggestion)"
                >
                  <span class="suggestion-icon">{{ suggestion.icon }}</span>
                  <span class="suggestion-text">{{ suggestion.text }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Messages -->
          <div v-else class="messages-container" ref="messagesContainer">
            <div
              v-for="(message, index) in messages"
              :key="index"
              :class="['message-group', message.role]"
            >
              <div class="message-avatar">
                <div v-if="message.role === 'user'" class="avatar user-avatar">U</div>
                <div v-else class="avatar ai-avatar">{{ currentTemplate.icon }}</div>
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-author">{{ message.role === 'user' ? '你' : currentTemplate.name }}</span>
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                </div>
                <div class="message-body">
                  <div v-if="message.role === 'assistant' && message.loading" class="loading-indicator">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                  </div>
                  <div v-else class="message-text" v-html="formatMessage(message.content)"></div>

                  <!-- Message Actions -->
                  <div v-if="message.role === 'assistant' && !message.loading" class="message-actions">
                    <button class="action-icon" @click="copyMessage(message.content)" title="复制">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                      </svg>
                    </button>
                    <button class="action-icon" @click="regenerateMessage(index)" title="重新生成">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <polyline points="23 4 23 10 17 10"/>
                        <polyline points="1 20 1 14 7 14"/>
                        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                      </svg>
                    </button>
                    <button class="action-icon" @click="likeMessage(index)" :class="{ liked: message.liked }" title="有用">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="input-container">
          <div class="input-wrapper">
            <textarea
              v-model="inputMessage"
              ref="inputTextarea"
              placeholder="输入消息..."
              class="message-input"
              rows="1"
              @keydown.enter.exact="handleEnterKey"
              @input="adjustTextareaHeight"
            ></textarea>
            <div class="input-actions">
              <button class="input-action-btn" @click="attachFile" title="附件">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
                </svg>
              </button>
              <button
                class="send-btn"
                :disabled="!inputMessage.trim() || isGenerating"
                @click="sendMessage"
              >
                <svg v-if="!isGenerating" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
                <span v-else class="loading-spinner"></span>
              </button>
            </div>
          </div>
          <div class="input-hint">
            <span>Shift + Enter 换行</span>
            <span class="divider">•</span>
            <span>{{ inputMessage.length }} / 2000</span>
          </div>
        </div>
      </main>

      <!-- Settings Panel -->
      <transition name="slide-left">
        <aside v-if="showSettings" class="settings-panel">
          <div class="settings-header">
            <h3>参数设置</h3>
            <button class="close-btn" @click="showSettings = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <div class="settings-body">
            <div class="setting-group">
              <label class="setting-label">
                温度 (Temperature)
                <span class="setting-value">{{ settings.temperature }}</span>
              </label>
              <input
                type="range"
                v-model.number="settings.temperature"
                min="0"
                max="2"
                step="0.1"
                class="setting-slider"
              />
              <p class="setting-hint">控制输出的随机性，值越高越有创造性</p>
            </div>

            <div class="setting-group">
              <label class="setting-label">
                最大长度 (Max Tokens)
                <span class="setting-value">{{ settings.maxTokens }}</span>
              </label>
              <input
                type="range"
                v-model.number="settings.maxTokens"
                min="256"
                max="4096"
                step="256"
                class="setting-slider"
              />
              <p class="setting-hint">生成内容的最大长度</p>
            </div>

            <div class="setting-group">
              <label class="setting-label">
                Top P
                <span class="setting-value">{{ settings.topP }}</span>
              </label>
              <input
                type="range"
                v-model.number="settings.topP"
                min="0"
                max="1"
                step="0.05"
                class="setting-slider"
              />
              <p class="setting-hint">核采样参数，控制多样性</p>
            </div>

            <div class="setting-group">
              <label class="setting-label">
                上下文记忆
                <span class="setting-value">{{ settings.contextLength }} 条</span>
              </label>
              <input
                type="range"
                v-model.number="settings.contextLength"
                min="0"
                max="20"
                step="1"
                class="setting-slider"
              />
              <p class="setting-hint">保留的历史对话轮数</p>
            </div>

            <div class="setting-group">
              <label class="setting-checkbox">
                <input type="checkbox" v-model="settings.streaming" />
                <span>流式输出</span>
              </label>
              <p class="setting-hint">实时显示生成内容</p>
            </div>

            <button class="reset-settings-btn" @click="resetSettings">
              恢复默认设置
            </button>
          </div>
        </aside>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const inputMessage = ref('');
const inputTextarea = ref(null);
const messagesContainer = ref(null);
const isGenerating = ref(false);
const sidebarCollapsed = ref(false);
const showSettings = ref(false);
const currentSessionId = ref(1);

const messages = ref([]);

const sessions = ref([
  { id: 1, title: '新对话', time: Date.now() },
]);

const settings = ref({
  temperature: 0.7,
  maxTokens: 2048,
  topP: 0.9,
  contextLength: 10,
  streaming: true
});

// Mock template data - in real app this would come from API
const templates = {
  1: {
    id: 1,
    name: '知识库问答助手',
    description: '基于企业文档和知识库，提供准确的问答服务',
    category: '知识问答',
    icon: '📚'
  },
  2: {
    id: 2,
    name: '营销文案生成器',
    description: '自动生成各类营销文案，包括社交媒体、广告语、产品描述等',
    category: '内容生成',
    icon: '✍️'
  }
};

const currentTemplate = computed(() => {
  const templateId = route.query.templateId || '1';
  return templates[templateId] || templates[1];
});

const suggestions = computed(() => {
  // Different suggestions based on template type
  const suggestionsByTemplate = {
    1: [
      { icon: '💡', text: '如何使用这个产品？' },
      { icon: '📖', text: '有哪些常见问题？' },
      { icon: '🔍', text: '帮我查找相关文档' },
      { icon: '❓', text: '解释一下这个概念' }
    ],
    2: [
      { icon: '✨', text: '帮我写一段产品介绍' },
      { icon: '📱', text: '生成社交媒体文案' },
      { icon: '🎯', text: '创作吸引人的广告语' },
      { icon: '📝', text: '优化这段营销文案' }
    ]
  };

  return suggestionsByTemplate[currentTemplate.value.id] || suggestionsByTemplate[1];
});

const goBack = () => {
  router.push('/');
};

const createNewSession = () => {
  const newSession = {
    id: sessions.value.length + 1,
    title: '新对话',
    time: Date.now()
  };
  sessions.value.unshift(newSession);
  currentSessionId.value = newSession.id;
  messages.value = [];
};

const switchSession = (sessionId) => {
  currentSessionId.value = sessionId;
  // In real app, load messages for this session
  messages.value = [];
};

const deleteSession = (sessionId) => {
  sessions.value = sessions.value.filter(s => s.id !== sessionId);
  if (currentSessionId.value === sessionId && sessions.value.length > 0) {
    currentSessionId.value = sessions.value[0].id;
  }
};

const sendSuggestion = (suggestion) => {
  inputMessage.value = suggestion.text;
  sendMessage();
};

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isGenerating.value) return;

  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    timestamp: Date.now()
  };

  messages.value.push(userMessage);
  inputMessage.value = '';
  adjustTextareaHeight();

  // Add AI response placeholder
  const aiMessage = {
    role: 'assistant',
    content: '',
    loading: true,
    timestamp: Date.now()
  };
  messages.value.push(aiMessage);

  isGenerating.value = true;
  await nextTick();
  scrollToBottom();

  // Simulate AI response
  setTimeout(() => {
    const responses = [
      '这是一个很好的问题。根据我对相关知识库的检索，我找到了以下信息：\n\n1. 首先，你需要了解基本概念\n2. 然后，按照步骤进行操作\n3. 最后，验证结果是否符合预期\n\n如果还有其他问题，随时询问我。',
      '让我为你生成一段精彩的文案：\n\n🎯 **突破创新，引领未来**\n\n我们致力于为客户提供最优质的产品和服务，通过持续创新和技术突破，帮助企业实现数字化转型。\n\n✨ 选择我们，选择成功！',
      '根据你的需求，我建议采取以下方案：\n\n**方案优势：**\n- 高效快速\n- 成本可控\n- 易于实施\n\n**实施步骤：**\n1. 准备阶段\n2. 执行阶段\n3. 验证阶段\n\n期待你的反馈！'
    ];

    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    aiMessage.loading = false;
    aiMessage.content = randomResponse;
    isGenerating.value = false;
    scrollToBottom();

    // Update session title with first message
    const currentSession = sessions.value.find(s => s.id === currentSessionId.value);
    if (currentSession && currentSession.title === '新对话') {
      currentSession.title = userMessage.content.slice(0, 20) + (userMessage.content.length > 20 ? '...' : '');
    }
  }, 1500);
};

const handleEnterKey = (event) => {
  if (!event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
};

const adjustTextareaHeight = () => {
  const textarea = inputTextarea.value;
  if (textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;

  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return Math.floor(diff / 60000) + ' 分钟前';
  if (diff < 86400000) return Math.floor(diff / 3600000) + ' 小时前';
  if (diff < 604800000) return Math.floor(diff / 86400000) + ' 天前';

  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
};

const formatMessage = (content) => {
  // Simple markdown-like formatting
  let formatted = content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');

  return formatted;
};

const copyMessage = (content) => {
  navigator.clipboard.writeText(content);
  // Show toast notification
  console.log('已复制到剪贴板');
};

const regenerateMessage = (index) => {
  // Regenerate the AI response
  console.log('重新生成消息', index);
};

const likeMessage = (index) => {
  messages.value[index].liked = !messages.value[index].liked;
};

const attachFile = () => {
  console.log('附加文件');
};

const shareTemplate = () => {
  console.log('分享模版');
};

const resetSettings = () => {
  settings.value = {
    temperature: 0.7,
    maxTokens: 2048,
    topP: 0.9,
    contextLength: 10,
    streaming: true
  };
};

onMounted(() => {
  adjustTextareaHeight();
});
</script>

<style scoped>
.generate-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.template-header {
  background: var(--panel);
  border-bottom: 1px solid var(--line);
  padding: 16px 24px;
  backdrop-filter: blur(12px);
  z-index: 10;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 100%;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: 8px;
  color: var(--text);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn svg {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

.back-btn:hover {
  background: var(--panel);
  border-color: var(--accent);
}

.template-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  margin: 0 24px;
}

.template-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.template-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--text);
}

.template-category {
  font-size: 14px;
  color: var(--muted);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: 10px;
  color: var(--text);
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn svg {
  width: 20px;
  height: 20px;
  stroke-width: 2;
}

.action-btn:hover {
  background: var(--panel);
  border-color: var(--accent);
}

.content-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: var(--panel);
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  position: relative;
}

.sidebar.collapsed {
  width: 60px;
}

.collapse-btn {
  position: absolute;
  right: -12px;
  top: 20px;
  width: 24px;
  height: 24px;
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
}

.collapse-btn svg {
  width: 14px;
  height: 14px;
  stroke-width: 2.5;
}

.collapse-btn:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--bg);
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--line);
}

.session-header h3 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--text);
}

.new-session-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  border: none;
  border-radius: 8px;
  color: var(--bg);
  cursor: pointer;
  transition: all 0.3s ease;
}

.new-session-btn svg {
  width: 16px;
  height: 16px;
  stroke-width: 2.5;
}

.new-session-btn:hover {
  transform: scale(1.1);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  margin-bottom: 8px;
  background: var(--panel-strong);
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.session-item:hover {
  border-color: var(--line);
}

.session-item.active {
  background: linear-gradient(135deg, rgba(126, 220, 255, 0.15), rgba(156, 123, 255, 0.15));
  border-color: var(--accent);
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.session-time {
  display: block;
  font-size: 12px;
  color: var(--muted);
}

.delete-session-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s ease;
}

.session-item:hover .delete-session-btn {
  opacity: 1;
}

.delete-session-btn svg {
  width: 14px;
  height: 14px;
  stroke-width: 2;
}

.delete-session-btn:hover {
  color: #ff6b6b;
}

/* Chat Container */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  max-width: 600px;
  margin: 60px auto;
  text-align: center;
}

.empty-icon {
  width: 100px;
  height: 100px;
  margin: 0 auto 24px;
  border-radius: 24px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  box-shadow: 0 20px 60px rgba(126, 220, 255, 0.3);
}

.empty-state h2 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px;
  color: var(--text);
  background: none;
  -webkit-text-fill-color: unset;
}

.empty-state h2::after {
  display: none;
}

.empty-state > p {
  font-size: 16px;
  color: var(--muted);
  margin: 0 0 40px;
}

.suggestions {
  margin-top: 40px;
}

.suggestions-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--muted);
  margin-bottom: 16px;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.suggestion-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
}

.suggestion-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(126, 220, 255, 0.2);
}

.suggestion-icon {
  font-size: 24px;
}

.suggestion-text {
  font-size: 14px;
  color: var(--text);
  font-weight: 500;
}

/* Messages */
.messages-container {
  max-width: 800px;
  margin: 0 auto;
}

.message-group {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  animation: fadeInUp 0.3s ease;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

.ai-avatar {
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  font-size: 20px;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.message-author {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.message-time {
  font-size: 12px;
  color: var(--muted);
}

.message-body {
  padding: 16px 20px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  position: relative;
}

.message-group.user .message-body {
  background: linear-gradient(135deg, rgba(126, 220, 255, 0.15), rgba(156, 123, 255, 0.15));
  border-color: rgba(126, 220, 255, 0.3);
}

.loading-indicator {
  display: flex;
  gap: 6px;
  padding: 8px 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

.message-text {
  color: var(--text);
  line-height: 1.7;
  font-size: 15px;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
}

.action-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 6px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-icon svg {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

.action-icon:hover {
  background: var(--panel-strong);
  border-color: var(--accent);
  color: var(--accent);
}

.action-icon.liked {
  background: rgba(126, 220, 255, 0.15);
  border-color: var(--accent);
  color: var(--accent);
}

/* Input Area */
.input-container {
  padding: 20px 24px;
  background: var(--panel);
  border-top: 1px solid var(--line);
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 14px 16px;
  background: var(--panel-strong);
  border: 2px solid var(--line);
  border-radius: 12px;
  color: var(--text);
  font-size: 15px;
  font-family: inherit;
  resize: none;
  max-height: 200px;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.message-input:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.06);
}

.message-input::placeholder {
  color: var(--muted);
}

.input-actions {
  display: flex;
  gap: 8px;
}

.input-action-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: 10px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.3s ease;
}

.input-action-btn svg {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

.input-action-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.send-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  border: none;
  border-radius: 10px;
  color: var(--bg);
  cursor: pointer;
  transition: all 0.3s ease;
}

.send-btn svg {
  width: 18px;
  height: 18px;
  stroke-width: 2.5;
}

.send-btn:not(:disabled):hover {
  transform: scale(1.05);
  box-shadow: 0 8px 20px rgba(126, 220, 255, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.input-hint {
  max-width: 800px;
  margin: 12px auto 0;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--muted);
}

.divider {
  color: var(--line);
}

/* Settings Panel */
.settings-panel {
  width: 320px;
  background: var(--panel);
  border-left: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--line);
}

.settings-header h3 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--text);
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 8px;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn svg {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

.close-btn:hover {
  background: var(--panel-strong);
  border-color: var(--accent);
  color: var(--accent);
}

.settings-body {
  padding: 20px;
}

.setting-group {
  margin-bottom: 28px;
}

.setting-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 12px;
}

.setting-value {
  padding: 4px 10px;
  background: rgba(126, 220, 255, 0.15);
  color: var(--accent);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
}

.setting-slider {
  width: 100%;
  height: 6px;
  background: var(--panel-strong);
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
}

.setting-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(126, 220, 255, 0.4);
}

.setting-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  border: none;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(126, 220, 255, 0.4);
}

.setting-hint {
  font-size: 12px;
  color: var(--muted);
  margin: 8px 0 0;
  line-height: 1.5;
}

.setting-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.setting-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.reset-settings-btn {
  width: 100%;
  padding: 12px;
  background: var(--panel-strong);
  border: 1px solid var(--line);
  border-radius: 10px;
  color: var(--text);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 20px;
}

.reset-settings-btn:hover {
  background: var(--panel);
  border-color: var(--accent);
  color: var(--accent);
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  transform: translateX(100%);
}

.slide-left-leave-to {
  transform: translateX(100%);
}

@media (max-width: 1024px) {
  .sidebar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 20;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }

  .settings-panel {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    z-index: 20;
    box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
  }
}

@media (max-width: 768px) {
  .template-info {
    margin: 0 12px;
  }

  .template-name {
    font-size: 16px;
  }

  .suggestion-grid {
    grid-template-columns: 1fr;
  }

  .chat-wrapper {
    padding: 16px;
  }

  .input-container {
    padding: 16px;
  }
}
</style>

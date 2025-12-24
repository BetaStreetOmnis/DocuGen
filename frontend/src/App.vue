<template>
  <div id="app">
    <div class="bg-pattern"></div>

    <!-- Header Navigation -->
    <header class="app-header">
      <div class="header-container">
        <div class="brand">
          <div class="brand-icon">📄</div>
          <div class="brand-text">
            <div class="brand-name">DocuGen</div>
            <div class="brand-tagline">文档生成工作台</div>
          </div>
        </div>

        <nav class="main-nav">
          <RouterLink to="/" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="3" width="7" height="7" rx="1"/>
              <rect x="3" y="14" width="7" height="7" rx="1"/>
              <rect x="14" y="14" width="7" height="7" rx="1"/>
            </svg>
            模版市场
          </RouterLink>
          <RouterLink to="/create" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            上传模版
          </RouterLink>
        </nav>

        <div class="header-actions">
          <button class="action-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4M12 8h.01"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="app-main">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="footer-container">
        <p>© 2024 DocuGen · AI驱动的文档生成平台</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router';
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-tertiary: #64748b;
  --accent: #3b82f6;
  --accent-secondary: #8b5cf6;
  --border: rgba(255, 255, 255, 0.1);
  --shadow: rgba(0, 0, 0, 0.5);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.bg-pattern {
  position: fixed;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(59, 130, 246, 0.15), transparent 40%),
    radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.15), transparent 40%);
  pointer-events: none;
  z-index: 0;
}

/* Header */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--accent), var(--accent-secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.brand-tagline {
  font-size: 11px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.main-nav {
  display: flex;
  gap: 8px;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
}

.nav-link svg {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

.nav-link:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.nav-link.router-link-active {
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.15);
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
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn svg {
  width: 20px;
  height: 20px;
  stroke-width: 2;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--accent);
  color: var(--text-primary);
}

/* Main */
.app-main {
  flex: 1;
  position: relative;
  z-index: 1;
}

/* Footer */
.app-footer {
  position: relative;
  z-index: 1;
  padding: 24px 0;
  border-top: 1px solid var(--border);
  margin-top: 60px;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  text-align: center;
}

.footer-container p {
  font-size: 14px;
  color: var(--text-tertiary);
}

/* Responsive */
@media (max-width: 768px) {
  .header-container {
    flex-wrap: wrap;
  }

  .main-nav {
    width: 100%;
    order: 3;
  }

  .brand-tagline {
    display: none;
  }

  .nav-link {
    flex: 1;
    justify-content: center;
  }
}
</style>

<template>
  <div id="app">
    <meta name="referrer" content="no-referrer" />

    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-container">
        <h1 class="logo">diy-bilibili</h1>
        <div class="nav-links">
          <router-link to="/characters" class="nav-link">角色卡片</router-link>
          <router-link to="/showall" class="nav-link">随机推荐</router-link>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-container">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style>
/* 全局基础样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  min-height: 100vh;
  background-color: #f5f5f7; /* Apple 风浅灰背景 */
  color: #1d1d1f;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
  scroll-behavior: smooth;
}

/* 导航栏 */
.navbar {
  position: sticky;
  top: 0;
  width: 100%;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  z-index: 1000;
  transition: background 0.3s ease;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* LOGO */
.logo {
  font-size: 1.6rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: #1d1d1f;
  user-select: none;
}

/* 导航链接 */
.nav-links {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-link {
  text-decoration: none;
  color: #1d1d1f;
  font-weight: 500;
  padding: 8px 18px;
  border-radius: 20px;
  transition: all 0.25s ease;
  background-color: transparent;
}

.nav-link:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.nav-link.router-link-active {
  background-color: #0071e3;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 113, 227, 0.3);
}

/* 主体容器 */
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px 80px;
}

/* 响应式 */
@media (max-width: 768px) {
  .logo {
    font-size: 1.3rem;
  }
  .nav-container {
    padding: 12px 16px;
  }
  .nav-link {
    padding: 6px 14px;
    font-size: 0.95rem;
  }
}
</style>

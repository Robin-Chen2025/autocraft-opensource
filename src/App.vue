<script setup lang="ts">
</script>

<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-left">
        <router-link to="/projects" class="logo">
          <span class="logo-icon">🦐</span>
          <span class="logo-text">AutoCraft</span>
        </router-link>
      </div>
      <nav class="header-nav">
        <router-link to="/projects" class="nav-item">
          项目概览
        </router-link>
      </nav>
      <div class="header-right">
        <!-- 预留位置 -->
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

/* Logo 区域 */
.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #303133;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.5px;
}

/* 导航区域 */
.header-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-item {
  padding: 8px 16px;
  font-size: 14px;
  color: #606266;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav-item:hover {
  color: #409eff;
  background: #ecf5ff;
}

.nav-item.router-link-active {
  color: #409eff;
  background: #ecf5ff;
  font-weight: 500;
}

/* 右侧预留 */
.header-right {
  width: 120px;
}

/* 主内容区 */
.app-main {
  flex: 1;
  padding: 20px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}
</style>
<template>
  <div class="task-list-view">
    <!-- 面包屑导航 -->
    <div class="breadcrumb-container">
      <el-breadcrumb separator=">">
        <el-breadcrumb-item :to="{ path: '/' }">
          <el-icon><HomeFilled /></el-icon>
          <span class="breadcrumb-text">首页</span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>
          <el-icon><List /></el-icon>
          <span class="breadcrumb-text active">任务列表</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 任务列表组件 -->
    <TaskList />
  </div>
</template>

<script setup lang="ts">
import TaskList from '../components/TaskList.vue'
import { HomeFilled, List } from '@element-plus/icons-vue'
</script>

<style scoped>
.task-list-view {
  background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
  min-height: 100vh;
  padding: 20px;
}

.breadcrumb-container {
  margin-bottom: 20px;
  padding: 16px 24px;
  background: linear-gradient(145deg, #1a1f2e 0%, #21283a 100%);
  border: 1px solid #00d4ff;
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
}

.breadcrumb-container :deep(.el-breadcrumb) {
  font-size: 14px;
  line-height: 1.5;
}

.breadcrumb-container :deep(.el-breadcrumb__item) {
  display: flex;
  align-items: center;
}

.breadcrumb-container :deep(.el-breadcrumb__inner) {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #8b949e;
  transition: all 0.3s ease;
}

.breadcrumb-container :deep(.el-breadcrumb__inner.is-link) {
  color: #00d4ff;
  cursor: pointer;
}

.breadcrumb-container :deep(.el-breadcrumb__inner.is-link:hover) {
  color: #00ffff;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.breadcrumb-text {
  margin-left: 4px;
}

.breadcrumb-text.active {
  color: #00d4ff;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.breadcrumb-container :deep(.el-breadcrumb__separator) {
  color: #00d4ff;
  margin: 0 8px;
  font-weight: bold;
}

.breadcrumb-container :deep(.el-icon) {
  color: #00d4ff;
  font-size: 16px;
}
</style>

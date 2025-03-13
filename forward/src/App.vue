<script setup lang="ts">
// App.vue 只需要渲染路由组件
</script>

<template>
  <router-view />
</template>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

#app {
  height: 100vh;
}

/* 隐藏滚动条但保留功能 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
</style>

<script setup lang="ts">
import { onMounted, watch, ref } from 'vue';
import { useRoute } from 'vue-router';

// 获取当前路由
const route = useRoute();
const currentTitle = ref('');

// 更新标题函数
const updateTitle = () => {
  // 获取路由元数据中的标题
  const metaTitle = route.meta.title as string;
  if (metaTitle) {
    currentTitle.value = metaTitle;
    // 更新浏览器标签标题
    document.title = metaTitle;
  } else {
    currentTitle.value = '景区数据分析与可视化系统';
    document.title = '景区数据分析与可视化系统';
  }
};

// 在组件挂载时更新标题
onMounted(() => {
  updateTitle();
});

// 监听路由变化，更新标题
watch(() => route.path, () => {
  updateTitle();
}, { immediate: true });
</script>

<template>
  <!-- 这是一个无视图组件，仅用于处理标题更新 -->
</template> 
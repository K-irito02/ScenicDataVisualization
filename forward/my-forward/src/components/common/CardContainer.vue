<template>
  <div class="card-container">
    <div class="card-header" v-if="title">
      <h3 class="card-title">{{ title }}</h3>
      <div class="card-actions">
        <slot name="actions"></slot>
      </div>
    </div>
    <div class="card-body" :class="{ 'no-padding': noPadding }">
      <slot></slot>
    </div>
    <div class="card-footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'CardContainer',
  props: {
    title: {
      type: String,
      default: ''
    },
    noPadding: {
      type: Boolean,
      default: false
    }
  }
})
</script>

<style scoped>
.card-container {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  width: 100%;
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.card-actions {
  display: flex;
  align-items: center;
}

.card-body {
  padding: 20px;
}

.card-body.no-padding {
  padding: 0;
}

.card-footer {
  padding: 15px 20px;
  border-top: 1px solid #f0f0f0;
}
</style> 
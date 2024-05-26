<script lang="ts">
import {defineComponent} from 'vue'

export default defineComponent({
  setup() {
    return {
      zIndex: 3000,
      size: 'default',
    }
  },
})
</script>

<template>
  <el-config-provider :size="size" :z-index="zIndex">
    <el-scrollbar height="100vh">
      <RouterView/>
    </el-scrollbar>
  </el-config-provider>
</template>

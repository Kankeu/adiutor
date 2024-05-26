<script setup lang="ts">
import { defineProps } from 'vue'
import {InfoFilled,Timer,CircleCheck} from "@element-plus/icons-vue";
const props = defineProps({task:{type:Object,required:true}})
</script>
<template>
      <el-card shadow="never" :body-style="{ padding: '12px 10px' }">
        <el-space class="m-task" style="width: 100%;">
          <div style="font-size: 16px;width: 100%;text-align: left;display: flex;justify-content: space-between;align-items: center">
            <template v-if="false">
              <el-icon>
                <component :is="f.icon"></component>
              </el-icon>
            </template>
            <div>
              <el-icon color="green" v-if="task.status=='done'"><CircleCheck /></el-icon>
              {{ task.title }}
            </div>
            <small style="display:flex;align-items: center"><span v-if="task.priority&&task.status!='done'" style="color:green;margin-right: 10px">★{{ task.priority }}</span> <span v-if="task.context" style="color:blue;margin-right: 10px">#{{task.context.name}}</span> <span v-if="task.deadline&&task.status!='done'"><div v-if="task.start"><el-icon><Timer /></el-icon>&nbsp;&nbsp;{{task.start}}</div>⌛ {{ task.deadline }}</span></small>
          </div>
        </el-space>
      </el-card>
</template>

<style>
.m-task .el-space__item{
  width: 100%;
}
</style>

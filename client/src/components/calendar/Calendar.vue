<script setup lang="ts">
import {useCalendar} from "@/stores/calendar";
import {ref,watch} from "vue";
import {storeToRefs} from "pinia"
import {InfoFilled} from "@element-plus/icons-vue";
import Task from "@/components/calendar/Task.vue";

const calendar = useCalendar()
const {tasks} = storeToRefs(calendar)
</script>

<template>
      <div v-if="!tasks.length" :style="{display: 'flex',alignItems: 'center',justifyContent: 'center',height: innerHeight+'px'}">
        <el-empty image="/images/defaults/sleeping.png" :image-size="200" description="Boredom traps"/>
      </div>
      <div style="width: 100%;display: flex;flex-direction: column;align-items: center;padding: 15px;" v-else>
        <div style="font-weight: bold;font-size: 20px;margin-bottom: 5px">To Do</div>
        <Task :task="task" v-for="task in tasks.filter(t=>t.status!='done')" :key="task.id" :style="{width:'100%',maxWidth:'600px',marginBottom: '.75em'}"></Task>
        <div style="font-weight: bold;font-size: 20px;margin-bottom: 5px" v-if="tasks.filter(t=>t.status=='done').length">Done</div>
        <Task :task="task" v-for="task in tasks.filter(t=>t.status=='done')" :key="task.id" :style="{width:'100%',maxWidth:'600px',marginBottom: '.75em'}"></Task>
      </div>
</template>
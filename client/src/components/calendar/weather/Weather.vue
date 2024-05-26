<script setup lang="ts">
import {useCalendar} from "@/stores/calendar";
import {ref,watch} from "vue";
import {storeToRefs} from "pinia"
import {ArrowDown,ArrowUp} from '@element-plus/icons-vue'

const calendar = useCalendar()
const {forecasts} = storeToRefs(calendar)

function get_emoji(forecast){
  const tmp = {}
  for (const hf of forecast.hourly_forecasts)
    if(hf.emoji) tmp[hf.emoji] = (tmp[hf.emoji]??0) + 1
  let max = [null,0]
  for (const emoji in tmp)
    if(tmp[emoji]>max[1]) max = [emoji,tmp[emoji]]
  return max[0]
}
function get_adverse_weather(forecast){
  const tmp = {}
  for (const hf of forecast.hourly_forecasts)
    if(hf.adverse_weather) tmp[hf.adverse_weather] = (tmp[hf.adverse_weather]??0) + 1
  let max = [null,0]
  for (const adverse_weather in tmp)
    if(tmp[adverse_weather]>max[1]) max = [adverse_weather,tmp[adverse_weather]]
  return max[0]?.replace("_"," ")
}
function dateToText(date){
  const today = new Date()
  const format = (today)=>today.getFullYear()+"-"+String(today.getMonth()+1).padStart(2, '0')+"-"+String(today.getDate()).padStart(2, '0')
  if (date==format(today))
  return "Today"
  today.setDate(today.getDate()+1)
  if (date==format(today))
    return "Tomorrow"
  return date
}
</script>

<template>
<el-card shadow="never">
  <div style="font-weight: bold;font-size: 20px;margin-bottom: 10px">Weather (Kaiserslautern)</div>
  <el-timeline style="max-width: 600px">
    <el-timeline-item :timestamp="dateToText(forecast.date)" placement="top" v-for="(forecast,i) in forecasts" Key="i">
      <el-card>
        <div style="display: flex;justify-content: space-between;align-items: center">
          <div>
            <span style="font-size: 20px;font-weight: bold" v-if="get_emoji(forecast)">{{get_emoji(forecast)}}</span> <span style="font-size: 20px;font-weight: bold">{{forecast.temperature}}°C</span>
          </div>
          <el-space></el-space>
          <div :style="{fontWeight: 'bold',color: get_adverse_weather(forecast) ? 'red':'green'}">
            {{ capitalize(get_adverse_weather(forecast) ? (get_adverse_weather(forecast)+" (adverse)") : "Good weather") }}
          </div>
          <el-button size="small" circle @click="forecast.show=!forecast.show" :icon="forecast.show? ArrowUp:ArrowDown "></el-button>
        </div>
        <p v-if="forecast.show">
          <div style="display: flex;justify-content: space-between;font-size: 15px;font-weight: bold" v-for="(hf,i) in forecast.hourly_forecasts" :key="i">
            <div style="">
              {{hf.emoji}} {{hf.temperature}}°C
            </div>
            <div>
              {{hf.date}}
            </div>
          </div>
        </p>


      </el-card>
    </el-timeline-item>
  </el-timeline>
</el-card>
</template>
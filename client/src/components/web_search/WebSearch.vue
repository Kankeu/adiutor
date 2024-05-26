<script setup lang="ts">
import {ref, onMounted, watch, type Ref} from "vue";
import {ChromeFilled} from "@element-plus/icons-vue";
import {Back,RefreshRight} from "@element-plus/icons-vue";
import "./x-frame-bypass"
import {useChat} from "@/stores/chat";
import {storeToRefs} from "pinia"

const chat = useChat()
const {web_search} = storeToRefs(chat)

const iframe: Ref<any> = ref(null)
const history:Ref<string[]> = ref([])
const current_source:Ref<any> = ref(null)

function init(){
  history.value = web_search.value.current ? [web_search.value.current] : []
  current_source.value = web_search.value.sources.find(s=>s.url==history.value[history.value.length-1])
  if(iframe.value)
    iframe.value.onload = ()=>{
      const div = document.createElement('div');
      div.innerHTML = iframe.value.srcdoc.split("\n")[1].trim()
      const base = div.querySelector("base")
      if(base&&history.value[history.value.length-1]!=base.href) history.value.push(base.href)
   }
}
onMounted(init)
watch(()=>web_search,()=>{
  init()
},{deep:true})
function back(){
  if(history.value.length>=2) {
    history.value.pop()
    iframe.value.load(history.value.pop())
  }
}
function refresh(){
  iframe.value.src = history.value[history.value.length-1]
}
</script>

<template>
<div style="height: 100%;width: 100%">
  <div v-if="history.length" style="height: 100%;width: 100%">
    <div style="background: white;padding: 10px;border-bottom: 1px var(--el-border-color) var(--el-border-style)" v-if="history.length">
      <el-page-header>
        <template #icon>
          <el-button @click="back" :icon="Back" circle></el-button>
        </template>
        <template #title>
          <el-button @click="refresh" :icon="RefreshRight" circle></el-button>
        </template>
        <template #content v-if="current_source">
          {{ toEllipsis(current_source.title,15) }}
        </template>
        <template #extra v-if="history.length">
          <el-button :type="current_source.url==source.url?'primary':null"  size="small" @click="chat.updateWebSearch({current:source.url})" v-for="(source,i) in web_search.sources" :key="i">Source {{i+1}}</el-button>
          <el-link target="_blank" style="margin-left: 10px" :href="history[history.length-1]">{{ toEllipsis(history[history.length-1],60) }}</el-link>
        </template>
      </el-page-header>
    </div>
    <iframe style="border: none" is="x-frame-bypass" ref="iframe" :src="history[history.length-1]" width="100%" height="100%"></iframe>
  </div>
  <div style="display: flex;justify-content: center;align-items: center;height: 100%;width: 100%" v-else>
    <div style="display: flex;flex-direction: column;align-items: center">
      Embedded browser
      <el-icon size="30"><ChromeFilled /></el-icon>
    </div>
  </div>
</div>
</template>

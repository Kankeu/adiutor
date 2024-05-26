<script setup lang="ts">
import {inject, reactive, ref} from "vue";
import {useRoute} from "vue-router"
import { ElMessage } from 'element-plus'
import {Microphone, Search, Close} from "@element-plus/icons-vue";
import chatRepository from "@/repositories/ChatRepository"

const loading = ref(false)
const recording = ref(false)
const form = reactive({text: ""})
const $route = useRoute()

async function send(type=null) {
  loading.value = true
  const data = {role: "human", text: form.text.trim()}
  if($route.query.feature) data.feature = $route.query.feature
  form.text = ""
  if (!!data.text) await chatRepository.query(data,type=="speech")
  loading.value = false
}
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || window.mozSpeechRecognition || window.msSpeechRecognition
let record:any = null
if(SpeechRecognition){
  const recognition = new SpeechRecognition()
  recognition.lang = 'en-US';
  recognition.onstart = () => {
    form.text = ""
    recording.value = true
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    form.text = transcript;
  };

  recognition.onend = () => {
    recording.value = false
    send("speech")
  };
  record = ()=>{
    if (!recording.value)
      recognition.start();
    else  recognition.stop();
  }
}else{
  ElMessage.error(
      {
        showClose: true,
        duration: 0,
        dangerouslyUseHTMLString: true,
        message:'The speech recognition is not supported by this browser. <br>Please one of the latest Chrome browser (e.g., version 123.0.6312.58)'
      })
}
</script>

<template>
  <el-input
      v-model="form.text"
      @keyup.enter="send"
      class="w-50 m-2"
      size="large"
      clearable
      :disabled="!$route.query.feature || loading"
      :placeholder="recording ? 'Listening...': ($route.query.feature=='web_search' ? 'Search in web': 'Ask your calendar')"
      :prefix-icon="Search"
  >
    <template #suffix>
      <el-button @click="chatRepository.stop()" v-if="loading" type="danger" size="small" circle :icon="Close"></el-button>
      <el-button @click="record" :type="recording ? 'success' : 'primary'" :size="recording ? 'default' : 'small'" :icon="Microphone" circle :disabled="!$route.query.feature || !SpeechRecognition" v-else/>
    </template>
  </el-input>
</template>

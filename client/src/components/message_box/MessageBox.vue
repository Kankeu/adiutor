<script setup lang="ts">
import {useChat} from "@/stores/chat";
import {ref,watch} from "vue";
import {storeToRefs} from "pinia"
import Message from "@/components/message/Message.vue";

const chat = useChat()
const {messages} = storeToRefs(chat)
const scrollbarRef = ref<InstanceType<typeof ElScrollbar>>()
chat.onMessage(()=>{
  const scrollHeight = scrollbarRef.value?.wrapRef?.scrollHeight
  const scrollTop = scrollbarRef.value?.wrapRef?.scrollTop

  if(!scrollHeight || !scrollTop || (scrollHeight - scrollTop)<2000)
    scrollbarRef.value?.setScrollTop(scrollHeight)
})
</script>

<template>
  <el-scrollbar ref="scrollbarRef" :style="{height: (innerHeight-200)+'px'}">
    <div :style="{height: (innerHeight-250)+'px',marginBottom: '.75em',display: 'flex',flexDirection: 'column',justifyContent: 'center'}" v-if="!messages.length">
      <div style="display: flex;justify-content: center;align-items: center;">
        <el-image
            style="width: 50px; height: 50px;border-radius: 50%;background: #002857"
            src="/images/defaults/rptu.png"
            :zoom-rate="1.2"
            :max-scale="7"
            :min-scale="0.2"
            :initial-index="4"
            fit="cover"
        />
      </div>
      <div style="font-weight: 700;font-size: 1.5rem;text-align: center">
        How can I help you today?
      </div>
    </div>
    <Message v-for="(message,i) in messages" :key="message.id" :item="message" v-else></Message>
  </el-scrollbar>
</template>
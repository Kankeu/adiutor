<script setup lang="ts">
import {Search, Delete, Microphone} from '@element-plus/icons-vue'

import MessageField from "@/components/message/MessageField.vue";
import MessageBox from "@/components/message_box/MessageBox.vue";
import {useChat} from "@/stores/chat";
import Mute from "@/components/message/Mute.vue";

const chat = useChat()

</script>

<template>
  <el-card :style="{height:innerHeight+'px'}" shadow="never">
    <template #header>
      <el-space style="justify-content: space-between;width: 100%;">
        <div class="card-header">
          <span>Adiutor</span>
        </div>
        <div>
          <el-tooltip
              effect="dark"
              content="Cancel speech synthesis"
              placement="top"
          >
            <el-button @click="stopSpeaking" type="danger" size="small" circle>
              <el-icon>
                <Mute></Mute>
              </el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip
              effect="dark"
              content="Empty the chat"
              placement="top"
          >
            <el-button @click="chat.clearMessages()" type="info" size="small" :icon="Delete" circle/>
          </el-tooltip>
        </div>
      </el-space>
    </template>
    <MessageBox></MessageBox>
    <template #footer>
        <MessageField></MessageField>
        <div style="font-size: small;text-align: center;">
          Adiutor may display inaccurate info, so double-check its responses.
        </div>
    </template>
  </el-card>
</template>


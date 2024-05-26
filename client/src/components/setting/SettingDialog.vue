<script lang="ts" setup>
  import {ref, watch} from 'vue'
  import {Setting} from "@element-plus/icons-vue";
  import { useChat } from '@/stores/chat';

  const chat = useChat()
  const dialog = ref(false)
  const formLabelWidth = '115px'

  const form = ref({})
  function confirm(){
    chat.setSettings(form.value)
  }
  watch(dialog, () => {
    form.value = {...(chat.settings() ?? {
       url: '',
       api_token: '',
       system_prompt: '',
     })}
  })
</script>

<template>
  <el-button type="info" size="small" :icon="Setting" circle @click="dialog = true"/>

  <el-dialog v-model="dialog" title="Settings" width="600" v-if="form">
    <el-form :model="form">
      <el-form-item label="LLM URL" :label-width="formLabelWidth">
        <el-input v-model="form.url" clearable placeholder="https://{name and region}.amazonaws.com/dsa_llm/generate"/>
      </el-form-item>
      <el-form-item label="LLM API Token" :label-width="formLabelWidth">
        <el-input v-model="form.api_token" clearable placeholder="AWS API TOKEN"/>
      </el-form-item>
      <el-form-item label="System Prompt" :label-width="formLabelWidth">
      <el-input
          v-model="form.system_prompt"
          :rows="2"
          type="textarea"
          autosize
          clearable
          placeholder="Be concise and answer in bullet points."
      />
      </el-form-item>

    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialog = false">Cancel</el-button>
        <el-button type="primary" @click="confirm();dialog = false">
          Confirm
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>
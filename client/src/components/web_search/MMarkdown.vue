<script setup lang="js">
import {defineProps} from "vue"
import Markdown from 'vue3-markdown-it';
import {useChat} from "@/stores/chat";

const chat = useChat()
const props = defineProps(["message"])

function navigate(event){
  if(event.target&&event.target.href) chat.updateWebSearch({current:event.target.href})

}
</script>

<template>
    <Markdown :source="message" @click.prevent="navigate"/>
</template>
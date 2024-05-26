<script>
import {Money, View, CopyDocument} from '@element-plus/icons-vue'

import {ref, watch} from 'vue';
import DotBouncing from '../loading/DotBouncing.vue'
import MMarkdown from "@/components/web_search/MMarkdown.vue";
import {useChat} from "@/stores/chat";
import Sound from "@/components/message/Sound.vue";
import {nextTick} from "vue";

export default {
  components: {DotBouncing, MMarkdown, Sound, Money, View, CopyDocument},
  props: {
    item: {type: Object, required: true},
  },
  mounted() {
    if (this.item.speech)
      nextTick(() => this.speak(this.$refs.message.$el.innerText))
    else watch(() => this.item, (n, l) => {
      if (n?.speech && !l?.speech)
        nextTick(() => this.speak(this.$refs.message.$el.innerText))
    }, {deep: true})
  },
  setup(props) {

    const chat = useChat()


    const showSources = ref(false);

    const toggleShowSource = () => {
      showSources.value = !showSources.value;
    };

    return {
      chat,
      showSources,
      toggleShowSource,
    }

  }
}

</script>

<template>
  <DotBouncing v-if="item.loading" style="font-size: 30px"></DotBouncing>
  <div style="margin-bottom: 10px" v-else>
    <el-row style="justify-content: space-between">
      <el-space>
        <span>{{ item.role == "human" ? 'You' : 'AI' }}</span>
        <template v-if="item?.cost">
          <el-tooltip placement="top" :content="'Estimated cost ' + item.cost + ' tokens'">
            <div style="align-items: center;display: flex">
              <el-icon>
                <Money/>
              </el-icon>&nbsp;cost
            </div>
          </el-tooltip>
        </template>
      </el-space>
      <template v-if="item?.sources?.length">
        <small style="cursor:pointer" @click="toggleShowSource">
          {{ showSources ? 'Hide Sources' : 'Show Source' }}
        </small>
      </template>
    </el-row>
    <el-collapse v-if="showSources" accordion>
      <el-collapse-item v-for="(source, index) in item?.sources" :key="index" :name="index">
        <template #title>
          <div style="display: flex;justify-content: space-between;width: 100%;align-items: baseline">
            <strong>{{ toEllipsis(source.title, 30) }}</strong>
            <div style="display:flex;">
              <el-button style="margin-right: 5px" size="small"
                         @click.prevent.stop="chat.updateWebSearch({current:source.url})" circle>
                <el-icon>
                  <View></View>
                </el-icon>
              </el-button>
              <div
                  style="background:gray;border-radius: 50%;display: flex;align-items: center;justify-content: center;color:white;height: 23px;width: 23px;margin-right: 5px;padding-top: 1px;font-size: 10px">
                {{ Math.round(source.score * 100) }}
              </div>
            </div>
          </div>
        </template>
        <div v-html="source.text"></div>
      </el-collapse-item>
    </el-collapse>
    <el-popover placement="top" :width="80">
      <div style="display:flex;justify-content: space-between">
        <el-button @click="copy(item.text)">
          <el-icon>
            <CopyDocument></CopyDocument>
          </el-icon>
        </el-button>
        <el-button @click="speak($refs.message.$el.innerText)" type="primary">
          <el-icon>
            <Sound></Sound>
          </el-icon>
        </el-button>
      </div>
      <template #reference>
        <el-card :body-style="{ padding: '12px 10px' }" shadow="hover"
                 :style="{cursor:'pointer',background: (item.role=='human' ? '#3b82f6' : '#eff6ff'), color: (item.role=='human' ? 'white' : 'black')}">
          <MMarkdown ref="message" :message="item.text"></MMarkdown>
        </el-card>
      </template>
    </el-popover>
  </div>
</template>

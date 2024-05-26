<script lang="ts">
import {Calendar, Search, Link, InfoFilled, HomeFilled, Delete} from '@element-plus/icons-vue'
import SettingDialog from "@/components/setting/SettingDialog.vue";
import Weather from "@/components/calendar/weather/Weather.vue";
import Mute from "@/components/message/Mute.vue";

export default {
  computed: {
    Delete() {
      return Delete
    }
  },
  components: {Mute, Weather, Calendar, Search, Link, InfoFilled, HomeFilled, SettingDialog},
  data: () => ({
    features: [
      {
        "icon": HomeFilled,
        "id": null,
        "name": "Welcome",
      },
      {
        "icon": Calendar,
        "id": "calendar",
        "name": "Calendar",
        "description": "Manage deadlines and to-do lists by scheduling tasks (based on weather conditions)."
      },
      {
        "icon": Search,
        "id": "web_search",
        "name": "Web Search",
        "description": "Perform web searches using RAG."
      },
    ]
  }),
  methods: {
    navigate(f) {
      if (f.id) {
        this.pushQuery({feature: f.id})
      } else {
        this.popQuery('feature')
      }
    }
  }
}
</script>

<template>
  <el-card :style="{padding: 0,margin: 0,height: innerHeight+'px'}" shadow="never" class="doc-list">
    <template #header>
      <el-space style="justify-content: space-between;width: 100%;">
        <div class="card-header">
          <span>Menu</span>
        </div>
      </el-space>
    </template>
    <el-scrollbar :style="{height: (innerHeight-70)+'px'}">
      <el-scrollbar
          :style="{height: .8*(innerHeight-70)+'px',paddingTop:'1em',paddingBottom: '1em',paddingLeft: '.5em',paddingRight: '.5em'}">
        <el-card shadow="hover" @click="navigate(f)" v-for="f in features" :key="f"
                 :style="{cursor:'pointer',marginBottom: '.75em',border: '1px solid var(--el-border-color)',opacity:!!$route.query.feature?.6:1,...(f.id==$route.query.feature ? {opacity:1,borderColor: 'blue',borderLeftWidth: '3px'} : {})}">
          <el-space style="justify-content: space-between;width: 100%">
            <div style="font-size: 16px;width: 100%;text-align: left">
              <template>
                <el-icon>
                  <component :is="f.icon"></component>
                </el-icon>
              </template>
              {{ f.name }}
            </div>
            <el-tooltip
                v-if="f.description"
                :content="f.description"
                placement="top"
            >
              <el-icon size="20">
                <InfoFilled></InfoFilled>
              </el-icon>
            </el-tooltip>
          </el-space>
        </el-card>
        <Weather v-if="$route.query.feature=='calendar'"></Weather>
      </el-scrollbar>
      <el-divider></el-divider>
      <el-image style="padding-left: .5em;padding-right: .5em;" src="/images/defaults/rptu-h.png"></el-image>
      <el-row style="padding: .5em;">
        <el-space style="justify-content: space-between;width: 100%">
          Made by KFIN
          <SettingDialog></SettingDialog>
        </el-space>
      </el-row>
    </el-scrollbar>
  </el-card>

</template>
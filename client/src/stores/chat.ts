import {defineStore} from 'pinia'
import {nextTick, reactive} from "vue";

export const useChat = defineStore('chat', {
    state: () => ({
        web_search: {current: null,sources:[]},
        _onMessage: null,
        messages: [],
    }),
    getters: {
        settings(state) {
            return () => {
                try {
                    return JSON.parse(localStorage.getItem('settings')??"{}")
                } catch (e) {
                    return null
                }
            }
        },
    },
    actions: {
        addMessage(message) {
            const i = this.messages.findIndex(m => m.id == message.id)
            if (i >= 0) {
                this.messages.splice(i, 1)
                nextTick(() => {
                    this.messages.splice(i, 0, message)
                    nextTick(() => {
                        if (this._onMessage) this._onMessage(message)
                    })
                })
            } else {
                this.messages.push(message)
                nextTick(() => {
                    if (this._onMessage) this._onMessage(message)
                })
            }
        },
        findMessage(id) {
            const i = this.messages.findIndex(m => m.id == id)
            return i >= 0 ? this.messages[i] : null
        },
        onMessage(onMessage) {
            this._onMessage = onMessage
        },
        removeMessage(id) {
            const i = this.messages.findIndex(m => m.id == id)
            if (i >= 0) this.messages.splice(i, 1)
        },
        clearMessages() {
            this.messages = []
        },
        setSettings(settings) {
            localStorage.setItem('settings', JSON.stringify(settings));
        },
        updateWebSearch(web_search){
            this.web_search = {...this.web_search,...web_search}
        }
    },
})
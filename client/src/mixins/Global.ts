import {computed, ref} from 'vue'
import {ElMessage} from 'element-plus'
import copy from "copy-text-to-clipboard"

const queue = []
const _speak = (text)=> {
    return  new Promise((resolve, reject) => {
         try {
             const utterance = new SpeechSynthesisUtterance(text.slice(0, 3840))

             utterance.volume = 1;
             utterance.rate = 1;
             utterance.lang = "en-US";

             async function resumeInfinity() {
                 await window.speechSynthesis.pause();
                 await window.speechSynthesis.resume();
                 if(window.speechSynthesis.speaking || window.speechSynthesis.pending)
                 window.timeoutResumeInfinity = setTimeout(resumeInfinity, 1000);
                 else resolve(true)
             }

             utterance.onstart = resumeInfinity
             utterance.onend = (event) => {
                 clearTimeout(window.timeoutResumeInfinity);
             };
             clearTimeout(window.timeoutResumeInfinity);
             window.speechSynthesis.cancel();
             clearTimeout(window.speech_timeout);

             window.speech_timeout = setTimeout(() => window.speechSynthesis.speak(utterance), 250);
         } catch (e) {
             console.error(e)
         }
    })
 }

const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))

 export async function speak(text){
     while(window.speechSynthesis.speaking || window.speechSynthesis.pending){
        await sleep(1000)
     }
     await _speak(text)
 }

const Mixin = {
    data() {
        return {
            elui: {
                breakpoint: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            }
        }
    },
    computed: {
        innerWidth() {
            return this.elui.breakpoint.width
        },
        innerHeight() {
            return this.elui.breakpoint.height
        },
    },
    mounted() {
        this.$nextTick(() => {
            window.addEventListener('resize', this.onResize);
        })
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.onResize);
    },
    methods: {
        capitalize(value) {
            return value[0].toUpperCase() + value.slice(1).toLowerCase()
        },
        stopSpeaking() {
            window.speechSynthesis.cancel()
        },
        speak,
        copy(text) {
            copy(text)
            ElMessage({
                message: 'Copied',
                type: 'success',
            })
        },
        toEllipsis(text, length) {
            return text.substr(0, length) + (text.length > length ? '...' : '')
        },
        pushQuery(toQuery) {
            this.$router.replace({...this.$route, query: {...this.$route.query, ...toQuery}}).catch(_ => {
            })
        },
        popQuery(...fromQuery) {
            let query = {...this.$route.query}
            fromQuery.forEach(e => delete query[e])
            this.$router.replace({query}).catch(_ => {
            })
        },

        onResize() {
            this.elui.breakpoint.weight = window.innerWidth
            this.elui.breakpoint.height = window.innerHeight
        }
    }
}

export default function (app) {
    app.mixin(Mixin)
}
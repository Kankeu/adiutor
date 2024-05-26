import { ElNotification } from 'element-plus'
import {useCalendar} from "@/stores/calendar";
import {useChat} from "@/stores/chat";
import {speak} from "@/mixins/Global";
import {default as http,HttpExecutor} from "@/http/http"
import StreamingJsonParser from "@/utils/StreamingJsonParser"

class ChatRepository{
    stopped = false
    executor?: HttpExecutor

    stop(){
        this.stopped = true
        this.executor?.abort()
    }

    async query(data:any,speech:boolean){
        this.stopped = false
        const chat = useChat()
        const calendar = useCalendar()
        const settings = chat.settings()
        chat.addMessage({...data,id:Date.now()})
        const loading_msg = {id:Date.now()+1,loading:true}
        chat.addMessage(loading_msg)
        const parser = new StreamingJsonParser()
        try{
            this.executor = http.post("api/query", {payload:{query:data.text,feature:data.feature},settings:{url:settings.url,api_token:settings.api_token,system_prompt:settings.system_prompt}})
            const res = await this.executor.execute()
            const message = {role:"assistant",text:"",id:Date.now()}

            const reader = res?.body?.getReader() as ReadableStreamDefaultReader;

            const decoder = new TextDecoder();
            let done = false;
            let metaData: any = null;
            let metaRawData = ""
            while (!done && !this.stopped) {
                try{
                    const { value, done: doneReading } = await reader.read();
                    done = doneReading;
                    let chunkValueStr = decoder.decode(value)
                    try{
                        let action = null
                        for (const chunkValue of parser.parse(chunkValueStr?.trim())){
                            [metaRawData,metaData,action] = this._processChunkValue(calendar,chat,metaRawData,metaData,loading_msg,message,chunkValue,speech)
                            if (action=="continue")
                                continue
                            if (action=="break")
                                break
                        }
                    }catch (e) {
                        console.error(e,chunkValueStr)
                    }
                }catch (e) {
                    console.error(e)
                    break
                }
            }
            reader?.cancel()
        }catch (e){
            console.error(e)
            chat.removeMessage(data.id)
            ElNotification({
                title: 'Oops something went wrong!!!',
                message: String(e),
                type: 'error',
                duration:9000
            })
            if(speech) speak('Oops something went wrong!!!')
        }
        chat.removeMessage(loading_msg.id)

    }

    _processChunkValue(calendar,chat,metaRawData,metaData,loading_msg,message,chunkValue,speech){
        console.log(chunkValue)
        if (chunkValue.status == "done")
            return [metaRawData,metaData,"done"]
        if (chunkValue.status=="error"){
            ElNotification({
                title: 'Error',
                message: chunkValue.payload.message,
                type: 'error',
                duration: 9000
            })
            if(speech) speak(chunkValue.payload.message)
            message.text = "Please try again!"
            chat.addMessage({...message,type:"error"})
        }
        if (chunkValue.type=="tasks"){
            if(["show","show_all"].includes(chunkValue.payload?.action)){
                function tasks_to_text(tasks){
                    let text = ""
                    for (const name of new Set(tasks.map(t=>t.context.name))){
                        text += "In your task list \""+name+"\", you have the following tasks to do:\n  -"
                        text += tasks.filter(t=>t.context.name==name).map(t=>t.title).join("\n  -")
                        text += "\n"
                    }
                    return text
                }
                calendar.clearTasks()
                for (const task of chunkValue.payload.tasks)
                    calendar.addTask(task)
                message.text = "Done!"
                if(speech) {
                    if(chunkValue.payload?.action=="show")
                        speak(tasks_to_text(chunkValue.payload.tasks))
                    else message.speech = true
                }
                chat.addMessage({...message,...metaData})
                return [metaRawData,metaData,"continue"]
            }
            if(chunkValue.payload?.action=="forecast") {
                calendar.clearForecasts()
                for (const forecast of chunkValue.payload.forecasts)
                    calendar.addForecast(forecast)
                return [metaRawData,metaData,"continue"]
            }
            if(chunkValue.payload?.action=="postpone") {
                ElNotification({
                    title: 'Info',
                    message: chunkValue.payload.response,
                    type: 'info',
                    duration: 9000
                })
                message.text = chunkValue.payload.response
                message.speech = speech
                chat.addMessage({...message,...metaData})
                //if(speech) speak(chunkValue.payload.response)
                return [metaRawData,metaData,"continue"]
            }
            if(chunkValue.payload?.action=="weather_checking") {
                message.text = chunkValue.payload.response
                message.speech = speech
                chat.addMessage({...message,...metaData})
                return [metaRawData,metaData,"continue"]
            }
            if(chunkValue.payload?.action=="execute") {
                console.log(chunkValue.payload.commands)
                return [metaRawData,metaData,"continue"]
            }
        }
        metaRawData += chunkValue

        if (chunkValue.type == "metadata"){
            const sources = chunkValue.payload.sources
            chat.updateWebSearch({current:sources.length ? sources[0].url : null, sources:sources})
            return [metaRawData,chunkValue.payload,null]
        }
        /*
        if (chunkValue.payload?.sources!=null) {
            metaData = chunkValue.payload
        } else {*/
        if(metaData && chunkValue.type=="web_search"){
            chat.removeMessage(loading_msg.id)
            //console.log("metadata",chunkValue,metaData)
            const sources = metaData.sources
            let reply = message.text + chunkValue.payload.response
            for (let i=0; i<sources.length; i++){
                const key = "WSD-#"+(i+1)
                if (reply.includes(key))
                    reply = reply.replaceAll(key,"["+(i+1)+"]("+sources[i].url+")")
            }
            message.speech = speech
            message.text = reply
            console.log(message)
            chat.addMessage({...message,...metaData})
        }
        //}
        return [metaRawData,metaData,null]
    }

    async calendar(){
        try{
            const executor = http.get("api/calendar")
            const res = await executor.execute()
            const payload = await res.json()
            const calendar = useCalendar()
            calendar.clearTasks()
            for (const task of payload.tasks)
                calendar.addTask(task)

            calendar.clearForecasts()
            for (const forecast of payload.forecasts)
                calendar.addForecast(forecast)
        }catch (e){
            console.error(e)
            ElNotification({
                title: 'Oops something went wrong!!!',
                message: String(e),
                type: 'error',
                duration: 9000
            })
        }
    }
}

export default new ChatRepository()
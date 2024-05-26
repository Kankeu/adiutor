import {defineStore} from 'pinia'
import {nextTick, reactive} from "vue";

export const useCalendar = defineStore('calendar', {
    state: () => ({
        tasks: [],
        forecasts:[]
    }),
    actions: {
        addTask(task) {
            const i = this.tasks.findIndex(t => t.id == task.id)
            if (i >= 0) {
                this.tasks.splice(i, 1)
                nextTick(() => {
                    this.tasks.splice(i, 0, task)
                })
            } else {
                this.tasks.push(task)
            }
        },
        clearTasks() {
            this.tasks = []
        },
        addForecast(forecast) {
            const i = this.forecasts.findIndex(f => f.date == forecast.date)
            if (i >= 0) {
                this.forecasts.splice(i, 1)
                nextTick(() => {
                    this.forecasts.splice(i, 0, forecast)
                })
            } else this.forecasts.push(forecast)
        },
        clearForecasts() {
            this.forecasts = []
        },
    },
})
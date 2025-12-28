import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import tooltip from './directives/tooltip'
import VueApexCharts from "vue3-apexcharts"

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueApexCharts)
app.directive('tooltip', tooltip) // Register global directive

app.mount('#app')

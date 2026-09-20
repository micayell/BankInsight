// ⚠️ Bootstrap & Icons CSS는 main.js에서 한 번만 import 해주세요:
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './index.js'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.mount('#app')

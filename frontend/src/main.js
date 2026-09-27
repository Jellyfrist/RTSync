import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

// Start the Vue application with the router and global stylesheet.
createApp(App).use(router).mount('#app')

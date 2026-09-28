// ไฟล์เริ่มต้นของ frontend สำหรับสร้าง Vue application และติดตั้ง router
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./styles/index.css";

// เริ่มต้น Vue application พร้อม router และ global stylesheet
createApp(App).use(router).mount("#app");

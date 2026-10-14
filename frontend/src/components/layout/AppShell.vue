<!-- โครงหน้าร่วมของทุกหน้า เช่น sidebar, header และพื้นที่เนื้อหา -->
<script setup>
import { ref, watch } from "vue";
import AppHeader from "./AppHeader.vue";
import AppSidebar from "./AppSidebar.vue";
import AppFooter from "./AppFooter.vue";
import { USE_MOCK } from "../../api/httpClient";

defineProps({});

// สถานะการยุบหรือขยาย sidebar ของทั้ง layout
const sidebarCollapsed = ref(
  localStorage.getItem("rtsync.sidebarCollapsed") === "true",
);
watch(sidebarCollapsed, (collapsed) => {
  localStorage.setItem("rtsync.sidebarCollapsed", String(collapsed));
});
</script>

<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <AppSidebar
      :collapsed="sidebarCollapsed"
      @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
    />
    <div class="app-content">
      <AppHeader />
      <main class="page-content">
        <div
          v-if="USE_MOCK"
          role="status"
          style="margin-bottom: 16px; padding: 12px 16px; border: 1px solid #bad4ed; border-radius: 8px; background: #eff6ff; color: #173e70; font-size: 14px;"
        >
          โหมดสาธิตสาธารณะ — ใช้ข้อมูลตัวอย่างที่เก็บในเบราว์เซอร์ของคุณ
          ไม่มีการบันทึกข้อมูลลง Supabase และไม่ต้องเข้าสู่ระบบ
        </div>
        <slot />
      </main>
      <AppFooter />
    </div>
  </div>
</template>

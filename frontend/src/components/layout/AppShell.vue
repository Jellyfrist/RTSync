<!-- โครงหน้าร่วมของทุกหน้า เช่น sidebar, header และพื้นที่เนื้อหา -->
<script setup>
import { ref, watch } from "vue";
import AppHeader from "./AppHeader.vue";
import AppSidebar from "./AppSidebar.vue";
import AppFooter from "./AppFooter.vue";

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
      <main class="page-content"><slot /></main>
      <AppFooter />
    </div>
  </div>
</template>

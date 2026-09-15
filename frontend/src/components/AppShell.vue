<!-- โครงหน้าร่วมของทุกหน้า เช่น sidebar, header และพื้นที่เนื้อหา -->
<script setup>
import { ref } from "vue";
import AppHeader from "./AppHeader.vue";
import AppSidebar from "./AppSidebar.vue";

defineProps({ placeholder: String });

// สถานะการยุบหรือขยาย sidebar ของทั้ง layout
const sidebarCollapsed = ref(false);
</script>

<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <AppSidebar :collapsed="sidebarCollapsed" />
    <div class="app-content">
      <AppHeader
        :placeholder="placeholder"
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
      />
      <main class="page-content"><slot /></main>
    </div>
  </div>
</template>

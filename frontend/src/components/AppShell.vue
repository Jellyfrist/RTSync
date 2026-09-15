<!-- โครงหน้าร่วมของทุกหน้า เช่น sidebar, header และพื้นที่เนื้อหา -->
<script setup>
import AppHeader from "./AppHeader.vue";
import AppSidebar from "./AppSidebar.vue";

defineProps({ placeholder: String });
</script>

<template>
  <div class="app-shell">
    <AppSidebar />
    <div class="app-content">
      <AppHeader :placeholder="placeholder" />
      <main class="page-content"><slot /></main>
    </div>
  </div>
</template>

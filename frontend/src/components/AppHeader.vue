<script setup>
import { ref } from 'vue'
import SvgIcon from './SvgIcon.vue'

defineProps({ placeholder: { type: String, default: 'ค้นหาข้อมูลในระบบ...' } })
const query = ref('')
</script>

<template>
  <!-- Shared header with search and system status -->
  <header class="app-header"><div class="header-search"><SvgIcon name="search"/><input v-model="query" :placeholder="placeholder" aria-label="ค้นหา"/></div><div class="header-actions"><span class="online-status">ระบบออนไลน์ (ONLINE)</span><button class="icon-button" title="การแจ้งเตือน"><span class="notification-dot">3</span><SvgIcon name="grid"/></button><div class="avatar"><SvgIcon name="user" size="17"/></div></div></header>
</template>

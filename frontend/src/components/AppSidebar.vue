<script setup>
import { RouterLink } from 'vue-router'
import SvgIcon from './SvgIcon.vue'

const items = [
  { to: '/customers', label: 'ใบเสนอราคา & ลูกค้า', icon: 'quote' },
  { to: '/inventory', label: 'สินค้า & คลังอุปกรณ์', icon: 'box' },
  { to: '/suppliers', label: 'ซัพพลายเออร์ & สั่งซื้อ', icon: 'truck' },
  { to: '/installations', label: 'ขาย · ติดตั้ง · บริการ', icon: 'solar' },
  { to: '/payroll', label: 'ค่าตอบแทน & OT พนักงาน', icon: 'wallet' }
]
</script>

<template>
  <!-- เมนูหลักที่ใช้ร่วมกันทุกหน้า -->
  <aside class="app-sidebar">
    <div class="brand"><span class="brand-mark">RT</span><div><strong>RT Sync</strong><small>SOLAR WORKBENCH</small></div></div>
    <div class="sidebar-scroll">
      <span class="section-label">ฝ่ายปฏิบัติการ & คลังสินค้า</span>
      <nav class="sidebar-nav">
        <RouterLink v-for="item in items" :key="item.to" :to="item.to" active-class="active"><SvgIcon :name="item.icon"/><span>{{ item.label }}</span></RouterLink>
      </nav>
      <span class="section-label section-label-spaced">การจัดการระบบ</span>
      <RouterLink to="/" class="sidebar-link"><SvgIcon name="settings"/><span>ตั้งค่าระบบ</span></RouterLink>
    </div>
    <div class="user-panel"><div class="avatar"><SvgIcon name="user" size="17"/></div><div><strong>ธีรภัทร วิจิตรวงศ์</strong><small>วิศวกรคลังสินค้า Lead</small></div></div>
  </aside>
</template>

<!-- เมนูด้านข้างสำหรับเปลี่ยนไปยังโมดูลต่าง ๆ -->
<script setup>
import { RouterLink } from "vue-router";
import SvgIcon from "./SvgIcon.vue";

const props = defineProps({ collapsed: { type: Boolean, default: false } });

const items = [
  { to: "/customers", label: "ใบเสนอราคา & ลูกค้า", icon: "quote" },
  { to: "/inventory", label: "สินค้า & คลังอุปกรณ์", icon: "box" },
  { to: "/suppliers", label: "ซัพพลายเออร์ & สั่งซื้อ", icon: "truck" },
  { to: "/installations", label: "ขาย · ติดตั้ง · บริการ", icon: "solar" },
  { to: "/payroll", label: "ค่าตอบแทน & OT พนักงาน", icon: "wallet" },
];
</script>

<template>
  <!-- เมนูหลักที่ใช้ร่วมกันทุกหน้า -->
  <aside class="app-sidebar">
    <div class="brand">
      <span class="brand-mark">RT</span>
      <div><strong>RTSync</strong><small>SOLAR WORKBENCH</small></div>
    </div>
    <div class="sidebar-scroll">
      <span class="section-label">เมนูหลัก</span>
      <nav class="sidebar-nav">
        <RouterLink
          v-for="item in items"
          :key="item.to"
          :to="item.to"
          :aria-label="item.label"
          :title="props.collapsed ? item.label : undefined"
          active-class="active"
          ><SvgIcon :name="item.icon" /><span>{{
            item.label
          }}</span></RouterLink
        >
      </nav>
    </div>
    <div class="user-panel">
      <div class="avatar"><SvgIcon name="user" size="17" /></div>
      <div>
        <strong>ธีรภัทร วิจิตรวงศ์</strong><small>วิศวกรคลังสินค้า Lead</small>
      </div>
    </div>
  </aside>
</template>

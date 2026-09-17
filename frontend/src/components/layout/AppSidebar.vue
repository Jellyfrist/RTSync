<!-- เมนูด้านข้างสำหรับเปลี่ยนไปยังโมดูลต่าง ๆ -->
<script setup>
import { RouterLink } from "vue-router";
import SvgIcon from "../SvgIcon.vue";

const props = defineProps({ collapsed: { type: Boolean, default: false } });
const emit = defineEmits(["toggle-sidebar"]);

const groups = [
  {
    label: "ข้อมูลตั้งต้น",
    items: [
      { to: "/inventory", label: "คลังสินค้า", icon: "box" },
      { to: "/suppliers", label: "ซัพพลายเออร์", icon: "truck" },
    ],
  },
  {
    label: "ลูกค้าและการขาย",
    items: [
      { to: "/sales", label: "การขาย & ใบเสนอราคา", icon: "quote" },
      { to: "/customers", label: "ลูกค้า", icon: "user" },
    ],
  },
  {
    label: "งานหน้างาน",
    items: [
      { to: "/installations", label: "การติดตั้ง", icon: "solar" },
      { to: "/service", label: "บริการหลังการขาย", icon: "headset" },
      { to: "/fuel-claims", label: "เบิกค่าน้ำมัน", icon: "wallet" },
    ],
  },
  {
    label: "ทีมงาน",
    items: [{ to: "/payroll", label: "ข้อมูลพนักงาน", icon: "briefcase" }],
  },
];
</script>

<template>
  <!-- เมนูหลักที่ใช้ร่วมกันทุกหน้า -->
  <aside id="primary-navigation" class="app-sidebar" aria-label="เมนูด้านข้าง">
    <div class="sidebar-topbar">
      <button
        class="icon-button sidebar-toggle"
        type="button"
        :aria-label="props.collapsed ? 'ขยายเมนูด้านข้าง' : 'ยุบเมนูด้านข้าง'"
        :title="props.collapsed ? 'ขยายเมนูด้านข้าง' : 'ยุบเมนูด้านข้าง'"
        :aria-expanded="!props.collapsed"
        aria-controls="primary-navigation"
        @click="emit('toggle-sidebar')"
      >
        <SvgIcon :name="props.collapsed ? 'menu' : 'chevron-left'" />
      </button>
    </div>
    <div class="sidebar-scroll">
      <div v-for="group in groups" :key="group.label" class="sidebar-group">
        <span class="section-label sidebar-group-label">{{ group.label }}</span>
        <nav class="sidebar-nav" :aria-label="group.label">
          <RouterLink
            v-for="item in group.items"
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
    </div>
  </aside>
</template>

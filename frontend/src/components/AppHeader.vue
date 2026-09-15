<!-- ส่วนหัวระบบที่แสดงช่องค้นหา สถานะระบบ และการแจ้งเตือน -->
<script setup>
import { ref } from "vue";
import SvgIcon from "./SvgIcon.vue";

defineProps({ placeholder: { type: String, default: "ค้นหาข้อมูลในระบบ..." } });
const query = ref("");
const showNotifications = ref(false);
const notifications = [
  {
    title: "สินค้าต่ำกว่า Reorder Point",
    detail: "Huawei SUN2000-5KTL เหลือ 12 เครื่อง · จุดสั่งซื้อ 15",
    time: "เมื่อ 10 นาทีที่แล้ว",
    tone: "warning",
  },
  {
    title: "นัดหมายรอยืนยัน 2 รายการ",
    detail: "มีงานติดตั้งวันที่ 20 มิ.ย. ต้องยืนยันกับลูกค้า",
    time: "เมื่อ 32 นาทีที่แล้ว",
    tone: "info",
  },
  {
    title: "ใบงานบริการใหม่",
    detail: "Monitoring ไม่ส่งข้อมูล · คุณกมลชนก สุขใจ",
    time: "เมื่อ 1 ชม.ที่แล้ว",
    tone: "danger",
  },
];
</script>

<template>
  <!-- Header กลางพร้อมช่องค้นหาและสถานะระบบ -->
  <header class="app-header">
    <div class="header-search">
      <SvgIcon name="search" /><input
        v-model="query"
        :placeholder="placeholder"
        aria-label="ค้นหา"
      />
    </div>
    <div class="header-actions">
      <span class="online-status">ระบบออนไลน์ (ONLINE)</span
      ><button
        class="icon-button notification-button"
        :aria-expanded="showNotifications"
        aria-label="การแจ้งเตือน"
        title="การแจ้งเตือน"
        @click="showNotifications = !showNotifications"
      >
        <span class="notification-dot">3</span><SvgIcon name="grid" />
      </button>
      <div v-if="showNotifications" class="notification-panel">
        <div class="notification-heading">
          <strong>การแจ้งเตือน</strong><small>3 รายการที่ต้องติดตาม</small>
        </div>
        <article
          v-for="item in notifications"
          :key="item.title"
          class="notification-item"
        >
          <span :class="['notification-icon', item.tone]"
            ><SvgIcon name="settings" size="15"
          /></span>
          <div>
            <strong>{{ item.title }}</strong>
            <p>{{ item.detail }}</p>
            <small>{{ item.time }}</small>
          </div>
        </article>
        <button class="notification-footer" @click="showNotifications = false">
          ดูงานที่ต้องติดตามทั้งหมด
        </button>
      </div>
      <div class="avatar"><SvgIcon name="user" size="17" /></div>
    </div>
  </header>
</template>

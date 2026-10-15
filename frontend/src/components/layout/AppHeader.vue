<!-- ส่วนหัวระบบกลางที่ใช้ร่วมกันทุกหน้า -->
<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { authEnabled, currentUser as sessionUser, logout } from "@/api/authSession";
import SvgIcon from "../SvgIcon.vue";

const router = useRouter();
const userMenuOpen = ref(false);
const currentUser = computed(() => ({
  name: authEnabled.value ? (sessionUser.value?.name || "RTSync User") : "RTSync",
  username: authEnabled.value ? (sessionUser.value?.email || "") : "Vercel protected",
  role: authEnabled.value
    ? (sessionUser.value?.role === "owner" ? "เจ้าของร้าน" : "พนักงาน")
    : "Restricted Access",
  organization: "RTSat",
}));
async function signOut() {
  userMenuOpen.value = false;
  if (authEnabled.value) {
    await logout();
    await router.replace("/login");
  }
}
</script>

<template>
  <header class="app-header">
    <div class="header-brand" aria-label="RTSync">
      <span class="header-brand-mark"
        ><SvgIcon class="brand-logo" name="rtsync-logo" size="36"
      /></span>
      <strong>RTSync</strong>
    </div>
    <div class="header-actions">
      <div class="user-menu">
        <button
          class="user-menu-trigger"
          type="button"
          aria-label="เปิดเมนูผู้ใช้"
          :aria-expanded="userMenuOpen"
          @click="userMenuOpen = !userMenuOpen"
        >
          <span class="user-menu-copy">
            <strong>{{ currentUser.name }}</strong>
            <small>{{ currentUser.username }} · {{ currentUser.role }}</small>
          </span>
          <span class="avatar"><SvgIcon name="user" size="17" /></span>
        </button>
        <div v-if="userMenuOpen" class="user-menu-popover" role="menu">
          <div class="user-menu-heading">
            <strong>{{ currentUser.name }}</strong>
            <small>{{ currentUser.username }}</small>
            <small class="user-menu-role"
              >{{ currentUser.role }} · {{ currentUser.organization }}</small
            >
          </div>
          <button
            class="user-menu-item"
            type="button"
            role="menuitem"
            v-if="authEnabled"
            @click="signOut"
          >
            <SvgIcon name="close" size="16" />ออกจากระบบ
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { loadCurrentUser } from "@/api/authSession";

const router = useRouter();
const route = useRoute();
const username = ref("");
const password = ref("");
const busy = ref(false);
const error = ref("");
const errorMessage = computed(() => error.value || (route.query.error ? "กรุณาเข้าสู่ระบบใหม่" : ""));
async function login() {
  if (busy.value) return;
  busy.value = true;
  error.value = "";
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.value, password: password.value }),
    });
    if (!response.ok) {
      const message = await response.json().catch(() => ({}));
      throw new Error(typeof message.detail === "string" ? message.detail : "เข้าสู่ระบบไม่สำเร็จ");
    }
    await loadCurrentUser();
    const dest = typeof route.query.returnTo === "string" &&
      route.query.returnTo.startsWith("/") && !route.query.returnTo.startsWith("//")
      ? route.query.returnTo : "/customers";
    await router.replace(dest);
  } catch (e) {
    error.value = e.message || "ไม่สามารถเข้าสู่ระบบได้";
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <main class="login-screen">
    <section class="login-card">
      <div class="login-mark">RT</div>
      <h1>RTSync</h1>
      <p class="subtitle">ระบบจัดการธุรกิจ RTSat</p>
      <h2>เข้าสู่ระบบ</h2>
      <p>เข้าสู่ระบบด้วยบัญชีที่ได้รับอนุญาตจาก RTSync</p>
      <form @submit.prevent="login">
        <label class="field-label" for="username">ชื่อผู้ใช้</label>
        <input id="username" v-model.trim="username" name="username" autocomplete="username" required />
        <label class="field-label" for="password">รหัสผ่าน</label>
        <input id="password" v-model="password" type="password" name="password" autocomplete="current-password" required />
        <p v-if="errorMessage" class="login-error" role="alert">{{ errorMessage }}</p>
        <button type="submit" class="login-button" :disabled="busy">
          {{ busy ? "กำลังเข้าสู่ระบบ..." : "เข้าสู่ระบบ" }}
        </button>
      </form>
      <small>สำหรับเจ้าของร้านและพนักงานที่ได้รับอนุญาต</small>
    </section>
  </main>
</template>

<style scoped>
.login-screen {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 20px;
  background: #f4f7fc;
  font-family: inherit;
}
.login-card {
  box-sizing: border-box;
  width: min(440px, 100%);
  padding: 42px 34px;
  background: #fff;
  border: 1px solid #d9e3f2;
  border-radius: 16px;
  box-shadow: 0 14px 48px rgba(29, 63, 132, 0.09);
  text-align: center;
  color: #172e53;
}
.login-mark {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  margin: 0 auto 14px;
  color: white;
  background: #193a87;
  font-size: 19px;
  font-weight: bold;
}
h1 { font-size: 27px; margin: 0 0 3px; }
h2 { font-size: 21px; margin: 26px 0 12px; }
.subtitle, p, small { color: #596a85; }
p { line-height: 1.65; }
.login-error {
  color: #9a2323;
  padding: 12px;
  border-radius: 8px;
  background: #fff2f2;
}
.login-button {
  width: 100%;
  padding: 13px 18px;
  margin: 16px 0 22px;
  border: 1px solid #9cadca;
  border-radius: 9px;
  background: white;
  color: #16315e;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}
.login-button:hover { background: #f2f6ff; }
.google-g { color: #4285f4; font-size: 22px; font-weight: 800; margin-right: 10px; }
</style>

<style scoped>
.field-label { display:block; text-align:left; font-weight:600; margin:14px 0 6px; }
input { box-sizing:border-box; display:block; width:100%; padding:12px; border:1px solid #a7b8cc; border-radius:8px; font:inherit; }
.login-button:disabled { opacity:.6; cursor:wait; }
</style>

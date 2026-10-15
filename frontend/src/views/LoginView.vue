<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const errorMessage = computed(() => {
  const messages = {
    oauth: "Google Login ไม่สำเร็จ กรุณาลองอีกครั้ง",
    not_approved: "บัญชีนี้ยังไม่ได้รับอนุญาตให้ใช้งาน RTSync",
  };
  return messages[route.query.error] || (route.query.error ? "ไม่สามารถเข้าสู่ระบบได้ กรุณาลองใหม่" : "");
});
function login() {
  // Google OAuth starts on FastAPI. No API key or access token is in frontend JS.
  window.location.assign("/api/auth/google");
}
</script>

<template>
  <main class="login-screen">
    <section class="login-card">
      <div class="login-mark">RT</div>
      <h1>RTSync</h1>
      <p class="subtitle">ระบบจัดการธุรกิจ RTSat</p>
      <h2>เข้าสู่ระบบ</h2>
      <p>ใช้บัญชี Google ที่ได้รับอนุญาต เพื่อเข้าถึงระบบจัดการงานเดิมของ RTSync</p>
      <p v-if="errorMessage" class="login-error" role="alert">{{ errorMessage }}</p>
      <button type="button" class="login-button" @click="login">
        <span class="google-g">G</span> ดำเนินการต่อด้วย Google
      </button>
      <small>หากไม่มีสิทธิ์เข้าใช้งาน กรุณาติดต่อผู้ดูแลระบบ</small>
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

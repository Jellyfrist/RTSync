// ฟังก์ชันช่วยควบคุมการเปิดและปิด modal ที่ใช้ร่วมกันหลายหน้า
import { ref } from "vue";

// จัดการสถานะเปิดปิด dialog ที่ใช้ในหลายหน้า
export function useModal() {
  const isOpen = ref(false);
  const open = () => {
    isOpen.value = true;
  };
  const close = () => {
    isOpen.value = false;
  };
  return { isOpen, open, close };
}

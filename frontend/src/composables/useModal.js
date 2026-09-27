import { ref } from 'vue'

// Manage dialog open and close state shared by several pages.
export function useModal() {
  const isOpen = ref(false)
  const open = () => { isOpen.value = true }
  const close = () => { isOpen.value = false }
  return { isOpen, open, close }
}

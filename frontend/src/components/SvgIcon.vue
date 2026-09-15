<!-- คอมโพเนนต์ไอคอน SVG ที่ใช้ร่วมกันทั้งระบบ -->
<script setup>
defineProps({
  name: { type: String, default: "grid" },
  size: { type: [Number, String], default: 18 },
});
</script>

<template>
  <!-- Icon กลางที่ใช้ SVG เท่านั้น เพื่อให้ทุกหน้ามีชุด icon เดียวกัน -->
  <svg
    class="svg-icon"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.9"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <template v-if="name === 'search'">
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-4-4" />
    </template>
    <template v-else-if="name === 'grid'">
      <rect x="4" y="4" width="6" height="6" />
      <rect x="14" y="4" width="6" height="6" />
      <rect x="4" y="14" width="6" height="6" />
      <rect x="14" y="14" width="6" height="6" />
    </template>
    <template v-else-if="name === 'box'">
      <path d="m4 7 8-4 8 4v10l-8 4-8-4Z" />
      <path d="m4 7 8 4 8-4M12 11v10" />
    </template>
    <template v-else-if="name === 'truck'">
      <path d="M3 6h11v10H3zM14 10h4l3 3v3h-7z" />
      <circle cx="7" cy="18" r="2" />
      <circle cx="18" cy="18" r="2" />
    </template>
    <template v-else-if="name === 'quote'">
      <path d="M5 4h14v16H5z" />
      <path d="M8 8h8M8 12h6M8 16h4" />
    </template>
    <template v-else-if="name === 'solar'">
      <circle cx="12" cy="12" r="3" />
      <path
        d="M12 2v3M12 19v3M4.9 4.9 7 7M17 17l2.1 2.1M2 12h3M19 12h3M4.9 19.1 7 17M17 7l2.1-2.1"
      />
    </template>
    <template v-else-if="name === 'wallet'">
      <path d="M4 6h15a1 1 0 0 1 1 1v11H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h13" />
      <path d="M16 12h4v4h-4a2 2 0 1 1 0-4Z" />
    </template>
    <template v-else-if="name === 'settings'">
      <path d="M12 15.2a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4Z" />
      <path
        d="m19.4 15 .1.1a2 2 0 0 1-2.8 2.8l-.1-.1a2 2 0 0 0-3.4 1.4v.2a2 2 0 0 1-4 0v-.2a2 2 0 0 0-3.4-1.4l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A2 2 0 0 0 1.6 12h-.2a2 2 0 0 1 0-4h.2A2 2 0 0 0 3 4.6l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A2 2 0 0 0 9.2.4h.2a2 2 0 0 1 4 0v.2a2 2 0 0 0 3.4 1.4l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1A2 2 0 0 0 21 8h.2a2 2 0 0 1 0 4H21a2 2 0 0 0-1.6 3Z"
      />
    </template>
    <template v-else-if="name === 'close'">
      <path d="m6 6 12 12M18 6 6 18" />
    </template>
    <template v-else-if="name === 'plus'">
      <path d="M12 5v14M5 12h14" />
    </template>
    <template v-else-if="name === 'download'">
      <path d="M12 3v12M7 10l5 5 5-5M4 21h16" />
    </template>
    <template v-else-if="name === 'user'">
      <circle cx="12" cy="8" r="3" />
      <path d="M5 21a7 7 0 0 1 14 0" />
    </template>
    <template v-else-if="name === 'edit'">
      <path d="m4 16-.8 4.8L8 20l11-11-4-4Z" />
      <path d="m13 6 4 4" />
    </template>
    <template v-else-if="name === 'check'">
      <path d="m5 12 4 4L19 6" />
    </template>
    <template v-else><circle cx="12" cy="12" r="8" /></template>
  </svg>
</template>

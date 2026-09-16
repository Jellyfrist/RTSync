<script setup>
import { computed, ref, watch } from "vue";
import SvgIcon from "@/components/SvgIcon.vue";

const props = defineProps({
  total: { type: Number, default: 0 },
  label: { type: String, default: "รายการ" },
});

const page = ref(1);
const pageSize = ref(10);
const totalPages = computed(() => Math.max(1, Math.ceil(props.total / pageSize.value)));
const start = computed(() => (props.total ? (page.value - 1) * pageSize.value + 1 : 0));
const end = computed(() => Math.min(page.value * pageSize.value, props.total));

watch([() => props.total, pageSize], () => {
  page.value = Math.min(page.value, totalPages.value);
});
</script>

<template>
  <nav class="table-pagination" :aria-label="`การแบ่งหน้า${label}`">
    <p>แสดง {{ start }}–{{ end }} จาก {{ total }} {{ label }}</p>
    <div class="pagination-controls">
      <label>
        <span>แถวต่อหน้า</span>
        <select v-model="pageSize" aria-label="จำนวนแถวต่อหน้า">
          <option :value="10">10</option>
          <option :value="25">25</option>
          <option :value="50">50</option>
        </select>
      </label>
      <div class="page-navigation" aria-label="เปลี่ยนหน้า">
        <button type="button" :disabled="page === 1" aria-label="หน้าก่อนหน้า" @click="page -= 1">
          <SvgIcon name="chevron-left" :size="16" />
        </button>
        <span aria-current="page">{{ page }}</span>
        <button type="button" :disabled="page === totalPages" aria-label="หน้าถัดไป" @click="page += 1">
          <SvgIcon name="chevron-right" :size="16" />
        </button>
      </div>
    </div>
  </nav>
</template>

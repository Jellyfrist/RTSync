<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import SvgIcon from "@/components/SvgIcon.vue";

const props = defineProps({
  total: { type: Number, default: 0 },
  label: { type: String, default: "รายการ" },
});

const page = ref(1);
const pageSize = ref(10);
const paginationRoot = ref(null);
let tableObserver;
const pageSizeValue = computed(() =>
  Math.min(1000, Math.max(1, Number(pageSize.value) || 1)),
);
const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.total / pageSizeValue.value)),
);
const start = computed(() =>
  props.total ? (page.value - 1) * pageSizeValue.value + 1 : 0,
);
const end = computed(() =>
  Math.min(page.value * pageSizeValue.value, props.total),
);

function commitPageSize() {
  pageSize.value = pageSizeValue.value;
  page.value = 1;
}
function findTable() {
  let parent = paginationRoot.value?.parentElement;
  while (parent) {
    const tables = [...parent.querySelectorAll("table")].filter((table) => {
      const position = table.compareDocumentPosition(paginationRoot.value);
      return position & Node.DOCUMENT_POSITION_FOLLOWING;
    });
    if (tables.length) return tables.at(-1);
    parent = parent.parentElement;
  }
  return null;
}
function applyPagination() {
  const table = findTable();
  if (!table) return;
  const rowGroups = [];
  [...table.querySelectorAll(":scope > tbody > tr")].forEach((row) => {
    const isDetailRow = row.className.includes("detail-row");
    if (isDetailRow && rowGroups.length) rowGroups.at(-1).push(row);
    else rowGroups.push([row]);
  });
  const firstVisible = (page.value - 1) * pageSizeValue.value;
  rowGroups.forEach((group, index) => {
    const hidden =
      index < firstVisible || index >= firstVisible + pageSizeValue.value;
    group.forEach((row) => {
      row.hidden = hidden;
    });
  });
}
function refreshPagination() {
  nextTick(applyPagination);
}
watch([() => props.total, pageSize, page], () => {
  page.value = Math.min(page.value, totalPages.value);
  refreshPagination();
});
onMounted(() => {
  refreshPagination();
  tableObserver = new MutationObserver(refreshPagination);
  const parent = paginationRoot.value?.parentElement;
  if (parent) tableObserver.observe(parent, { childList: true, subtree: true });
});
onBeforeUnmount(() => tableObserver?.disconnect());
</script>

<template>
  <nav
    ref="paginationRoot"
    class="table-pagination"
    :aria-label="`การแบ่งหน้า${label}`"
  >
    <p>แสดง {{ start }}–{{ end }} จาก {{ total }} {{ label }}</p>
    <div class="pagination-controls">
      <label class="page-size-control">
        <span>แถวต่อหน้า</span>
        <input
          class="page-size-field"
          v-model.number="pageSize"
          type="number"
          min="1"
          max="1000"
          inputmode="numeric"
          aria-label="จำนวนแถวต่อหน้า"
          @change="commitPageSize"
          @blur="commitPageSize"
        />
      </label>
      <div class="page-navigation" aria-label="เปลี่ยนหน้า">
        <button
          type="button"
          :disabled="page === 1"
          aria-label="หน้าก่อนหน้า"
          @click="page -= 1"
        >
          <SvgIcon name="chevron-left" :size="16" />
        </button>
        <span aria-current="page">{{ page }}</span>
        <button
          type="button"
          :disabled="page === totalPages"
          aria-label="หน้าถัดไป"
          @click="page += 1"
        >
          <SvgIcon name="chevron-right" :size="16" />
        </button>
      </div>
    </div>
  </nav>
</template>

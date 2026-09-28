// ฟังก์ชันช่วยค้นหารายการจากหลายฟิลด์ของข้อมูล
import { computed, ref } from "vue";

// กรองรายการตาม keyword โดยไม่ต้องควบคุม DOM โดยตรง
export function useSearch(items, fields = ["name"]) {
  const query = ref("");
  const filteredItems = computed(() => {
    const keyword = query.value.trim().toLowerCase();
    if (!keyword) return items.value;
    return items.value.filter((item) =>
      fields.some((field) =>
        String(item[field] ?? "")
          .toLowerCase()
          .includes(keyword),
      ),
    );
  });
  return { query, filteredItems };
}

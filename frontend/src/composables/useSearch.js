import { computed, ref } from 'vue'

// Filter records by a keyword without controlling the DOM directly.
export function useSearch(items, fields = ['name']) {
  const query = ref('')
  const filteredItems = computed(() => {
    const keyword = query.value.trim().toLowerCase()
    if (!keyword) return items.value
    return items.value.filter(item => fields.some(field => String(item[field] ?? '').toLowerCase().includes(keyword)))
  })
  return { query, filteredItems }
}

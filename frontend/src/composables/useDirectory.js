import { computed, ref } from 'vue';
import { useSearch } from './useSearch.js';

/** Each controller invocation owns its selection and query. */
export function useDirectory(repository, fields = ['name']) {
  const items = ref(repository.list());
  const selectedId = ref(items.value[0]?.id ?? null);
  const selectedItem = computed(() => items.value.find((item) => item.id === selectedId.value));
  const { query, filteredItems } = useSearch(items, fields);
  const select = (id) => { selectedId.value = id; };
  return { items, selectedId, selectedItem, query, filteredItems, select };
}

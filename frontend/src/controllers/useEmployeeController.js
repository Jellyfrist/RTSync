import { ref } from 'vue';
import { repositories } from '../repositories/index.js';
import { useDirectory } from '../composables/useDirectory.js';

export function useEmployeeController({ repository = repositories.employees } = {}) {
  const {
    items: employees, selectedId: activeId, selectedItem: activeEmployee,
    query: search, filteredItems: visibleEmployees,
  } = useDirectory(repository, ['id', 'name', 'role']);
  const collapsed = ref(false);
  return { employees, activeId, collapsed, search, visibleEmployees, activeEmployee };
}

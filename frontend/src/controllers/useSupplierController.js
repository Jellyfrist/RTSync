import { useModal } from '../composables/useModal.js';
import { repositories } from '../repositories/index.js';
import { useDirectory } from '../composables/useDirectory.js';

export function useSupplierController({ repository = repositories.suppliers } = {}) {
  const {
    items: suppliers, selectedId, selectedItem: selectedSupplier,
    query: filter, filteredItems: visibleSuppliers,
  } = useDirectory(repository, ['name', 'category']);
  const { isOpen, open, close } = useModal();
  return { suppliers, selectedId, filter, isOpen, open, close, visibleSuppliers, selectedSupplier };
}

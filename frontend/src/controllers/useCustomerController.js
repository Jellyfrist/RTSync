import { ref, computed } from "vue";
import { useModal } from "../composables/useModal.js";
import { useDirectory } from '../composables/useDirectory.js';
import { repositories } from '../repositories/index.js';

export function useCustomerController({ repository = repositories.customers, notify = (message) => window.alert(message) } = {}) {
  const { items: customers, selectedId: activeId, selectedItem: selectedCustomer, select: selectCustomer } = useDirectory(repository);
  const selectedType = ref("ทั้งหมด");
  const { isOpen, open, close } = useModal();
  const visibleCustomers = computed(() =>
    selectedType.value === "ทั้งหมด"
      ? customers.value
      : customers.value.filter(
          (customer) =>
            customer.type === selectedType.value ||
            (selectedType.value === "รอนัดตรวจเช็ก" &&
              customer.status === selectedType.value),
        ),
  );

  // Keep the old new-customer button behavior through a reactive dialog.
  const showNotice = (message) => notify(message);
  return { customers, activeId, selectedType, isOpen, open, close, selectedCustomer, visibleCustomers, selectCustomer, showNotice };
}

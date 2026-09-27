import { computed, ref } from 'vue';
import { api } from '../api/client.js';

export function useProcurementController(client = api) {
  const suppliers = ref([]);
  const products = ref([]);
  const orders = ref([]);
  const selectedId = ref(null);
  const history = ref({ events: [], receipts: [] });
  const actor = ref('');
  const supplierForm = ref({ name: '', category: '', delivery: '' });
  const linkForm = ref({ supplier_id: '', product_sku: '' });
  const orderForm = ref({ supplier_id: '', lines: [] });
  const lineForm = ref({ product_sku: '', quantity: 1 });
  const receiptReference = ref('');
  const receiptQuantities = ref({});
  const loading = ref(false);
  const error = ref('');
  const message = ref('');
  const selectedOrder = computed(() => orders.value.find(item => item.id === selectedId.value));

  async function run(operation) {
    loading.value = true;
    error.value = '';
    message.value = '';
    try { return await operation(); }
    catch (cause) { error.value = cause.message; return null; }
    finally { loading.value = false; }
  }

  async function refresh() {
    return run(async () => {
      [suppliers.value, products.value, orders.value] = await Promise.all([
        client.get('/suppliers'), client.get('/catalog/products'), client.get('/purchase-orders'),
      ]);
      if (selectedId.value && !orders.value.some(order => order.id === selectedId.value)) selectedId.value = null;
      if (!selectedId.value && orders.value.length) selectedId.value = orders.value[0].id;
      if (selectedId.value) history.value = await client.get(`/purchase-orders/${selectedId.value}/history`);
    });
  }

  async function selectOrder(id) {
    selectedId.value = id;
    receiptQuantities.value = {};
    return run(async () => { history.value = await client.get(`/purchase-orders/${id}/history`); });
  }

  function addLine() {
    const sku = lineForm.value.product_sku;
    const quantity = Number(lineForm.value.quantity);
    if (!sku || !Number.isInteger(quantity) || quantity <= 0) {
      error.value = 'Choose a product and enter a positive whole quantity.';
      return;
    }
    if (orderForm.value.lines.some(line => line.product_sku === sku)) {
      error.value = 'Each product can appear only once in an order.';
      return;
    }
    error.value = '';
    orderForm.value.lines.push({ product_sku: sku, quantity });
    lineForm.value = { product_sku: '', quantity: 1 };
  }

  function removeLine(sku) {
    orderForm.value.lines = orderForm.value.lines.filter(line => line.product_sku !== sku);
  }

  async function createSupplier() {
    if (!supplierForm.value.name.trim() || !supplierForm.value.category.trim() || !supplierForm.value.delivery.trim()) {
      error.value = 'Complete all supplier fields.';
      return;
    }
    const created = await run(() => client.post('/suppliers', supplierForm.value));
    if (created) {
      suppliers.value.push(created);
      orderForm.value.supplier_id = created.id;
      supplierForm.value = { name: '', category: '', delivery: '' };
      message.value = 'Supplier saved.';
    }
  }

  async function linkProduct() {
    const { supplier_id, product_sku } = linkForm.value;
    if (!supplier_id || !product_sku) { error.value = 'Choose a supplier and product.'; return; }
    const product = await run(() => client.post(`/suppliers/${supplier_id}/products/${product_sku}`, {}));
    if (product) {
      await refresh();
      linkForm.value.product_sku = '';
      message.value = 'Supplier and product linked.';
    }
  }

  async function createOrder() {
    if (!actor.value.trim() || !orderForm.value.supplier_id || !orderForm.value.lines.length) {
      error.value = 'Enter your name, choose a supplier, and add at least one product.';
      return;
    }
    const created = await run(() => client.post('/purchase-orders', { ...orderForm.value, actor: actor.value.trim() }));
    if (created) {
      orders.value.unshift(created);
      selectedId.value = created.id;
      orderForm.value = { supplier_id: '', lines: [] };
      history.value = await client.get(`/purchase-orders/${created.id}/history`);
      message.value = 'Purchase order created as a draft.';
    }
  }

  async function approve() {
    if (!selectedOrder.value || !actor.value.trim()) { error.value = 'Enter your name and select an order.'; return; }
    const updated = await run(() => client.post(`/purchase-orders/${selectedId.value}/approve`, { actor: actor.value.trim() }));
    if (updated) {
      orders.value = orders.value.map(order => order.id === updated.id ? updated : order);
      history.value = await client.get(`/purchase-orders/${updated.id}/history`);
      message.value = 'Purchase order approved.';
    }
  }

  async function receive() {
    const order = selectedOrder.value;
    const lines = order?.lines
      .map(line => ({ order_line_id: line.id, quantity: Number(receiptQuantities.value[line.id] || 0) }))
      .filter(line => line.quantity > 0) || [];
    if (!order || !actor.value.trim() || !receiptReference.value.trim() || !lines.length) {
      error.value = 'Enter your name, a receipt reference, and a received quantity.';
      return;
    }
    if (lines.some(line => !Number.isInteger(line.quantity))) { error.value = 'Received quantities must be whole numbers.'; return; }
    const receipt = await run(() => client.post(`/purchase-orders/${order.id}/receipts`, {
      actor: actor.value.trim(), reference: receiptReference.value.trim(), lines,
    }));
    if (receipt) {
      const updated = await client.get(`/purchase-orders/${order.id}`);
      orders.value = orders.value.map(item => item.id === updated.id ? updated : item);
      history.value = await client.get(`/purchase-orders/${order.id}/history`);
      receiptReference.value = '';
      receiptQuantities.value = {};
      message.value = 'Receipt saved and stock updated.';
    }
  }

  return { suppliers, products, orders, selectedId, selectedOrder, history, actor,
    supplierForm, linkForm, orderForm, lineForm, receiptReference, receiptQuantities,
    loading, error, message, refresh, selectOrder, addLine, removeLine, createSupplier, linkProduct, createOrder, approve, receive };
}

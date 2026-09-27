import test from 'node:test';
import assert from 'node:assert/strict';
import { Quote } from '../src/models/Quote.js';
import { InMemoryRepository } from '../src/repositories/InMemoryRepository.js';
import { useCustomerController } from '../src/controllers/useCustomerController.js';
import { useEmployeeController } from '../src/controllers/useEmployeeController.js';
import { useSupplierController } from '../src/controllers/useSupplierController.js';
import { useProductController } from '../src/controllers/useProductController.js';
import { useSalesController } from '../src/controllers/useSalesController.js';
import { useProcurementController } from '../src/controllers/useProcurementController.js';
import { ApiClient } from '../src/api/client.js';

test('quote merges lines, calculates totals, and does not mutate catalog records', () => {
  const product = { name: 'Panel', price: 4150, qty: 18, unit: 'panel' };
  const quote = new Quote();
  quote.add(product);
  quote.add(product);
  assert.equal(quote.items.length, 1);
  assert.equal(quote.total, 149400);
  assert.equal(product.qty, 18);
  quote.remove(-1);
  assert.equal(quote.items.length, 1);
  quote.remove(0);
  assert.equal(quote.total, 0);
});

test('quote rejects invalid prices and quantities without changing the draft', () => {
  const quote = new Quote();
  for (const [price, qty] of [[-1, 1], [NaN, 1], [Infinity, 1], [1, 0], [1, -1], [1, 1.5]]) {
    assert.throws(() => quote.add({ name: 'Invalid', price, qty }), RangeError);
  }
  assert.equal(quote.items.length, 0);
});

test('quote matches products by SKU and totals money in cents', () => {
  const quote = new Quote();
  quote.add({ sku: 'P-1', name: 'Panel', price: '0.10', qty: 1 });
  quote.add({ sku: 'P-1', name: 'Panel', price: '0.10', qty: 2 });
  quote.add({ sku: 'P-2', name: 'Panel', price: '0.20', qty: 1 });
  assert.equal(quote.items.length, 2);
  assert.equal(quote.total, 0.5);
});

test('repository copies input and output, including nested data', () => {
  const records = [{ id: 'a', details: { name: 'Original' } }];
  const repository = new InMemoryRepository(records);
  records[0].details.name = 'Changed';
  repository.list()[0].details.name = 'Also changed';
  assert.equal(repository.list()[0].details.name, 'Original');
});

test('customer filtering, selection, and modal state remain reactive and isolated', () => {
  const repository = new InMemoryRepository([
    { id: 'a', type: 'บ้านพักอาศัย', status: 'ชำระครบถ้วน' },
    { id: 'b', type: 'ธุรกิจ/โรงงาน', status: 'รอนัดตรวจเช็ก' },
  ]);
  const controller = useCustomerController({ repository });
  const other = useCustomerController({ repository });
  assert.equal(controller.selectedCustomer.value.id, 'a');
  controller.selectedType.value = 'รอนัดตรวจเช็ก';
  assert.deepEqual(controller.visibleCustomers.value.map(item => item.id), ['b']);
  controller.selectCustomer('b');
  assert.equal(controller.selectedCustomer.value.id, 'b');
  assert.equal(other.selectedCustomer.value.id, 'a');
  controller.open();
  assert.equal(controller.isOpen.value, true);
  assert.equal(other.isOpen.value, false);
  controller.close();
  assert.equal(controller.isOpen.value, false);
});

test('directory controllers accept empty data and custom repositories', () => {
  const repository = { list: () => [] };
  assert.equal(useCustomerController({ repository }).selectedCustomer.value, undefined);
  assert.equal(useEmployeeController({ repository }).activeEmployee.value, undefined);
  assert.equal(useSupplierController({ repository }).selectedSupplier.value, undefined);
  assert.deepEqual(useProductController({ repository }).filteredProducts.value, []);
});

test('employee and supplier search handle whitespace and case', () => {
  const repository = { list: () => [{ id: 'new', name: 'Alice', role: 'Engineer', category: 'Solar' }] };
  const employee = useEmployeeController({ repository });
  employee.search.value = ' ENGINEER ';
  assert.equal(employee.visibleEmployees.value.length, 1);
  assert.equal(employee.activeEmployee.value.id, 'new');
  const supplier = useSupplierController({ repository });
  supplier.filter.value = ' solar ';
  assert.equal(supplier.visibleSuppliers.value.length, 1);
});

test('inventory loads API data and combines category and text filters', async () => {
  const client = { get: async (path) => path.endsWith('stock-movements') ? [] : [
    { sku: 'I-1', name: 'Huawei Inverter', category: 'Inverter', stock: 4, price: 100 },
    { sku: 'I-2', name: 'Huawei Plus', category: 'Inverter', stock: 2, price: 200 },
  ] };
  const controller = useProductController(client);
  await controller.refresh();
  controller.query.value = ' HUAWEI ';
  controller.category.value = 'Inverter';
  assert.equal(controller.filteredProducts.value.length, 2);
  assert.equal(controller.totalStock.value, 6);
  assert.equal(controller.totalValue.value, 800);
  controller.query.value = 'no match';
  assert.equal(controller.filteredProducts.value.length, 0);
});

test('procurement controller creates and receives through the API', async () => {
  const calls = [];
  const order = { id: 'order-1', supplier_id: 'supplier-1', status: 'draft', lines: [
    { id: 'line-1', product_sku: 'P-1', ordered_quantity: 5, received_quantity: 0 },
  ] };
  const client = {
    get: async (path) => {
      calls.push(['get', path]);
      if (path === '/suppliers') return [{ id: 'supplier-1', name: 'Solar' }];
      if (path === '/catalog/products') return [{ sku: 'P-1', name: 'Panel' }];
      if (path === '/purchase-orders') return [];
      if (path.endsWith('/history')) return { events: [], receipts: [] };
      if (path === '/purchase-orders/order-1') return { ...order, status: 'partially_received', lines: [{ ...order.lines[0], received_quantity: 2 }] };
    },
    post: async (path, body) => {
      calls.push(['post', path, body]);
      if (path === '/purchase-orders') return order;
      if (path === '/suppliers/supplier-1/products/P-1') return { sku: 'P-1', supplier_ids: ['supplier-1'] };
      if (path.endsWith('/approve')) return { ...order, status: 'approved' };
      if (path.endsWith('/receipts')) return { id: 'receipt-1', order_id: 'order-1' };
    },
  };
  const controller = useProcurementController(client);
  await controller.refresh();
  controller.linkForm.value = { supplier_id: 'supplier-1', product_sku: 'P-1' };
  await controller.linkProduct();
  assert.ok(calls.some(call => call[1] === '/suppliers/supplier-1/products/P-1'));
  controller.actor.value = 'buyer';
  controller.orderForm.value.supplier_id = 'supplier-1';
  controller.lineForm.value = { product_sku: 'P-1', quantity: 5 };
  controller.addLine();
  await controller.createOrder();
  assert.equal(controller.selectedOrder.value.status, 'draft');
  assert.equal(calls.find(call => call[1] === '/purchase-orders' && call[0] === 'post')[2].actor, 'buyer');
  await controller.approve();
  assert.equal(controller.selectedOrder.value.status, 'approved');
  controller.receiptReference.value = 'GR-1';
  controller.receiptQuantities.value['line-1'] = 2;
  await controller.receive();
  assert.equal(controller.selectedOrder.value.lines[0].received_quantity, 2);
  assert.deepEqual(calls.find(call => call[1].endsWith('/receipts'))[2].lines, [{ order_line_id: 'line-1', quantity: 2 }]);
});

test('API client reports backend validation errors', async () => {
  const client = new ApiClient('http://local/api', async () => ({
    ok: false, status: 409, json: async () => ({ detail: 'Receipt reference already exists.' }),
  }));
  await assert.rejects(client.post('/receipt', {}), /Receipt reference already exists/);
});

test('sales uses the product API and records outbound stock', async () => {
  const calls = [];
  let stock = 3;
  const client = {
    get: async (path) => {
      calls.push(['get', path]);
      return [{ sku: 'P-1', name: 'Panel', price: '12.50', stock, unit: 'ชิ้น' }];
    },
    post: async (path, body) => {
      calls.push(['post', path, body]);
      stock -= body.lines[0].quantity;
      return { id: 'issue-1' };
    },
  };
  const controller = useSalesController({ client });
  await controller.refresh();
  const product = controller.catalog.value[0];
  controller.addToBill(product);
  assert.equal(controller.total.value, product.price);
  controller.addToBill(product);
  assert.equal(controller.total.value, product.price * 2);
  controller.reference.value = 'SALE-1';
  controller.actor.value = 'seller';
  await controller.saveOrder();
  assert.equal(controller.bill.value.length, 0);
  assert.equal(controller.catalog.value[0].stock, 1);
  assert.deepEqual(calls.find(call => call[0] === 'post')[2].lines, [{ product_sku: 'P-1', quantity: 2 }]);
  assert.equal(useSalesController().bill.value.length, 0);
});

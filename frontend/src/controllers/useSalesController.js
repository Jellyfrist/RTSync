import { ref, computed, reactive } from 'vue';
import { api } from '../api/client.js';
import { Quote } from '../models/Quote.js';
import { formatCurrency } from '../utils/formatCurrency.js';

export function useSalesController({ client = api } = {}) {
  const catalog = ref([]);
  const quote = reactive(new Quote());
  const reference = ref('');
  const actor = ref('');
  const loading = ref(false);
  const error = ref('');
  const message = ref('');
  const bill = computed(() => quote.items);
  const total = computed(() => quote.total);

  async function refresh() {
    loading.value = true;
    error.value = '';
    try {
      catalog.value = (await client.get('/catalog/products')).map(product => ({ ...product, price: Number(product.price) }));
    } catch (cause) { error.value = cause.message; }
    finally { loading.value = false; }
  }

  function addToBill(product) {
    const inBill = quote.items.find(item => item.sku === product.sku)?.qty || 0;
    if (inBill >= product.stock) { error.value = 'Not enough stock for this product.'; return; }
    error.value = '';
    quote.add({ ...product, qty: 1 });
  }

  const removeItem = (index) => quote.remove(index);

  async function saveOrder() {
    if (!reference.value.trim() || !actor.value.trim() || !quote.items.length) {
      error.value = 'Enter a reference, your name, and at least one product.';
      return;
    }
    loading.value = true;
    error.value = '';
    message.value = '';
    try {
      await client.post('/catalog/stock-issues', {
        reference: reference.value.trim(), actor: actor.value.trim(),
        lines: quote.items.map(item => ({ product_sku: item.sku, quantity: item.qty })),
      });
      quote.items.splice(0);
      reference.value = '';
      message.value = 'บันทึกการจ่ายสินค้าและตัดสต็อกแล้ว';
      try {
        catalog.value = (await client.get('/catalog/products')).map(product => ({ ...product, price: Number(product.price) }));
      } catch {
        message.value += ' กรุณารีเฟรชรายการสินค้าอีกครั้ง';
      }
    } catch (cause) { error.value = cause.message; }
    finally { loading.value = false; }
  }

  return { catalog, bill, total, reference, actor, loading, error, message,
    refresh, addToBill, removeItem, formatCurrency, saveOrder };
}

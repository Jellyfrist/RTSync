import { computed, ref } from 'vue';
import { api } from '../api/client.js';
import { useSearch } from '../composables/useSearch.js';

export function useProductController(client = api) {
  const products = ref([]);
  const movements = ref([]);
  const loading = ref(false);
  const error = ref('');
  const message = ref('');
  const productForm = ref({ sku: '', name: '', category: '', unit: 'ชิ้น', reorder_point: 0, price: 0 });
  const { query, filteredItems } = useSearch(products, ['sku', 'name', 'category']);
  const category = ref('ทั้งหมด');
  const categories = computed(() => ['ทั้งหมด', ...new Set(products.value.map(item => item.category))]);
  const filteredProducts = computed(() => category.value === 'ทั้งหมด'
    ? filteredItems.value : filteredItems.value.filter(item => item.category === category.value));
  const totalStock = computed(() => products.value.reduce((sum, item) => sum + item.stock, 0));
  const totalValue = computed(() => products.value.reduce((sum, item) => sum + item.stock * item.price, 0));

  async function refresh() {
    loading.value = true;
    error.value = '';
    try {
      [products.value, movements.value] = await Promise.all([
        client.get('/catalog/products'), client.get('/catalog/stock-movements'),
      ]);
    } catch (cause) { error.value = cause.message; }
    finally { loading.value = false; }
  }

  async function createProduct() {
    loading.value = true;
    error.value = '';
    message.value = '';
    try {
      const created = await client.post('/catalog/products', { ...productForm.value, price: Number(productForm.value.price) });
      products.value.push(created);
      productForm.value = { sku: '', name: '', category: '', unit: 'ชิ้น', reorder_point: 0, price: 0 };
      message.value = 'Product saved. Stock starts at zero until a receipt is posted.';
    } catch (cause) { error.value = cause.message; }
    finally { loading.value = false; }
  }

  return { products, movements, loading, error, message, productForm, query, category, categories,
    filteredProducts, totalStock, totalValue, refresh, createProduct };
}

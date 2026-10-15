<script setup>
// ไฟล์นี้แสดงทะเบียนสินค้าและรายการที่ถึงจุดสั่งซื้อ
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppShell from "@/components/layout/AppShell.vue";
import AppPageHeader from "@/components/ui/AppPageHeader.vue";
import AppSearchField from "@/components/ui/AppSearchField.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import InventoryFormModal from "@/components/ui/InventoryFormModal.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import TablePagination from "@/components/TablePagination.vue";
import { useSearch } from "@/composables/useSearch";
import { inventoryApi } from "@/api/inventoryApi";
import { peopleApi } from "@/api/peopleApi";
import { operationsApi } from "@/api/operationsApi";
import { mockDb } from "@/api/mockDb";
import { authEnabled, currentUser } from "@/api/authSession";
import { getWeightedAverageCost, pricingDecision } from "@/api/pricingPolicy";

const router = useRouter();
const route = useRoute();
const category = ref("ทั้งหมด");
const categoryFilterQuery = ref("");
const showCategoryPicker = ref(false);
const showStatusPicker = ref(false);
const showModal = ref(false);
const showCategoryModal = ref(false);
const showReceiveModal = ref(false);
const editingProduct = ref(null);
const receivingProduct = ref(null);
const receiveAmount = ref(10);
const receiveUnitCost = ref(0);
const toast = ref(null);
const selectedReorderSkus = ref([]);
const isCreatingPurchaseOrder = ref(false);
const showManualPurchaseModal = ref(false);
const manualPurchaseSearch = ref("");
const selectedManualPurchaseSkus = ref([]);
const newCategoryName = ref("");
const PRODUCT_DRAFT_KEY = "rtsync.inventory.productDraft";
let toastTimer;
// รายการสินค้าที่โหลดจาก API คลังสินค้า
const products = ref([]);
const suppliers = ref([]);
const isLoading = ref(true);
const loadError = ref("");
// แบบฟอร์มเพิ่มหรือแก้ไขสินค้า
const form = ref({
  sku: "",
  name: "",
  category: "",
  stock: 0,
  reorderPoint: 10,
  unit: "ชิ้น",
  price: 0,
  salePrice: 0,
  supplier: "",
});
const { query, filteredItems } = useSearch(products, [
  "sku",
  "name",
  "category",
]);
const categories = ref(["ทั้งหมด"]);
const statusFilter = ref("ทั้งหมด");
const statusOptions = mockDb.get("inventoryStatuses");
const filteredProducts = computed(() =>
  filteredItems.value.filter(
    (item) =>
      (category.value === "ทั้งหมด" || item.category === category.value) &&
      (statusFilter.value === "ทั้งหมด" || item.status === statusFilter.value),
  ),
);
const filteredCategoryOptions = computed(() =>
  categories.value.filter((item) =>
    item.toLowerCase().includes(categoryFilterQuery.value.trim().toLowerCase()),
  ),
);
const lowStock = computed(() =>
  products.value.filter((item) => item.stock <= item.reorderPoint),
);
const manualPurchaseProducts = computed(() => {
  const query = manualPurchaseSearch.value.trim().toLocaleLowerCase("th-TH");
  if (!query) return products.value;
  return products.value.filter((item) =>
    `${item.name} ${item.sku} ${item.category}`
      .toLocaleLowerCase("th-TH")
      .includes(query),
  );
});
const formattedMoney = (value) => `฿${Number(value).toLocaleString("th-TH")}`;
function getLatestCost(product) {
  const lots = Array.isArray(product?.costLots) ? product.costLots : [];
  const latestLot = [...lots].sort(
    (a, b) => new Date(b.receivedAt) - new Date(a.receivedAt),
  )[0];
  return Number(
    latestLot?.unitCost ?? product?.costPrice ?? product?.price ?? 0,
  );
}
function getProductSalePrice(product) {
  return Number(product?.salePrice ?? product?.price ?? 0);
}
function getProductPricing(product) {
  return pricingDecision(getProductSalePrice(product), product);
}
const filteredInventoryValue = computed(() =>
  filteredProducts.value.reduce(
    (sum, item) => sum + item.stock * getWeightedAverageCost(item),
    0,
  ),
);
const filteredLowStock = computed(() =>
  filteredProducts.value.filter((item) => item.stock <= item.reorderPoint),
);
function notify(message, title = "ดำเนินการสำเร็จ") {
  toast.value = { title, message };
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.value = null;
  }, 3600);
}
async function loadProducts() {
  // โหลดรายการสินค้าจาก backend
  isLoading.value = true;
  loadError.value = "";
  try {
    products.value = await inventoryApi.getProducts();
  } catch (error) {
    loadError.value = error.message;
  } finally {
    isLoading.value = false;
  }
}
async function loadCategories() {
  const records = await inventoryApi.getCategories();
  categories.value = ["ทั้งหมด", ...records.map((item) => item.name)];
  if (!categories.value.includes(category.value)) category.value = "ทั้งหมด";
}
async function loadSuppliers() {
  suppliers.value = await peopleApi.getSuppliers();
}
function hydrateProductSuppliers(records) {
  return records.map((product) => ({
    ...product,
    supplier:
      (product.supplier_ids || [])
        .map((supplierId) =>
          suppliers.value.find((supplier) => supplier.id === supplierId)?.name,
        )
        .find(Boolean) || "",
  }));
}
onMounted(async () => {
  await Promise.all([loadProducts(), loadCategories(), loadSuppliers()]);
  products.value = hydrateProductSuppliers(products.value);
  const supplierName = route.query.supplier;
  const draft = readProductDraft();
  const hasSupplierFromQuery =
    typeof supplierName === "string" &&
    suppliers.value.some((item) => item.name === supplierName);

  if (draft || hasSupplierFromQuery) {
    resetForm();
    if (draft?.form) form.value = { ...form.value, ...draft.form };
    if (draft?.editingSku) {
      editingProduct.value = products.value.find(
        (item) => item.sku === draft.editingSku,
      ) || null;
    }
    if (hasSupplierFromQuery) form.value.supplier = supplierName;
    showModal.value = true;
    clearProductDraft();
    if (hasSupplierFromQuery) router.replace({ path: "/inventory" });
  }
});
onBeforeUnmount(() => {
  // Preserve an unfinished product form when the user changes pages.
  if (showModal.value) saveProductDraft();
});
function readProductDraft() {
  try {
    return JSON.parse(sessionStorage.getItem(PRODUCT_DRAFT_KEY) || "null");
  } catch {
    return null;
  }
}
function saveProductDraft() {
  try {
    sessionStorage.setItem(
      PRODUCT_DRAFT_KEY,
      JSON.stringify({
        form: form.value,
        editingSku: editingProduct.value?.sku || null,
      }),
    );
  } catch {
    // Draft preservation is best-effort; it must not block navigation.
  }
}
function clearProductDraft() {
  try {
    sessionStorage.removeItem(PRODUCT_DRAFT_KEY);
  } catch {
    // Ignore storage restrictions and keep the normal form flow working.
  }
}
function resetForm() {
  // ล้างแบบฟอร์มและออกจากโหมดแก้ไข
  form.value = {
    sku: "",
    name: "",
    category: categories.value[1] || "",
    stock: 0,
    reorderPoint: 10,
    unit: "ชิ้น",
    price: 0,
    salePrice: 0,
    supplier: "",
  };
  editingProduct.value = null;
}
function openAdd() {
  clearProductDraft();
  resetForm();
  showModal.value = true;
}
function selectCategory(nextCategory) {
  category.value = nextCategory;
  categoryFilterQuery.value = "";
  showCategoryPicker.value = false;
}
function selectStatus(nextStatus) {
  statusFilter.value = nextStatus;
  showStatusPicker.value = false;
}
function openCategoryModal() {
  newCategoryName.value = "";
  showCategoryModal.value = true;
}
function goToSupplierManagement() {
  saveProductDraft();
  showModal.value = false;
  router.push({ path: "/suppliers", query: { from: "inventory" } });
}
async function saveCategory() {
  const name = newCategoryName.value.trim();
  if (!name) return;
  try {
    const newCategory = await inventoryApi.createCategory(name);
    await loadCategories();
    form.value.category = newCategory.name;
    showCategoryModal.value = false;
    notify(`เพิ่มหมวดหมู่ ${newCategory.name} แล้ว`);
  } catch (error) {
    loadError.value = error.message;
  }
}
function openEdit(product) {
  clearProductDraft();
  form.value = {
    ...product,
    salePrice: product.salePrice ?? product.price ?? 0,
  };
  editingProduct.value = product;
  showModal.value = true;
}
async function saveProduct() {
  // บันทึกสินค้าใหม่หรือข้อมูลที่แก้ไขผ่าน API
  if (!form.value.sku || !form.value.name) return;
  const payload = {
    ...form.value,
    stock: Number(form.value.stock),
    reorder_point: Number(form.value.reorderPoint),
    price: Number(form.value.price),
    cost_price: Number(form.value.price),
    sale_price: Number(form.value.salePrice),
  };
  try {
    const previousSupplierIds = editingProduct.value?.supplier_ids || [];
    if (editingProduct.value)
      await inventoryApi.updateProduct(editingProduct.value.sku, payload);
    else await inventoryApi.createProduct(payload);

    const selectedSupplier = suppliers.value.find(
      (supplier) => supplier.name === form.value.supplier,
    );
    const savedSku = editingProduct.value?.sku || form.value.sku;
    for (const supplierId of previousSupplierIds) {
      if (!selectedSupplier || supplierId !== selectedSupplier.id) {
        await peopleApi.unlinkProduct(supplierId, savedSku);
      }
    }
    if (
      selectedSupplier &&
      !previousSupplierIds.includes(selectedSupplier.id)
    ) {
      await peopleApi.linkProduct(selectedSupplier.id, savedSku);
    }
    await loadProducts();
    products.value = hydrateProductSuppliers(products.value);
    showModal.value = false;
    clearProductDraft();
    notify(
      editingProduct.value
        ? "บันทึกการแก้ไขสินค้าแล้ว"
        : "ลงทะเบียนสินค้าใหม่แล้ว",
    );
  } catch (error) {
    loadError.value = error.message;
  }
}
function closeProductModal() {
  clearProductDraft();
  showModal.value = false;
}
function openReceiveStock(product) {
  receivingProduct.value = product;
  receiveAmount.value = 10;
  receiveUnitCost.value = Math.round(getWeightedAverageCost(product));
  showReceiveModal.value = true;
}
async function receiveStock() {
  // รับจำนวนสินค้าเข้าและบันทึกการเคลื่อนไหวคลัง
  const product = receivingProduct.value;
  const amount = Number(receiveAmount.value);
  if (!product || !Number.isFinite(amount) || amount <= 0) return;
  try {
    await inventoryApi.receiveStock(product.sku, amount, receiveUnitCost.value);
    await loadProducts();
    showReceiveModal.value = false;
    notify(
      `เพิ่ม ${amount.toLocaleString("th-TH")} ${product.unit} ให้ ${product.sku} แล้ว`,
      "อัปเดตคลังสินค้าแล้ว",
    );
  } catch (error) {
    loadError.value = error.message;
  }
}
// Existing reorder workflow: create the order with calculated quantities,
// then open the existing supplier purchase-order section (no extra modal).
function createPurchaseRequest(product) {
  selectedReorderSkus.value = [product.sku];
  void createPurchaseOrder([product]);
}
function toggleReorderSelection(sku) {
  selectedReorderSkus.value = selectedReorderSkus.value.includes(sku)
    ? selectedReorderSkus.value.filter((item) => item !== sku)
    : [...selectedReorderSkus.value, sku];
}
function openManualPurchasePicker() {
  manualPurchaseSearch.value = "";
  selectedManualPurchaseSkus.value = [];
  showManualPurchaseModal.value = true;
}
function toggleManualPurchaseSelection(sku) {
  selectedManualPurchaseSkus.value = selectedManualPurchaseSkus.value.includes(sku)
    ? selectedManualPurchaseSkus.value.filter((item) => item !== sku)
    : [...selectedManualPurchaseSkus.value, sku];
}
async function addManualPurchaseItems() {
  const selected = products.value.filter((item) =>
    selectedManualPurchaseSkus.value.includes(item.sku),
  );
  if (!selected.length) return;
  await createPurchaseOrder(selected);
}
async function createPurchaseOrder(items = null) {
  if (isCreatingPurchaseOrder.value) return;
  // Do not pass a native click event as "items" (the old button did this).
  const selected = Array.isArray(items)
    ? items
    : lowStock.value.filter((item) => selectedReorderSkus.value.includes(item.sku));
  if (!selected.length) {
    notify("กรุณาเลือกสินค้าที่ต้องการสั่งซื้อก่อน", "ยังไม่มีสินค้า");
    return;
  }
  const order = {
    id: `PO-${Date.now()}-${Math.random().toString(36).slice(2, 7).toUpperCase()}`,
    createdAt: new Date().toISOString(),
    status: "รอดำเนินการ",
    items: selected.map((item) => {
      const unitCost = Math.max(0, Number(getWeightedAverageCost(item)) || 0);
      return {
        sku: item.sku,
        name: item.name,
        supplier: item.supplier,
        unit: item.unit,
        currentStock: item.stock,
        reorderPoint: item.reorderPoint,
        quantity: Math.max(Number(item.reorderPoint) - Number(item.stock), 1),
        price: item.price,
        unitCost,
        priceAtOrder: unitCost,
      };
    }),
  };
  isCreatingPurchaseOrder.value = true;
  try {
    await operationsApi.create("purchaseOrders", order);
    showManualPurchaseModal.value = false;
    selectedReorderSkus.value = [];
    selectedManualPurchaseSkus.value = [];
    if (authEnabled.value && currentUser.value?.role === "employee") {
      // UC-03-06/07: Staff can create the request, but UC-02-07 (supplier
      // purchase-order status management) remains Store-owner-only.
      notify("ส่งรายการสั่งซื้อให้เจ้าของร้านดำเนินการต่อแล้ว", "สร้างคำสั่งซื้อสำเร็จ");
    } else {
      await router.push({ path: "/suppliers", hash: "#purchase-orders" });
    }
  } catch (error) {
    notify(error.message || "กรุณาลองใหม่", "สร้างคำสั่งซื้อไม่สำเร็จ");
  } finally {
    isCreatingPurchaseOrder.value = false;
  }
}
</script>

<template>
  <AppShell>
    <AppPageHeader
      eyebrow="INVENTORY CONTROL CENTER"
      title="จัดการข้อมูลสินค้า"
      description="ลงทะเบียนสินค้า ติดตาม Stock และวางแผน Reorder Point ในที่เดียว"
      class-name="inventory-heading"
    />
    <div v-if="isLoading" class="panel loading-state">
      กำลังโหลดข้อมูลจากระบบคลัง...
    </div>
    <div v-else-if="loadError" class="panel error-state">
      {{ loadError }}
      <button class="button secondary" @click="loadProducts">ลองใหม่</button>
    </div>
    <section
      v-if="!isLoading && !loadError"
      class="operations-table-section inventory-table-section"
    >
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">ทะเบียนสินค้า</h2>
          <p class="section-caption">รายการสินค้าและอุปกรณ์ที่อยู่ในระบบคลัง</p>
        </div>
        <button class="button primary" @click="openAdd">
          <SvgIcon name="plus" />ลงทะเบียนสินค้า
        </button>
      </div>
      <div class="task-overview-grid">
        <div>
          <span>สินค้าทั้งหมด</span
          ><strong>{{ filteredProducts.length }}</strong
          ><small>รายการในมุมมองนี้</small>
        </div>
        <div>
          <span>มูลค่าคงคลัง</span
          ><strong>{{ formattedMoney(filteredInventoryValue) }}</strong
          ><small>รวมจากรายการที่แสดง</small>
        </div>
        <div>
          <span>ถึง Reorder Point</span
          ><strong>{{ filteredLowStock.length }}</strong
          ><small>รายการในมุมมองนี้</small>
        </div>
      </div>
      <div
        class="task-table-tools table-filters-below-overview inventory-table-filters"
      >
        <AppSearchField
          v-model="query"
          class-name="table-filter-search"
          placeholder="ค้นหา SKU หรือชื่อสินค้า..."
          label="ค้นหาในตารางสินค้า"
        />
        <div class="category-picker status-picker">
          <button
            type="button"
            class="category-picker-trigger control-field"
            :aria-expanded="showStatusPicker"
            aria-controls="inventory-status-options"
            @click="showStatusPicker = !showStatusPicker"
          >
            <span>สถานะ</span><strong>{{ statusFilter }}</strong
            ><SvgIcon
              class="status-picker-chevron"
              name="chevron-right"
              size="16"
            />
          </button>
          <div
            v-if="showStatusPicker"
            id="inventory-status-options"
            class="category-picker-menu"
          >
            <div class="category-option-list">
              <button
                v-for="status in statusOptions"
                :key="status"
                type="button"
                :class="{ selected: statusFilter === status }"
                @click="selectStatus(status)"
              >
                {{ status }}
              </button>
            </div>
          </div>
        </div>
        <div class="category-picker">
          <button
            type="button"
            class="category-picker-trigger control-field"
            :aria-expanded="showCategoryPicker"
            aria-controls="inventory-category-options"
            @click="showCategoryPicker = !showCategoryPicker"
          >
            <span>หมวดหมู่</span><strong>{{ category }}</strong>
          </button>
          <div
            v-if="showCategoryPicker"
            id="inventory-category-options"
            class="category-picker-menu"
          >
            <AppSearchField
              v-model="categoryFilterQuery"
              class-name="category-picker-search"
              placeholder="ค้นหาหมวดหมู่"
              label="ค้นหาหมวดหมู่"
            />
            <div class="category-option-list">
              <button
                v-for="item in filteredCategoryOptions"
                :key="item"
                type="button"
                :class="{ selected: category === item }"
                @click="selectCategory(item)"
              >
                {{ item }}
              </button>
              <p v-if="!filteredCategoryOptions.length" class="category-empty">
                ไม่พบหมวดหมู่ที่ค้นหา
              </p>
            </div>
          </div>
        </div>
      </div>
      <div class="table-scroll">
        <table class="data-table inventory-table">
          <thead>
            <tr>
              <th>SKU / รหัสสินค้า</th>
              <th>สินค้า</th>
              <th>หมวดหมู่</th>
              <th>คงเหลือ</th>
              <th>Reorder Point</th>
              <th>ต้นทุนล่าสุด</th>
              <th>ราคาขาย</th>
              <th>สถานะ</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredProducts" :key="product.sku">
              <td>
                <span class="sku-code">{{ product.sku }}</span>
              </td>
              <td>
                <strong>{{ product.name }}</strong
                ><small class="table-subtext">{{ product.supplier }}</small>
              </td>
              <td>{{ product.category }}</td>
              <td>
                <strong>{{ product.stock.toLocaleString() }}</strong>
                {{ product.unit }}
              </td>
              <td>{{ product.reorderPoint }} {{ product.unit }}</td>
              <td class="inventory-pricing-cell">
                <strong
                  >ทุนล่าสุด
                  {{ formattedMoney(getLatestCost(product)) }}</strong
                >
                <small class="table-subtext pricing-meta"
                  >เฉลี่ยถ่วงน้ำหนัก
                  {{ formattedMoney(getWeightedAverageCost(product)) }}</small
                >
              </td>
              <td class="inventory-pricing-cell inventory-sale-price-cell">
                <strong
                  >ราคาขาย
                  {{ formattedMoney(getProductSalePrice(product)) }}</strong
                >
                <small
                  class="table-subtext pricing-meta"
                  :class="
                    getProductPricing(product).isLoss
                      ? 'pricing-danger'
                      : 'pricing-safe'
                  "
                >
                  {{
                    getProductPricing(product).isLoss
                      ? "ขาดทุน"
                      : `กำไร ${Math.round(getProductPricing(product).marginRate * 100)}%`
                  }}
                  · ขั้นต่ำ
                  {{
                    formattedMoney(getProductPricing(product).recommendedPrice)
                  }}
                </small>
              </td>
              <td>
                <span
                  :class="
                    product.stock <= product.reorderPoint
                      ? 'warning-tag'
                      : 'success-tag'
                  "
                  >{{ product.status }}</span
                >
              </td>
              <td>
                <div class="table-actions">
                  <button
                    class="icon-button"
                    title="เติมสินค้า"
                    @click="openReceiveStock(product)"
                  >
                    <SvgIcon name="plus" /></button
                  ><button
                    class="icon-button"
                    title="แก้ไข"
                    @click="openEdit(product)"
                  >
                    <SvgIcon name="edit" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!filteredProducts.length">
              <td colspan="8" class="empty-state">ไม่พบรายการสินค้าที่ค้นหา</td>
            </tr>
          </tbody>
        </table>
      </div>
      <TablePagination :total="filteredProducts.length" label="รายการสินค้า" />
    </section>
    <section v-if="!isLoading && !loadError" class="panel reorder-panel">
      <div class="panel-toolbar">
        <div>
          <h2 class="section-heading">Reorder Point</h2>
          <p class="section-caption">
            ระบบแจ้งเตือนเมื่อ Stock เหลือน้อยกว่าหรือเท่ากับค่าที่ตั้งไว้
          </p>
        </div>
        <div class="button-row reorder-actions">
          <button
            class="button secondary"
            type="button"
            @click="openManualPurchasePicker"
          >
            <SvgIcon name="plus" />สั่งซื้อสินค้าอื่น
          </button>
          <button
            class="button primary"
            type="button"
            :disabled="!selectedReorderSkus.length || isCreatingPurchaseOrder"
            @click="createPurchaseOrder()"
          >
            <SvgIcon name="plus" />สร้างคำสั่งซื้อ<span
              v-if="selectedReorderSkus.length"
            >
              ({{ selectedReorderSkus.length }})</span
            >
          </button>
        </div>
      </div>
      <div class="table-scroll reorder-table-wrap">
        <table class="data-table reorder-table">
          <thead>
            <tr>
              <th>ชื่อสินค้า</th>
              <th>รหัสสินค้า</th>
              <th>จำนวนปัจจุบัน / Reorder Point</th>
              <th class="reorder-select-cell">
                <span class="sr-only">เลือก</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="product in lowStock"
              :key="product.sku"
              :class="{ selected: selectedReorderSkus.includes(product.sku) }"
            >
              <td>
                <strong>{{ product.name }}</strong
                ><small class="table-subtext">{{ product.supplier }}</small>
              </td>
              <td>
                <span class="sku-code">{{ product.sku }}</span>
              </td>
              <td>
                <strong class="low-stock-number"
                  >{{ product.stock }} {{ product.unit }}</strong
                ><span class="reorder-target"
                  >/ {{ product.reorderPoint }} {{ product.unit }}</span
                >
              </td>
              <td class="reorder-select-cell">
                <input
                  type="checkbox"
                  :checked="selectedReorderSkus.includes(product.sku)"
                  :aria-label="`เลือกรายการ ${product.name}`"
                  @change="toggleReorderSelection(product.sku)"
                />
              </td>
            </tr>
            <tr v-if="!lowStock.length">
              <td colspan="4" class="empty-state">
                ไม่มีสินค้าที่ต้องสั่งเพิ่มในขณะนี้
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    <InventoryFormModal
      v-if="showManualPurchaseModal"
      eyebrow="MANUAL PURCHASE"
      title="เลือกสินค้าที่ต้องการสั่งซื้อ"
      description="เลือกสินค้าได้แม้ยังไม่ถึง Reorder Point สำหรับงานเร่ง งานโครงการ หรือการเติมสต็อกล่วงหน้า"
      modal-class="manual-purchase-modal"
      @close="showManualPurchaseModal = false"
      @submit="addManualPurchaseItems"
    >
      <AppSearchField
        v-model="manualPurchaseSearch"
        class-name="manual-purchase-search"
        placeholder="ค้นหาชื่อสินค้า SKU หรือหมวดหมู่..."
        label="ค้นหาสินค้าสำหรับสั่งซื้อล่วงหน้า"
      />
      <div class="table-scroll manual-purchase-table-wrap">
        <table class="data-table manual-purchase-table">
          <thead>
            <tr>
              <th class="manual-purchase-check-column" aria-label="เลือก"></th>
              <th>สินค้า</th>
              <th>คงเหลือ</th>
              <th>Reorder Point</th>
              <th>ซัพพลายเออร์</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="product in manualPurchaseProducts"
              :key="product.sku"
              :class="{
                selected: selectedManualPurchaseSkus.includes(product.sku),
              }"
            >
              <td class="manual-purchase-check-column">
                <input
                  type="checkbox"
                  :checked="selectedManualPurchaseSkus.includes(product.sku)"
                  :aria-label="`เลือก ${product.name}`"
                  @change="toggleManualPurchaseSelection(product.sku)"
                />
              </td>
              <td>
                <strong>{{ product.name }}</strong
                ><small class="table-subtext">{{ product.sku }}</small>
              </td>
              <td>{{ product.stock }} {{ product.unit }}</td>
              <td>{{ product.reorderPoint }} {{ product.unit }}</td>
              <td>{{ product.supplier || "ยังไม่ระบุ" }}</td>
            </tr>
            <tr v-if="!manualPurchaseProducts.length">
              <td colspan="5" class="empty-state">ไม่พบสินค้าที่ค้นหา</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer-pagination>
        <TablePagination
          :total="manualPurchaseProducts.length"
          label="รายการสินค้า"
        />
      </template>
      <template #actions>
        <button
          type="button"
          class="button secondary"
          @click="showManualPurchaseModal = false"
        >
          ยกเลิก
        </button>
        <button
          type="submit"
          class="button primary"
          :disabled="!selectedManualPurchaseSkus.length"
        >
          <SvgIcon name="plus" />เพิ่มรายการ ({{
            selectedManualPurchaseSkus.length
          }})
        </button>
      </template>
    </InventoryFormModal>
    <div v-if="toast" class="toast" role="status" aria-live="polite">
      <span class="toast-icon"><SvgIcon name="check" /></span>
      <div class="toast-content">
        <strong>{{ toast.title }}</strong
        ><span>{{ toast.message }}</span>
      </div>
      <button
        class="toast-close"
        type="button"
        aria-label="ปิดการแจ้งเตือน"
        @click="toast = null"
      >
        <SvgIcon name="close" size="16" />
      </button>
    </div>
    <InventoryFormModal
      v-if="showReceiveModal"
      eyebrow="STOCK RECEIPT"
      title="เติมสินค้าเข้าคลัง"
      modal-class="receive-stock-modal"
      @close="showReceiveModal = false"
      @submit="receiveStock"
    >
      <div v-if="receivingProduct" class="receive-product-summary">
        <span class="sku-code">{{ receivingProduct.sku }}</span>
        <div>
          <strong>{{ receivingProduct.name }}</strong
          ><small
            >คงเหลือ {{ receivingProduct.stock.toLocaleString("th-TH") }}
            {{ receivingProduct.unit }}</small
          >
        </div>
      </div>
      <label
        >จำนวนที่รับเข้า ({{ receivingProduct?.unit || "หน่วย" }})
        <input
          v-model.number="receiveAmount"
          type="number"
          min="1"
          step="1"
          required
          autofocus
        />
      </label>
      <div class="quantity-shortcuts" aria-label="เลือกจำนวนด่วน">
        <span>เลือกจำนวนด่วน</span>
        <div>
          <button
            v-for="amount in [1, 5, 10, 20]"
            :key="amount"
            type="button"
            :class="{ selected: receiveAmount === amount }"
            @click="receiveAmount = amount"
          >
            +{{ amount }}
          </button>
        </div>
      </div>
      <label
        >ต้นทุนต่อหน่วยของล็อตใหม่<input
          v-model.number="receiveUnitCost"
          type="number"
          min="0"
          step="0.01"
          required
      /></label>
      <p class="form-helper">
        ต้นทุนล็อตเดิมจะไม่ถูกเขียนทับ
        ระบบจะคำนวณต้นทุนเฉลี่ยถ่วงน้ำหนักเมื่อรับของเข้า
      </p>
      <template #actions>
        <button
          type="button"
          class="button secondary"
          @click="showReceiveModal = false"
        >
          ยกเลิก
        </button>
        <button type="submit" class="button primary">
          <SvgIcon name="plus" />ยืนยันการเติมสินค้า
        </button>
      </template>
    </InventoryFormModal>
    <div
      v-if="showModal"
      class="modal-backdrop"
      @click.self="closeProductModal"
    >
      <form class="modal product-modal" @submit.prevent="saveProduct">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">PRODUCT REGISTRATION</span>
            <h2>
              {{ editingProduct ? "แก้ไขข้อมูลสินค้า" : "ลงทะเบียนสินค้าใหม่" }}
            </h2>
          </div>
          <button
            type="button"
            class="icon-button"
            title="ปิด"
            @click="closeProductModal"
          >
            <SvgIcon name="close" />
          </button>
        </div>
        <div class="form-grid">
          <label
            >SKU / รหัสสินค้า<input
              v-model="form.sku"
              required
              placeholder="เช่น INV-HW-5K1P" /></label
          ><label
            >ชื่อสินค้า<input
              v-model="form.name"
              required
              placeholder="ชื่อสินค้าและรุ่น" /></label
          ><label
            >หมวดหมู่
            <div class="category-select-row">
              <AppSelect
                v-model="form.category"
                :options="categories.slice(1)"
                placeholder="เลือกหมวดหมู่สินค้า"
                aria-label="เลือกหมวดหมู่สินค้า"
                required
              >
                <template #menu-footer="{ close }">
                  <button
                    type="button"
                    class="app-select-add-action"
                    @click.stop="
                      close();
                      openCategoryModal();
                    "
                  >
                    <SvgIcon name="plus" size="15" />เพิ่มหมวดหมู่
                  </button>
                </template>
              </AppSelect>
            </div></label
          ><label
            >หน่วยนับ<input
              v-model="form.unit"
              placeholder="ชิ้น / แผง / เครื่อง" /></label
          ><label
            >จำนวน Stock เริ่มต้น<input
              v-model="form.stock"
              type="number"
              min="0" /></label
          ><label
            >Reorder Point<input
              v-model="form.reorderPoint"
              type="number"
              min="0"
            /><small class="field-helper"
              >แจ้งเตือนเมื่อ Stock ปัจจุบันน้อยกว่าหรือเท่ากับค่านี้</small
            ></label
          ><label
            >ต้นทุนล่าสุดต่อหน่วย<input
              v-model="form.price"
              type="number"
              min="0" /></label
          ><label
            >ราคาขายต่อหน่วย<input
              v-model="form.salePrice"
              type="number"
              min="0"
              required
            /><small class="field-helper"
              >ใช้เทียบกำไรกับต้นทุนล่าสุดและต้นทุนเฉลี่ย</small
            ></label
          ><label
            >ซัพพลายเออร์
            <div class="category-select-row">
              <AppSelect
                v-model="form.supplier"
                :options="
                  suppliers.map((supplier) => ({
                    value: supplier.name,
                    label: supplier.name,
                  }))
                "
                placeholder="เลือกซัพพลายเออร์"
                aria-label="เลือกซัพพลายเออร์"
                required
              >
                <template #menu-footer="{ close }">
                  <button
                    type="button"
                    class="app-select-add-action"
                    @click.stop="
                      close();
                      goToSupplierManagement();
                    "
                  >
                    <SvgIcon name="plus" size="15" />เพิ่มซัพพลายเออร์
                  </button>
                </template>
              </AppSelect>
            </div></label
          >
        </div>
        <div class="button-row end">
          <button
            type="button"
            class="button secondary"
            @click="closeProductModal"
          >
            ยกเลิก</button
          ><button type="submit" class="button primary">
            บันทึกข้อมูลสินค้า
          </button>
        </div>
      </form>
    </div>
    <div
      v-if="showCategoryModal"
      class="modal-backdrop"
      @click.self="showCategoryModal = false"
    >
      <form class="modal category-modal" @submit.prevent="saveCategory">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">PRODUCT CATEGORY</span>
            <h2>เพิ่มหมวดหมู่สินค้า</h2>
          </div>
          <button
            type="button"
            class="icon-button"
            title="ปิด"
            @click="showCategoryModal = false"
          >
            <SvgIcon name="close" />
          </button>
        </div>
        <label
          >ชื่อหมวดหมู่ใหม่<input
            v-model="newCategoryName"
            required
            placeholder="เช่น แบตเตอรี่และระบบกักเก็บพลังงาน"
        /></label>
        <p class="form-helper">
          หมวดหมู่จะถูกบันทึกลงฐานข้อมูลและพร้อมเลือกใช้ทันที
        </p>
        <div class="button-row end">
          <button
            type="button"
            class="button secondary"
            @click="showCategoryModal = false"
          >
            ยกเลิก
          </button>
          <button type="submit" class="button primary">บันทึกหมวดหมู่</button>
        </div>
      </form>
    </div>
  </AppShell>
</template>

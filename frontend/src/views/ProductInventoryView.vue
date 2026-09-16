<script setup>
// ไฟล์นี้แสดงทะเบียนสินค้าและรายการที่ถึงจุดสั่งซื้อ
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppShell from "@/components/layout/AppShell.vue";
import AppPageHeader from "@/components/ui/AppPageHeader.vue";
import AppSearchField from "@/components/ui/AppSearchField.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import TablePagination from "@/components/TablePagination.vue";
import { useSearch } from "@/composables/useSearch";
import { inventoryApi } from "@/api/inventoryApi";
import { peopleApi } from "@/api/peopleApi";
import { mockDb } from "@/api/mockDb";
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
const showPurchaseOrderModal = ref(false);
const purchaseOrderItems = ref([]);
const newCategoryName = ref("");
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
  supplier: "",
});
const { query, filteredItems } = useSearch(products, [
  "sku",
  "name",
  "category",
]);
const categories = ref(["ทั้งหมด"]);
const statusFilter = ref("ทั้งหมด");
const statusOptions = ["ทั้งหมด", "พร้อมขาย", "ต้องสั่งเพิ่ม"];
const filteredProducts = computed(() =>
  filteredItems.value.filter((item) =>
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
const formattedMoney = (value) => `฿${Number(value).toLocaleString("th-TH")}`;
const filteredInventoryValue = computed(() =>
  filteredProducts.value.reduce(
    (sum, item) => sum + item.stock * item.price,
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
onMounted(async () => {
  await Promise.all([loadProducts(), loadCategories(), loadSuppliers()]);
  const supplierName = route.query.supplier;
  if (
    typeof supplierName === "string" &&
    suppliers.value.some((item) => item.name === supplierName)
  ) {
    resetForm();
    form.value.supplier = supplierName;
    showModal.value = true;
    router.replace({ path: "/inventory" });
  }
});
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
    supplier: "",
  };
  editingProduct.value = null;
}
function openAdd() {
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
  form.value = { ...product };
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
  };
  try {
    if (editingProduct.value)
      await inventoryApi.updateProduct(editingProduct.value.sku, payload);
    else await inventoryApi.createProduct(payload);
    await loadProducts();
    showModal.value = false;
    notify(editingProduct.value
      ? "บันทึกการแก้ไขสินค้าแล้ว"
      : "ลงทะเบียนสินค้าใหม่แล้ว");
  } catch (error) {
    loadError.value = error.message;
  }
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
function createPurchaseRequest(product) {
  selectedReorderSkus.value = [product.sku];
  openPurchaseOrder();
}
function toggleReorderSelection(sku) {
  selectedReorderSkus.value = selectedReorderSkus.value.includes(sku)
    ? selectedReorderSkus.value.filter((item) => item !== sku)
    : [...selectedReorderSkus.value, sku];
}
function openPurchaseOrder() {
  const selected = lowStock.value.filter((item) => selectedReorderSkus.value.includes(item.sku));
  if (!selected.length) return;
  purchaseOrderItems.value = selected.map((item) => ({
    sku: item.sku,
    name: item.name,
    supplier: item.supplier,
    unit: item.unit,
    currentStock: item.stock,
    reorderPoint: item.reorderPoint,
    quantity: Math.max(item.reorderPoint - item.stock, 1),
    price: item.price,
    unitCost: Math.round(getWeightedAverageCost(item)),
  }));
  showPurchaseOrderModal.value = true;
}
function removePurchaseOrderItem(sku) {
  purchaseOrderItems.value = purchaseOrderItems.value.filter((item) => item.sku !== sku);
  selectedReorderSkus.value = selectedReorderSkus.value.filter((item) => item !== sku);
}
function createPurchaseOrder() {
  if (!purchaseOrderItems.value.length) return;
  const existing = mockDb.get("purchaseOrders");
  const order = {
    id: `PO-${new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 12)}`,
    createdAt: new Date().toISOString(),
    status: "รอดำเนินการ",
    items: purchaseOrderItems.value.map((item) => ({ ...item, quantity: Number(item.quantity) || 1, unitCost: Number(item.unitCost) || 0, priceAtOrder: Number(item.unitCost) || 0 })),
  };
  mockDb.set("purchaseOrders", [order, ...existing]);
  showPurchaseOrderModal.value = false;
  selectedReorderSkus.value = [];
  notify(`สร้างรายการสั่งซื้อ ${order.items.length} รายการแล้ว`);
  router.push("/suppliers");
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
    <section v-if="!isLoading && !loadError" class="operations-table-section inventory-table-section">
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
        <div><span>สินค้าทั้งหมด</span><strong>{{ filteredProducts.length }}</strong><small>รายการในมุมมองนี้</small></div>
        <div><span>มูลค่าคงคลัง</span><strong>{{ formattedMoney(filteredInventoryValue) }}</strong><small>รวมจากรายการที่แสดง</small></div>
        <div><span>ถึง Reorder Point</span><strong>{{ filteredLowStock.length }}</strong><small>รายการในมุมมองนี้</small></div>
      </div>
      <div class="task-table-tools table-filters-below-overview inventory-table-filters">
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
            <span>สถานะ</span><strong>{{ statusFilter }}</strong><SvgIcon class="status-picker-chevron" name="chevron-right" size="16" />
          </button>
          <div v-if="showStatusPicker" id="inventory-status-options" class="category-picker-menu">
            <div class="category-option-list">
              <button
                v-for="status in statusOptions"
                :key="status"
                type="button"
                :class="{ selected: statusFilter === status }"
                @click="selectStatus(status)"
              >{{ status }}</button>
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
              <th>มูลค่า</th>
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
              <td class="mono">
                {{ formattedMoney(product.stock * product.price) }}
                <small class="table-subtext pricing-meta">ต้นทุนเฉลี่ย {{ formattedMoney(getWeightedAverageCost(product)) }}</small>
                <small class="table-subtext pricing-meta">ขายแนะนำ {{ formattedMoney(pricingDecision(product.salePrice ?? product.price, product).recommendedPrice) }}</small>
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
        <button
          class="button primary"
          :disabled="!selectedReorderSkus.length"
          @click="openPurchaseOrder"
        >
          <SvgIcon name="plus" />สร้างคำสั่งซื้อ ({{ selectedReorderSkus.length }})
        </button>
      </div>
      <div class="table-scroll reorder-table-wrap">
        <table class="data-table reorder-table">
          <thead>
            <tr>
              <th>ชื่อสินค้า</th>
              <th>รหัสสินค้า</th>
              <th>จำนวนปัจจุบัน / Reorder Point</th>
              <th class="reorder-select-cell"><span class="sr-only">เลือก</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in lowStock" :key="product.sku" :class="{ selected: selectedReorderSkus.includes(product.sku) }">
              <td><strong>{{ product.name }}</strong><small class="table-subtext">{{ product.supplier }}</small></td>
              <td><span class="sku-code">{{ product.sku }}</span></td>
              <td><strong class="low-stock-number">{{ product.stock }} {{ product.unit }}</strong><span class="reorder-target">/ {{ product.reorderPoint }} {{ product.unit }}</span></td>
              <td class="reorder-select-cell">
                <input
                  type="checkbox"
                  :checked="selectedReorderSkus.includes(product.sku)"
                  :aria-label="`เลือกรายการ ${product.name}`"
                  @change="toggleReorderSelection(product.sku)"
                />
              </td>
            </tr>
            <tr v-if="!lowStock.length"><td colspan="4" class="empty-state">ไม่มีสินค้าที่ต้องสั่งเพิ่มในขณะนี้</td></tr>
          </tbody>
        </table>
      </div>
    </section>
    <div v-if="showPurchaseOrderModal" class="modal-backdrop" @click.self="showPurchaseOrderModal = false">
      <section class="modal purchase-order-modal" aria-labelledby="purchase-order-title">
        <div class="modal-heading">
          <div><span class="eyebrow">PURCHASE ORDER</span><h2 id="purchase-order-title">รายการสั่งซื้อ</h2></div>
          <button type="button" class="icon-button" title="ปิด" @click="showPurchaseOrderModal = false"><SvgIcon name="close" /></button>
        </div>
        <p class="form-helper">ตรวจสอบและแก้ไขจำนวนที่ต้องการสั่ง ก่อนส่งรายการไปยังหน้าซัพพลายเออร์</p>
        <div class="purchase-order-list">
          <div v-for="item in purchaseOrderItems" :key="item.sku" class="purchase-order-row">
            <div><strong>{{ item.name }}</strong><small>{{ item.sku }} · {{ item.supplier }}</small></div>
            <label>จำนวนสั่งซื้อ<input v-model.number="item.quantity" type="number" min="1" step="1" :aria-label="`จำนวนสั่งซื้อ ${item.name}`" /></label>
            <label>ต้นทุน/หน่วย<input v-model.number="item.unitCost" type="number" min="0" step="0.01" :aria-label="`ต้นทุนต่อหน่วย ${item.name}`" /></label>
            <small v-if="item.unitCost > item.price" class="purchase-cost-warning">สูงกว่าต้นทุนเดิม ฿{{ Number(item.price).toLocaleString('th-TH') }}</small>
            <button type="button" class="icon-button" title="ลบรายการ" :aria-label="`ลบ ${item.name}`" @click="removePurchaseOrderItem(item.sku)"><SvgIcon name="close" size="16" /></button>
          </div>
          <p v-if="!purchaseOrderItems.length" class="empty-state">ไม่มีรายการที่เลือก</p>
        </div>
        <div class="button-row end"><button type="button" class="button secondary" @click="showPurchaseOrderModal = false">กลับไปแก้ไข</button><button type="button" class="button primary" :disabled="!purchaseOrderItems.length" @click="createPurchaseOrder">สร้างรายการสั่งซื้อ</button></div>
      </section>
    </div>
    <div v-if="toast" class="toast" role="status" aria-live="polite">
      <span class="toast-icon"><SvgIcon name="check" /></span>
      <div class="toast-content"><strong>{{ toast.title }}</strong><span>{{ toast.message }}</span></div>
      <button class="toast-close" type="button" aria-label="ปิดการแจ้งเตือน" @click="toast = null">
        <SvgIcon name="close" size="16" />
      </button>
    </div>
    <div v-if="showReceiveModal" class="modal-backdrop" @click.self="showReceiveModal = false">
      <form class="modal receive-stock-modal" @submit.prevent="receiveStock">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">STOCK RECEIPT</span>
            <h2>เติมสินค้าเข้าคลัง</h2>
          </div>
          <button type="button" class="icon-button" title="ปิด" @click="showReceiveModal = false">
            <SvgIcon name="close" />
          </button>
        </div>
        <div v-if="receivingProduct" class="receive-product-summary">
          <span class="sku-code">{{ receivingProduct.sku }}</span>
          <div><strong>{{ receivingProduct.name }}</strong><small>คงเหลือ {{ receivingProduct.stock.toLocaleString("th-TH") }} {{ receivingProduct.unit }}</small></div>
        </div>
        <label>จำนวนที่รับเข้า ({{ receivingProduct?.unit || "หน่วย" }})
          <input v-model.number="receiveAmount" type="number" min="1" step="1" required autofocus />
        </label>
        <div class="quantity-shortcuts" aria-label="เลือกจำนวนด่วน">
          <span>เลือกจำนวนด่วน</span>
          <div>
            <button v-for="amount in [1, 5, 10, 20]" :key="amount" type="button" :class="{ selected: receiveAmount === amount }" @click="receiveAmount = amount">+{{ amount }}</button>
          </div>
        </div>
        <label>ต้นทุนต่อหน่วยของล็อตใหม่<input v-model.number="receiveUnitCost" type="number" min="0" step="0.01" required /></label>
        <p class="form-helper">ต้นทุนล็อตเดิมจะไม่ถูกเขียนทับ ระบบจะคำนวณต้นทุนเฉลี่ยถ่วงน้ำหนักเมื่อรับของเข้า</p>
        <div class="button-row end">
          <button type="button" class="button secondary" @click="showReceiveModal = false">ยกเลิก</button>
          <button type="submit" class="button primary"><SvgIcon name="plus" />ยืนยันการเติมสินค้า</button>
        </div>
      </form>
    </div>
    <div
      v-if="showModal"
      class="modal-backdrop"
      @click.self="showModal = false"
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
            @click="showModal = false"
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
            >หมวดหมู่<div class="category-select-row">
              <select v-model="form.category" required>
                <option disabled value="">เลือกหมวดหมู่สินค้า</option>
                <option v-for="item in categories.slice(1)" :key="item">
                  {{ item }}
                </option>
              </select>
              <button type="button" class="button secondary" @click="openCategoryModal">
                <SvgIcon name="plus" />เพิ่ม
              </button>
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
              min="0" /><small class="field-helper">แจ้งเตือนเมื่อ Stock ปัจจุบันน้อยกว่าหรือเท่ากับค่านี้</small></label
          ><label
            >ราคาต่อหน่วย<input
              v-model="form.price"
              type="number"
              min="0" /></label
          ><label
            >ซัพพลายเออร์<div class="category-select-row">
              <select v-model="form.supplier" required>
                <option disabled value="">เลือกซัพพลายเออร์</option>
                <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.name">
                  {{ supplier.name }}
                </option>
              </select>
              <button type="button" class="button secondary" @click="goToSupplierManagement">
                <SvgIcon name="plus" />เพิ่ม
              </button>
            </div></label>
        </div>
        <div class="button-row end">
          <button
            type="button"
            class="button secondary"
            @click="showModal = false"
          >
            ยกเลิก</button
          ><button type="submit" class="button primary">
            บันทึกข้อมูลสินค้า
          </button>
        </div>
      </form>
    </div>
    <div v-if="showCategoryModal" class="modal-backdrop" @click.self="showCategoryModal = false">
      <form class="modal category-modal" @submit.prevent="saveCategory">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">PRODUCT CATEGORY</span>
            <h2>เพิ่มหมวดหมู่สินค้า</h2>
          </div>
          <button type="button" class="icon-button" title="ปิด" @click="showCategoryModal = false">
            <SvgIcon name="close" />
          </button>
        </div>
        <label>ชื่อหมวดหมู่ใหม่<input v-model="newCategoryName" required placeholder="เช่น แบตเตอรี่และระบบกักเก็บพลังงาน" /></label>
        <p class="form-helper">หมวดหมู่จะถูกบันทึกลงฐานข้อมูลและพร้อมเลือกใช้ทันที</p>
        <div class="button-row end">
          <button type="button" class="button secondary" @click="showCategoryModal = false">ยกเลิก</button>
          <button type="submit" class="button primary">บันทึกหมวดหมู่</button>
        </div>
      </form>
    </div>
  </AppShell>
</template>

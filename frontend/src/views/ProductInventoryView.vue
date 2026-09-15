<script setup>
// ไฟล์นี้แสดงทะเบียนสินค้า รายงาน Stock และรายการที่ถึงจุดสั่งซื้อ
import { computed, onMounted, ref } from "vue";
import AppShell from "@/components/AppShell.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import { useSearch } from "@/composables/useSearch";
import { inventoryApi } from "@/api/inventoryApi";

const activeTab = ref("products");
const category = ref("ทั้งหมด");
const showModal = ref(false);
const editingProduct = ref(null);
const toast = ref("");
// รายการสินค้าที่โหลดจาก API คลังสินค้า
const products = ref([]);
const isLoading = ref(true);
const loadError = ref("");
// แบบฟอร์มเพิ่มหรือแก้ไขสินค้า
const form = ref({
  sku: "",
  name: "",
  category: "แผงโซลาร์",
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
const categories = [
  "ทั้งหมด",
  "แผงโซลาร์",
  "อินเวอร์เตอร์",
  "อุปกรณ์วัด",
  "อุปกรณ์ติดตั้ง",
];
const filteredProducts = computed(() =>
  category.value === "ทั้งหมด"
    ? filteredItems.value
    : filteredItems.value.filter((item) => item.category === category.value),
);
const lowStock = computed(() =>
  products.value.filter((item) => item.stock <= item.reorderPoint),
);
const inventoryValue = computed(() =>
  products.value.reduce((sum, item) => sum + item.stock * item.price, 0),
);
const formattedMoney = (value) => `฿${Number(value).toLocaleString("th-TH")}`;
const availableCount = computed(
  () => products.value.filter((item) => item.stock > 0).length,
);
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
onMounted(loadProducts);
function resetForm() {
  // ล้างแบบฟอร์มและออกจากโหมดแก้ไข
  form.value = {
    sku: "",
    name: "",
    category: "แผงโซลาร์",
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
    toast.value = editingProduct.value
      ? "บันทึกการแก้ไขสินค้าแล้ว"
      : "ลงทะเบียนสินค้าใหม่แล้ว";
    setTimeout(() => {
      toast.value = "";
    }, 2600);
  } catch (error) {
    loadError.value = error.message;
  }
}
async function receiveStock(product) {
  // รับจำนวนสินค้าเข้าและบันทึกการเคลื่อนไหวคลัง
  const amount = Number(
    window.prompt(
      `เติมสินค้า ${product.name}\nระบุจำนวน ${product.unit} ที่รับเข้า`,
      "10",
    ),
  );
  if (!Number.isNaN(amount) && amount > 0) {
    try {
      await inventoryApi.receiveStock(product.sku, amount);
      await loadProducts();
      toast.value = `เติม Stock ${product.sku} จำนวน ${amount} ${product.unit} แล้ว`;
      setTimeout(() => {
        toast.value = "";
      }, 2600);
    } catch (error) {
      loadError.value = error.message;
    }
  }
}
function createPurchaseRequest(product) {
  toast.value = `สร้างรายการสั่งซื้อ ${product.sku} แล้ว`;
  setTimeout(() => {
    toast.value = "";
  }, 2600);
}
</script>

<template>
  <AppShell placeholder="ค้นหา SKU, รหัสสินค้า, ชื่อสินค้า...">
    <div class="page-title inventory-heading">
      <div>
        <span class="eyebrow">INVENTORY CONTROL CENTER</span>
        <h1>จัดการข้อมูลสินค้า</h1>
        <p>ลงทะเบียนสินค้า ติดตาม Stock และวางแผน Reorder Point ในที่เดียว</p>
      </div>
      <div class="button-row">
        <button class="button secondary" @click="activeTab = 'stock'">
          <SvgIcon name="download" />รายงาน Stock</button
        ><button class="button primary" @click="openAdd">
          <SvgIcon name="plus" />ลงทะเบียนสินค้า
        </button>
      </div>
    </div>
    <div v-if="isLoading" class="panel loading-state">
      กำลังโหลดข้อมูลจากระบบคลัง...
    </div>
    <div v-else-if="loadError" class="panel error-state">
      {{ loadError }}
      <button class="button secondary" @click="loadProducts">ลองใหม่</button>
    </div>
    <section v-else class="inventory-kpis">
      <article class="inventory-kpi">
        <div class="kpi-icon blue"><SvgIcon name="box" size="20" /></div>
        <div>
          <span>สินค้าทั้งหมด</span
          ><strong>{{ products.length }} <small>รายการ</small></strong
          ><em>{{ availableCount }} รายการมี Stock</em>
        </div>
      </article>
      <article class="inventory-kpi">
        <div class="kpi-icon green"><SvgIcon name="wallet" size="20" /></div>
        <div>
          <span>มูลค่าคงคลัง</span
          ><strong>{{ formattedMoney(inventoryValue) }}</strong
          ><em>อัปเดตล่าสุดจากฐานข้อมูล</em>
        </div>
      </article>
      <article class="inventory-kpi alert">
        <div class="kpi-icon orange"><SvgIcon name="settings" size="20" /></div>
        <div>
          <span>รายการถึง Reorder Point</span
          ><strong>{{ lowStock.length }} <small>รายการ</small></strong
          ><em>ควรตรวจสอบภายในวันนี้</em>
        </div>
      </article>
    </section>
    <nav class="inventory-tabs" aria-label="เมนูจัดการข้อมูลสินค้า">
      <button
        :class="{ active: activeTab === 'products' }"
        @click="activeTab = 'products'"
      >
        <SvgIcon name="box" />ทะเบียนสินค้า
        <span>{{ products.length }}</span></button
      ><button
        :class="{ active: activeTab === 'stock' }"
        @click="activeTab = 'stock'"
      >
        <SvgIcon name="download" />รายงาน Stock</button
      ><button
        :class="{ active: activeTab === 'reorder' }"
        @click="activeTab = 'reorder'"
      >
        <SvgIcon name="settings" />Reorder Point
        <span class="tab-alert">{{ lowStock.length }}</span>
      </button>
    </nav>
    <section v-if="activeTab === 'products'" class="panel inventory-panel">
      <div class="panel-toolbar">
        <div>
          <h2 class="section-heading">ทะเบียนสินค้า</h2>
          <p class="section-caption">รายการสินค้าและอุปกรณ์ที่อยู่ในระบบคลัง</p>
        </div>
        <div class="inventory-toolbar">
          <div class="filter-tabs">
            <button
              v-for="item in categories"
              :key="item"
              :class="{ selected: category === item }"
              @click="category = item"
            >
              {{ item }}
            </button>
          </div>
          <div class="search-inline">
            <SvgIcon name="search" /><input
              v-model="query"
              placeholder="ค้นหาในตาราง"
            />
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
                    @click="receiveStock(product)"
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
    </section>
    <section v-else-if="activeTab === 'stock'" class="stock-report-layout">
      <article class="panel stock-overview">
        <div class="panel-toolbar">
          <div>
            <h2 class="section-heading">รายงาน Stock สินค้า</h2>
            <p class="section-caption">ภาพรวมระดับคงคลังแยกตามหมวดหมู่</p>
          </div>
          <button class="button secondary">
            <SvgIcon name="download" />ส่งออกรายงาน
          </button>
        </div>
        <div class="stock-bars">
          <div
            v-for="item in categories.slice(1)"
            :key="item"
            class="stock-bar-row"
          >
            <div class="bar-label">
              <span>{{ item }}</span
              ><strong>{{
                products
                  .filter((p) => p.category === item)
                  .reduce((s, p) => s + p.stock, 0)
                  .toLocaleString()
              }}</strong>
            </div>
            <div class="bar-track">
              <span
                :style="{
                  width: `${Math.min(100, products.filter((p) => p.category === item).reduce((s, p) => s + p.stock, 0) / 3)}%`,
                }"
              ></span>
            </div>
          </div>
        </div>
      </article>
      <article class="panel movement-card">
        <span class="eyebrow">MOVEMENT THIS MONTH</span
        ><strong>+286 <small>หน่วย</small></strong>
        <p>รับเข้า 342 หน่วย · เบิกออก 56 หน่วย</p>
        <div class="movement-line">
          <span style="height: 38%"></span><span style="height: 52%"></span
          ><span style="height: 46%"></span><span style="height: 74%"></span
          ><span style="height: 62%"></span><span style="height: 89%"></span
          ><span style="height: 80%"></span>
        </div>
        <small
          >สัปดาห์ 1&nbsp;&nbsp;&nbsp; สัปดาห์ 2&nbsp;&nbsp;&nbsp; สัปดาห์
          3&nbsp;&nbsp;&nbsp; สัปดาห์ 4</small
        >
      </article>
    </section>
    <section v-else class="panel reorder-panel">
      <div class="panel-toolbar">
        <div>
          <h2 class="section-heading">Reorder Point</h2>
          <p class="section-caption">
            รายการที่ Stock ต่ำกว่าจุดสั่งซื้อที่ตั้งไว้
          </p>
        </div>
        <span class="warning-summary"
          ><SvgIcon name="settings" />
          {{ lowStock.length }} รายการต้องดำเนินการ</span
        >
      </div>
      <div class="reorder-grid">
        <article
          v-for="product in lowStock"
          :key="product.sku"
          class="reorder-card"
        >
          <div class="reorder-card-head">
            <span class="sku-code">{{ product.sku }}</span
            ><span class="warning-tag">ต่ำกว่าจุดสั่งซื้อ</span>
          </div>
          <h3>{{ product.name }}</h3>
          <div class="stock-meter">
            <div>
              <span
                >Stock ปัจจุบัน
                <strong>{{ product.stock }} {{ product.unit }}</strong></span
              ><span
                >จุดสั่งซื้อ
                <strong
                  >{{ product.reorderPoint }} {{ product.unit }}</strong
                ></span
              >
            </div>
            <div class="meter-track">
              <span
                :style="{
                  width: `${Math.min(100, (product.stock / product.reorderPoint) * 100)}%`,
                }"
              ></span>
            </div>
          </div>
          <button
            class="button primary full"
            @click="createPurchaseRequest(product)"
          >
            สร้างรายการสั่งซื้อ
          </button>
        </article>
        <div v-if="!lowStock.length" class="empty-state">
          ไม่มีสินค้าที่ต้องสั่งเพิ่มในขณะนี้
        </div>
      </div>
    </section>
    <div v-if="toast" class="toast"><SvgIcon name="check" />{{ toast }}</div>
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
            >หมวดหมู่<select v-model="form.category">
              <option v-for="item in categories.slice(1)" :key="item">
                {{ item }}
              </option>
            </select></label
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
              min="0" /></label
          ><label
            >ราคาต่อหน่วย<input
              v-model="form.price"
              type="number"
              min="0" /></label
          ><label
            >ซัพพลายเออร์<input
              v-model="form.supplier"
              placeholder="ชื่อผู้จัดจำหน่าย"
          /></label>
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
  </AppShell>
</template>

<script setup>
// ไฟล์นี้จัดการซัพพลายเออร์และการผูกสินค้าเข้ากับแหล่งจัดซื้อ
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppShell from "@/components/layout/AppShell.vue";
import AppPageHeader from "@/components/ui/AppPageHeader.vue";
import AppSearchField from "@/components/ui/AppSearchField.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import TablePagination from "@/components/TablePagination.vue";
import { useModal } from "@/composables/useModal";
import { peopleApi } from "@/api/peopleApi";
import { inventoryApi } from "@/api/inventoryApi";
import { operationsApi } from "@/api/operationsApi";
import { mockDb } from "@/api/mockDb";
const router = useRouter();
const route = useRoute();
// รายชื่อซัพพลายเออร์จาก API
const suppliers = ref([]);
const supplierCategories = ref([]);
// ยังไม่เลือกคู่ค้าเมื่อเข้าหน้า เพื่อให้ผู้ใช้เลือกจากรายการก่อน
const selectedId = ref("");
const filter = ref("");
const { isOpen, open, close } = useModal();
const editingSupplier = ref(null);
const showCategoryModal = ref(false);
const newCategoryName = ref("");
const form = ref({
  name: "",
  category: "",
  description: "",
  delivery: "2-3 วัน",
});
// รายการสินค้าจาก API คลังที่ใช้แสดงการผูกซัพพลายเออร์
const products = ref([]);
const purchaseOrders = ref([]);
const showPurchaseHistory = ref(false);
const showSupplierCategoryFilter = ref(false);
const supplierCategoryFilter = ref("ทั้งหมด");
const supplierCategoryFilterQuery = ref("");
const purchaseOrderStatuses = ["รอดำเนินการ", "กำลังจัดซื้อ", "สั่งซื้อแล้ว", "สำเร็จ"];
const visibleSuppliers = computed(() =>
  suppliers.value.filter((item) =>
    `${item.name} ${item.category}`.toLowerCase().includes(filter.value.toLowerCase())
    && (supplierCategoryFilter.value === "ทั้งหมด" || item.category === supplierCategoryFilter.value),
  ),
);
const filteredSupplierCategories = computed(() => {
  const query = supplierCategoryFilterQuery.value.toLowerCase().trim();
  return supplierCategories.value.filter((category) =>
    category.name.toLowerCase().includes(query),
  );
});
const selectedSupplier = computed(() =>
  suppliers.value.find((item) => item.id === selectedId.value),
);
const supplierProducts = computed(() =>
  products.value.filter((item) => item.supplierId === selectedId.value),
);
const unassignedProducts = computed(() =>
  products.value.filter((item) => item.supplierId !== selectedId.value),
);
const linkedProductCount = computed(
  () => products.value.filter((item) => item.supplierId).length,
);
const activePurchaseOrders = computed(() =>
  purchaseOrders.value.filter((order) => order.status !== "สำเร็จ"),
);
const completedPurchaseOrders = computed(() =>
  purchaseOrders.value.filter((order) => order.status === "สำเร็จ"),
);
const productToAssign = ref("");
async function loadSupplierCategories() {
  supplierCategories.value = await peopleApi.getSupplierCategories();
}
onMounted(async () => {
  // โหลดซัพพลายเออร์และสินค้าเมื่อเปิดหน้า
  const [supplierRecords, inventoryRecords, purchaseOrderRecords] = await Promise.all([
    peopleApi.getSuppliers(),
    inventoryApi.getProducts(),
    operationsApi.getPurchaseOrders(),
    loadSupplierCategories(),
  ]);
  suppliers.value = supplierRecords.map((item) => ({
    ...item,
    sku: item.sku_count,
  }));
  const supplierIds = {
    "JA Solar Thailand": "SUP-TH-001",
    "LONGi Thailand": "SUP-TH-020",
    "Huawei Solar": "SUP-TH-019",
    "Solar Cable Co.": "SUP-TH-025",
  };
  products.value = inventoryRecords.map((item) => ({
    ...item,
    supplierId: supplierIds[item.supplier] || "",
    reorderPoint: item.reorderPoint,
  }));
  purchaseOrders.value = purchaseOrderRecords?.length ? purchaseOrderRecords : mockDb.get("purchaseOrders");
});
function resetForm() {
  form.value = {
    name: "",
    category: supplierCategories.value[0]?.name || "",
    description: "",
    delivery: "2-3 วัน",
  };
  editingSupplier.value = null;
}
function openAdd() {
  resetForm();
  open();
}
function toggleSupplier(supplierId) {
  selectedId.value = selectedId.value === supplierId ? "" : supplierId;
}
function openEdit() {
  form.value = { ...selectedSupplier.value };
  editingSupplier.value = selectedSupplier.value;
  open();
}
function openCategoryModal() {
  newCategoryName.value = "";
  showCategoryModal.value = true;
}
async function saveCategory() {
  const name = newCategoryName.value.trim();
  if (!name) return;
  try {
    const category = await peopleApi.createSupplierCategory(name);
    await loadSupplierCategories();
    form.value.category = category.name;
    showCategoryModal.value = false;
  } catch (error) {
    window.alert(error.message);
  }
}
async function saveSupplier() {
  // บันทึกซัพพลายเออร์ใหม่ลงฐานข้อมูล
  if (!form.value.name.trim() || !form.value.category.trim()) return;
  if (editingSupplier.value) {
    Object.assign(editingSupplier.value, form.value);
    mockDb.set("suppliers", suppliers.value);
  } else {
    try {
      const supplier = await peopleApi.createSupplier(form.value);
      suppliers.value.push({ ...supplier, sku: supplier.sku_count });
      selectedId.value = supplier.id;
      close();
      if (route.query.from === "inventory") {
        router.push({ path: "/inventory", query: { supplier: supplier.name } });
        return;
      }
    } catch (error) {
      window.alert(error.message);
      return;
    }
  }
  close();
}
function assignProduct() {
  // ผูกสินค้าที่เลือกเข้ากับซัพพลายเออร์ปัจจุบัน
  const product = products.value.find(
    (item) => item.sku === productToAssign.value,
  );
  if (!product) return;
  product.supplierId = selectedId.value;
  mockDb.set("products", products.value);
  productToAssign.value = "";
}
function selectSupplierCategory(category) {
  supplierCategoryFilter.value = category;
  supplierCategoryFilterQuery.value = "";
  showSupplierCategoryFilter.value = false;
}
function orderStatusClass(status) {
  if (status === "สำเร็จ") return "success-tag";
  if (status === "รอดำเนินการ") return "warning-tag";
  return "code-tag";
}
function advancePurchaseOrder(order) {
  const currentIndex = purchaseOrderStatuses.indexOf(order.status);
  order.status = purchaseOrderStatuses[Math.min(currentIndex + 1, purchaseOrderStatuses.length - 1)];
  mockDb.set("purchaseOrders", purchaseOrders.value);
}
</script>

<template>
  <AppShell>
    <AppPageHeader
      eyebrow="SUPPLIER & SOURCING"
      title="ศูนย์จัดการซัพพลายเออร์และสินค้า"
      description="Suppliers & Sourcing Hub"
    />
    <div class="supplier-page">
    <section class="operations-table-section supplier-workspace">
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">ภาพรวมคู่ค้า</h2>
          <p class="section-caption">ค้นหา เลือกคู่ค้า และจัดการรายการสินค้าที่เกี่ยวข้อง</p>
        </div>
        <button class="button primary" @click="openAdd">
          <SvgIcon name="plus" />เพิ่มซัพพลายเออร์
        </button>
      </div>
      <div class="task-overview-grid supplier-overview-grid">
        <div><span>ซัพพลายเออร์ทั้งหมด</span><strong>{{ suppliers.length }} <small>ราย</small></strong><small>พร้อมใช้กับการจัดซื้อ</small></div>
        <div><span>หมวดหมู่คู่ค้า</span><strong>{{ supplierCategories.length }} <small>หมวด</small></strong><small>จัดการจากฐานข้อมูล</small></div>
        <div><span>สินค้าที่ผูกแล้ว</span><strong>{{ linkedProductCount }} <small>SKU</small></strong><small>กำหนดแหล่งจัดซื้อแล้ว</small></div>
      </div>
      <div class="task-table-tools table-filters-below-overview supplier-table-toolbar">
        <AppSearchField
          v-model="filter"
          class-name="table-filter-search"
          placeholder="ค้นหาซัพพลายเออร์"
          label="ค้นหาซัพพลายเออร์"
        />
        <div class="category-picker supplier-category-filter">
          <button
            type="button"
            class="category-picker-trigger control-field"
            :aria-expanded="showSupplierCategoryFilter"
            aria-controls="supplier-category-options"
            @click="showSupplierCategoryFilter = !showSupplierCategoryFilter"
          >
            <span>หมวดหมู่</span><strong>{{ supplierCategoryFilter }}</strong><SvgIcon class="supplier-category-chevron" name="chevron-right" size="16" />
          </button>
          <div v-if="showSupplierCategoryFilter" id="supplier-category-options" class="category-picker-menu">
            <AppSearchField
              v-model="supplierCategoryFilterQuery"
              class-name="category-picker-search"
              placeholder="ค้นหาหมวดหมู่"
              label="ค้นหาหมวดหมู่ซัพพลายเออร์"
            />
            <div class="category-option-list">
              <button
                type="button"
                :class="{ selected: supplierCategoryFilter === 'ทั้งหมด' }"
                @click="selectSupplierCategory('ทั้งหมด')"
              >ทั้งหมด</button>
              <button
                v-for="category in filteredSupplierCategories"
                :key="category.category_id || category.name"
                type="button"
                :class="{ selected: supplierCategoryFilter === category.name }"
                @click="selectSupplierCategory(category.name)"
              >{{ category.name }}</button>
              <p v-if="!filteredSupplierCategories.length" class="category-empty">ไม่พบหมวดหมู่ที่ค้นหา</p>
            </div>
          </div>
        </div>
      <p class="supplier-workspace-hint">
        เลือกซัพพลายเออร์เพื่อเปิดรายละเอียดและจัดการรายการสินค้าที่เกี่ยวข้อง
      </p>
      </div>
      <div class="table-scroll supplier-directory-table-wrap">
        <table class="data-table supplier-directory-table">
          <thead>
            <tr>
              <th>ซัพพลายเออร์</th>
              <th>หมวดหมู่</th>
              <th>รายละเอียด</th>
              <th>ระยะเวลาจัดส่ง</th>
              <th>SKU</th>
              <th aria-label="เปิดรายละเอียด"></th>
            </tr>
          </thead>
          <tbody>
        <template
          v-for="supplier in visibleSuppliers"
          :key="supplier.id"
        >
          <tr
            class="supplier-table-row"
            :class="{ selected: selectedId === supplier.id }"
            :aria-expanded="selectedId === supplier.id"
            tabindex="0"
            @click="toggleSupplier(supplier.id)"
            @keydown.enter.prevent="toggleSupplier(supplier.id)"
            @keydown.space.prevent="toggleSupplier(supplier.id)"
          >
            <td><strong>{{ supplier.name }}</strong></td>
            <td><span class="code-tag">{{ supplier.category }}</span></td>
            <td class="supplier-description">{{ supplier.description }}</td>
            <td>{{ supplier.delivery }}</td>
            <td>{{ supplier.sku }} SKU</td>
            <td class="supplier-table-action">
              <button
                class="icon-button"
                :aria-label="`ดูรายละเอียด ${supplier.name}`"
                @click.stop="toggleSupplier(supplier.id)"
              >
                <SvgIcon class="supplier-table-chevron" name="chevron-right" size="20" />
              </button>
            </td>
          </tr>
          <tr
            v-if="selectedId === supplier.id"
            :id="`supplier-detail-${supplier.id}`"
            class="supplier-detail-row"
          >
            <td colspan="6">
              <div class="detail-card supplier-inline-detail">
        <div class="detail-heading">
          <div>
            <span class="code-tag">{{ supplier.id }}</span>
            <h2>{{ supplier.name }}</h2>
            <p>{{ supplier.description }}</p>
          </div>
          <button class="button secondary" @click="openEdit">
            <SvgIcon name="edit" />แก้ไขข้อมูล
          </button>
        </div>
        <div class="info-grid">
          <div>
            <small>หมวดหมู่หลัก</small
            ><strong>{{ supplier.category }}</strong>
          </div>
          <div>
            <small>ระยะเวลาจัดส่ง</small
            ><strong>{{ supplier.delivery }}</strong>
          </div>
          <div>
            <small>จำนวน SKU</small
            ><strong>{{ supplier.sku }} รายการ</strong>
          </div>
        </div>
        <h3>สินค้าจากซัพพลายเออร์</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>รายการสินค้า</th>
              <th>ราคา</th>
              <th>สถานะ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in supplierProducts" :key="product.sku">
              <td class="mono">{{ product.sku }}</td>
              <td>
                <strong>{{ product.name }}</strong
                ><small class="table-subtext"
                  >Stock {{ product.stock }} · Reorder Point
                  {{ product.reorderPoint }}</small
                >
              </td>
              <td>฿{{ product.price.toLocaleString("th-TH") }}</td>
              <td>
                <span
                  :class="
                    product.status === 'ต้องสั่งเพิ่ม'
                      ? 'warning-tag'
                      : 'success-tag'
                  "
                  >{{ product.status }}</span
                >
              </td>
            </tr>
            <tr v-if="!supplierProducts.length">
              <td colspan="4" class="empty-state">
                ยังไม่มีสินค้าที่ผูกกับซัพพลายเออร์รายนี้
              </td>
            </tr>
          </tbody>
        </table>
        <TablePagination :total="supplierProducts.length" label="รายการสินค้า" />
        <div class="supplier-product-link">
          <div>
            <strong>ผูกสินค้าเข้ากับ Supplier</strong
            ><small
              >กำหนดแหล่งจัดซื้อให้แต่ละ SKU เพื่อใช้กับงานสั่งซื้อและ
              Reorder</small
            >
          </div>
          <div class="button-row">
            <select v-model="productToAssign" aria-label="เลือกสินค้าที่จะผูก">
              <option value="">เลือกสินค้า</option>
              <option
                v-for="product in unassignedProducts"
                :key="product.sku"
                :value="product.sku"
              >
                {{ product.sku }} · {{ product.name }}
              </option></select
            ><button
              class="button secondary"
              :disabled="!productToAssign"
              @click="assignProduct"
            >
              <SvgIcon name="plus" />ผูกสินค้า
            </button>
          </div>
        </div>
          </div>
            </td>
          </tr>
        </template>
          </tbody>
        </table>
      </div>
      <TablePagination
        :total="visibleSuppliers.length"
        label="รายการซัพพลายเออร์"
      />
    </section>
    <section class="panel purchase-orders-panel">
      <div class="panel-toolbar purchase-orders-heading">
        <div>
          <h2 class="section-heading">รายการสั่งซื้อ</h2>
          <p class="section-caption">รายการที่สร้างจาก Reorder Point และส่งต่อให้ทีมจัดซื้อ</p>
        </div>
        <button
          type="button"
          class="button secondary purchase-history-toggle"
          @click="showPurchaseHistory = !showPurchaseHistory"
        >
          <SvgIcon name="refresh" size="15" />{{ showPurchaseHistory ? "กลับไปรายการปัจจุบัน" : "ดูประวัติที่สำเร็จแล้ว" }}
        </button>
      </div>
      <div v-if="(showPurchaseHistory ? completedPurchaseOrders : activePurchaseOrders).length" class="purchase-orders-list">
        <article v-for="order in (showPurchaseHistory ? completedPurchaseOrders : activePurchaseOrders)" :key="order.id" class="purchase-order-summary">
          <div class="purchase-order-summary-head">
            <strong>{{ order.id }}</strong>
            <div class="purchase-order-summary-actions">
              <span :class="orderStatusClass(order.status)">{{ order.status }}</span>
              <button
                v-if="!showPurchaseHistory"
                type="button"
                class="button secondary purchase-order-status-button"
                :disabled="order.status === 'สำเร็จ'"
                @click="advancePurchaseOrder(order)"
              >
                <SvgIcon name="refresh" size="14" />อัปเดตสถานะ
              </button>
            </div>
          </div>
          <small>สร้างเมื่อ {{ new Date(order.createdAt).toLocaleString("th-TH") }}</small>
          <ul>
            <li v-for="item in order.items" :key="item.sku"><span>{{ item.name }} <em>{{ item.sku }}</em></span><strong>{{ item.quantity }} {{ item.unit }}</strong></li>
          </ul>
        </article>
      </div>
      <div v-else class="empty-state">{{ showPurchaseHistory ? "ยังไม่มีรายการสั่งซื้อที่สำเร็จ" : "ยังไม่มีรายการสั่งซื้อจากคลังสินค้า" }}</div>
      <TablePagination
        :total="(showPurchaseHistory ? completedPurchaseOrders : activePurchaseOrders).length"
        :label="showPurchaseHistory ? 'ประวัติการสั่งซื้อ' : 'รายการสั่งซื้อ'"
      />
    </section>
    </div>
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <form class="modal product-modal supplier-modal" @submit.prevent="saveSupplier">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">SUPPLIER REGISTRATION</span>
            <h2>
              {{
                editingSupplier ? "แก้ไขข้อมูลซัพพลายเออร์" : "เพิ่มซัพพลายเออร์"
              }}
            </h2>
          </div>
          <button type="button" class="icon-button" title="ปิด" @click="close">
            <SvgIcon name="close" />
          </button>
        </div>
        <div class="form-grid">
          <label
            >ชื่อบริษัท / ซัพพลายเออร์<input
              v-model="form.name"
              required
              placeholder="เช่น Huawei Solar" /></label
          ><label
            >หมวดหมู่<div class="category-select-row">
              <select v-model="form.category" required>
                <option disabled value="">เลือกหมวดหมู่ซัพพลายเออร์</option>
                <option v-for="category in supplierCategories" :key="category.category_id" :value="category.name">
                  {{ category.name }}
                </option>
              </select>
              <button type="button" class="button secondary" @click="openCategoryModal">
                <SvgIcon name="plus" />เพิ่ม
              </button>
            </div></label
          ><label
            >รายละเอียด<input
              v-model="form.description"
              placeholder="คำอธิบายและจุดเด่นของ Supplier" /></label
          ><label
            >ระยะเวลาจัดส่ง<input
              v-model="form.delivery"
              placeholder="เช่น 2-3 วัน"
          /></label>
        </div>
        <div class="button-row end">
          <button type="button" class="button secondary" @click="close">ยกเลิก</button
          ><button type="submit" class="button primary">บันทึกข้อมูลซัพพลายเออร์</button>
        </div>
      </form>
    </div>
    <div v-if="showCategoryModal" class="modal-backdrop" @click.self="showCategoryModal = false">
      <form class="modal category-modal" @submit.prevent="saveCategory">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">SUPPLIER CATEGORY</span>
            <h2>เพิ่มหมวดหมู่ซัพพลายเออร์</h2>
          </div>
          <button type="button" class="icon-button" title="ปิด" @click="showCategoryModal = false">
            <SvgIcon name="close" />
          </button>
        </div>
        <label>ชื่อหมวดหมู่ใหม่<input v-model="newCategoryName" required placeholder="เช่น อุปกรณ์โครงสร้างและติดตั้ง" /></label>
        <p class="form-helper">หมวดหมู่จะถูกบันทึกลงฐานข้อมูลและพร้อมเลือกใช้ทันที</p>
        <div class="button-row end">
          <button type="button" class="button secondary" @click="showCategoryModal = false">ยกเลิก</button>
          <button type="submit" class="button primary">บันทึกหมวดหมู่</button>
        </div>
      </form>
    </div>
  </AppShell>
  >
</template>

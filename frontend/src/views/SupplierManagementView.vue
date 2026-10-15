<script setup>
// ไฟล์นี้จัดการซัพพลายเออร์และการผูกสินค้าเข้ากับแหล่งจัดซื้อ
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppShell from "@/components/layout/AppShell.vue";
import AppPageHeader from "@/components/ui/AppPageHeader.vue";
import AppSearchField from "@/components/ui/AppSearchField.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import TablePagination from "@/components/TablePagination.vue";
import { useModal } from "@/composables/useModal";
import { peopleApi } from "@/api/peopleApi";
import { inventoryApi } from "@/api/inventoryApi";
import { operationsApi } from "@/api/operationsApi";
import { mockDb } from "@/api/mockDb";
import { authEnabled, currentUser } from "@/api/authSession";
const router = useRouter();
const route = useRoute();
const isInventorySupplierFlow = computed(
  () => authEnabled.value && currentUser.value?.role === "employee" &&
    route.query.from === "inventory",
);
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
  contactName: "",
  contactPhone: "",
  contactEmail: "",
  delivery: "2-3 วัน",
  paymentTerms: "เครดิต 30 วัน",
});
// รายการสินค้าจาก API คลังที่ใช้แสดงการผูกซัพพลายเออร์
const products = ref([]);
const purchaseOrders = ref([]);
const showSupplierCategoryFilter = ref(false);
const supplierCategoryFilter = ref("ทั้งหมด");
const supplierCategoryFilterQuery = ref("");
const purchaseOrderStatuses = mockDb.get("purchaseOrderStatuses");
const showPurchaseHistory = ref(false);
const visibleSuppliers = computed(() =>
  suppliers.value.filter(
    (item) =>
      `${item.name} ${item.category} ${item.contactName} ${item.contactPhone}`
        .toLowerCase()
        .includes(filter.value.toLowerCase()) &&
      (supplierCategoryFilter.value === "ทั้งหมด" ||
        item.category === supplierCategoryFilter.value),
  ),
);
const supplierCategoryOptions = computed(() => {
  const options = [
    ...supplierCategories.value,
    ...suppliers.value.map((supplier) => ({ name: supplier.category })),
  ].filter((category) => category.name);
  return [
    ...new Map(options.map((category) => [category.name, category])).values(),
  ];
});
const filteredSupplierCategories = computed(() => {
  const query = supplierCategoryFilterQuery.value.toLowerCase().trim();
  return supplierCategoryOptions.value.filter((category) =>
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
  const [supplierRecords, inventoryRecords, purchaseOrderRecords] =
    await Promise.all([
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
    supplierId: item.supplier_ids?.[0] || supplierIds[item.supplier] || "",
    reorderPoint: item.reorderPoint,
  }));
  // An empty response is real: never inject demo purchase orders into production.
  purchaseOrders.value = purchaseOrderRecords ?? [];
});
function resetForm() {
  form.value = {
    name: "",
    category: supplierCategories.value[0]?.name || "",
    description: "",
    contactName: "",
    contactPhone: "",
    contactEmail: "",
    delivery: "2-3 วัน",
    paymentTerms: "เครดิต 30 วัน",
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
  const supplier = selectedSupplier.value;
  if (!supplier) return;
  form.value = {
    name: supplier.name || "",
    category: supplier.category || "",
    description: supplier.description || "",
    contactName: supplier.contactName || supplier.contact_name || "",
    contactPhone:
      supplier.contactPhone ||
      supplier.contact_phone ||
      supplier.phone ||
      "",
    contactEmail:
      supplier.contactEmail ||
      supplier.contact_email ||
      supplier.email ||
      supplier.email_address ||
      "",
    delivery: supplier.delivery || "",
    paymentTerms:
      supplier.paymentTerms || supplier.payment_terms || "",
  };
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
    const supplier = await peopleApi.updateSupplier(editingSupplier.value.id, form.value);
    Object.assign(editingSupplier.value, supplier);
  } else {
    try {
      const supplier = await peopleApi.createSupplier(form.value);
      suppliers.value.push({ ...supplier, sku: supplier.sku_count });
      selectedId.value = supplier.id;
      close();
      if (route.query.from === "inventory") {
        router.push({
          path: "/inventory",
          query: { supplierId: String(supplier.id) },
        });
        return;
      }
    } catch (error) {
      window.alert(error.message);
      return;
    }
  }
  close();
}
async function assignProduct() {
  // ผูกสินค้าที่เลือกเข้ากับซัพพลายเออร์ปัจจุบัน
  const product = products.value.find(
    (item) => item.sku === productToAssign.value,
  );
  if (!product) return;
  await peopleApi.linkProduct(selectedId.value, product.sku);
  product.supplierId = selectedId.value;
  productToAssign.value = "";
}
async function removeSupplierProduct(product) {
  await peopleApi.unlinkProduct(selectedId.value, product.sku);
  product.supplierId = "";
}
function selectSupplierCategory(category) {
  supplierCategoryFilter.value = category;
  supplierCategoryFilterQuery.value = "";
  showSupplierCategoryFilter.value = false;
}
function orderStatusClass(status) {
  if (["รับของเรียบร้อยแล้ว", "สำเร็จ"].includes(status)) return "success-tag";
  if (["รอดำเนินการ", "รอของมาส่ง"].includes(status)) return "warning-tag";
  return "code-tag";
}
async function updatePurchaseOrderStatus(order) {
  await operationsApi.update("purchaseOrders", order.id, order);
  notify(`อัปเดต ${order.id} เป็น ${order.status} แล้ว`);
}
async function completePurchaseOrder(order) {
  order.status = "สำเร็จ";
  order.completedAt = new Date().toISOString();
  await operationsApi.update("purchaseOrders", order.id, order);
  notify(`${order.id} รับของเรียบร้อยและปิดรายการสำเร็จแล้ว`);
}
</script>

<template>
  <AppShell>
    <AppPageHeader
      eyebrow="SUPPLIER & SOURCING"
      title="ศูนย์จัดการซัพพลายเออร์และสินค้า"
      description="Suppliers & Sourcing Hub"
    />
    <div v-if="isInventorySupplierFlow" class="supplier-page">
      <section class="operations-table-section supplier-workspace">
        <div class="task-table-heading">
          <div>
            <h2 class="section-heading">เพิ่มซัพพลายเออร์จากฟอร์มสินค้า</h2>
            <p class="section-caption">
              UC-03-08 · ใช้เฉพาะการลงทะเบียนคู่ค้า แล้วกลับไปกรอกสินค้า
            </p>
          </div>
          <button type="button" class="button primary" @click="openAdd">
            <SvgIcon name="plus" />เพิ่มซัพพลายเออร์
          </button>
        </div>
        <button type="button" class="button secondary"
          @click="router.push('/inventory')">กลับไปคลังสินค้า</button>
      </section>
    </div>
    <div v-else class="supplier-page">
      <section class="operations-table-section supplier-workspace">
        <div class="task-table-heading">
          <div>
            <h2 class="section-heading">ภาพรวมคู่ค้า</h2>
            <p class="section-caption">
              ค้นหา เลือกคู่ค้า และจัดการรายการสินค้าที่เกี่ยวข้อง
            </p>
          </div>
          <button class="button primary" @click="openAdd">
            <SvgIcon name="plus" />เพิ่มซัพพลายเออร์
          </button>
        </div>
        <div class="task-overview-grid supplier-overview-grid">
          <div>
            <span>ซัพพลายเออร์ทั้งหมด</span
            ><strong>{{ suppliers.length }} <small>ราย</small></strong
            ><small>พร้อมใช้กับการจัดซื้อ</small>
          </div>
          <div>
            <span>หมวดหมู่คู่ค้า</span
            ><strong>{{ supplierCategoryOptions.length }} <small>หมวด</small></strong
            ><small>จัดการจากฐานข้อมูล</small>
          </div>
          <div>
            <span>สินค้าที่ผูกแล้ว</span
            ><strong>{{ linkedProductCount }} <small>SKU</small></strong
            ><small>กำหนดแหล่งจัดซื้อแล้ว</small>
          </div>
        </div>
        <div
          class="task-table-tools table-filters-below-overview supplier-table-toolbar"
        >
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
              <span>หมวดหมู่</span><strong>{{ supplierCategoryFilter }}</strong
              ><SvgIcon
                class="supplier-category-chevron"
                name="chevron-right"
                size="16"
              />
            </button>
            <div
              v-if="showSupplierCategoryFilter"
              id="supplier-category-options"
              class="category-picker-menu"
            >
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
                >
                  ทั้งหมด
                </button>
                <button
                  v-for="category in filteredSupplierCategories"
                  :key="category.category_id || category.name"
                  type="button"
                  :class="{
                    selected: supplierCategoryFilter === category.name,
                  }"
                  @click="selectSupplierCategory(category.name)"
                >
                  {{ category.name }}
                </button>
                <p
                  v-if="!filteredSupplierCategories.length"
                  class="category-empty"
                >
                  ไม่พบหมวดหมู่ที่ค้นหา
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="table-scroll employee-directory-table-wrap">
          <table
            class="data-table employee-directory-table supplier-directory-table"
          >
            <thead>
              <tr>
                <th>ซัพพลายเออร์</th>
                <th>หมวดหมู่</th>
                <th>ผู้ติดต่อ</th>
                <th>ระยะเวลาจัดส่ง</th>
                <th>เงื่อนไขชำระเงิน</th>
                <th>SKU</th>
                <th aria-label="เปิดรายละเอียด"></th>
              </tr>
            </thead>
            <tbody>
              <template v-for="supplier in visibleSuppliers" :key="supplier.id">
                <tr
                  class="employee-directory-row supplier-table-row"
                  :class="{ selected: selectedId === supplier.id }"
                  :aria-expanded="selectedId === supplier.id"
                  tabindex="0"
                  @click="toggleSupplier(supplier.id)"
                  @keydown.enter.prevent="toggleSupplier(supplier.id)"
                  @keydown.space.prevent="toggleSupplier(supplier.id)"
                >
                  <td>
                    <strong>{{ supplier.name }}</strong
                    ><small class="table-subtext">{{
                      supplier.description || "ยังไม่มีรายละเอียด"
                    }}</small>
                  </td>
                  <td>
                    <span class="code-tag">{{ supplier.category }}</span>
                  </td>
                  <td class="supplier-contact">
                    <strong>{{ supplier.contactName || "ยังไม่ระบุ" }}</strong
                    ><small class="table-subtext">{{
                      supplier.contactPhone || "ยังไม่ระบุเบอร์โทร"
                    }}</small
                    ><small
                      v-if="supplier.contactEmail"
                      class="table-subtext"
                      >{{ supplier.contactEmail }}</small
                    >
                  </td>
                  <td>{{ supplier.delivery || "ยังไม่ระบุ" }}</td>
                  <td>{{ supplier.paymentTerms || "ยังไม่ระบุ" }}</td>
                  <td>{{ supplier.sku }} SKU</td>
                  <td class="supplier-table-action">
                    <button
                      class="icon-button"
                      :aria-label="`ดูรายละเอียด ${supplier.name}`"
                      @click.stop="toggleSupplier(supplier.id)"
                    >
                      <SvgIcon
                        class="supplier-table-chevron"
                        name="chevron-right"
                        size="20"
                      />
                    </button>
                  </td>
                </tr>
                <tr
                  v-if="selectedId === supplier.id"
                  :id="`supplier-detail-${supplier.id}`"
                  class="employee-detail-row supplier-detail-row"
                >
                  <td colspan="7">
                    <div
                      class="detail-card employee-inline-detail supplier-inline-detail"
                    >
                      <div class="detail-heading">
                        <div>
                          <span class="code-tag">{{ supplier.id }}</span>
                          <h2>{{ supplier.name }}</h2>
                          <p>{{ supplier.description }}</p>
                        </div>
                        <button
                          class="icon-button"
                          type="button"
                          title="แก้ไขข้อมูลซัพพลายเออร์"
                          aria-label="แก้ไขข้อมูลซัพพลายเออร์"
                          @click="openEdit"
                        >
                          <SvgIcon name="edit" size="17" />
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
                        <div>
                          <small>ผู้ติดต่อหลัก</small
                          ><strong>{{
                            supplier.contactName || "ยังไม่ระบุ"
                          }}</strong>
                        </div>
                        <div>
                          <small>ช่องทางติดต่อ</small
                          ><strong>{{
                            supplier.contactPhone || "ยังไม่ระบุ"
                          }}</strong>
                          <small>{{
                            supplier.contactEmail || "ยังไม่ระบุอีเมล"
                          }}</small>
                        </div>
                        <div>
                          <small>เงื่อนไขชำระเงิน</small
                          ><strong>{{
                            supplier.paymentTerms || "ยังไม่ระบุ"
                          }}</strong>
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
                            <th>จัดการ</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="product in supplierProducts"
                            :key="product.sku"
                          >
                            <td class="mono">{{ product.sku }}</td>
                            <td>
                              <strong>{{ product.name }}</strong
                              ><small class="table-subtext"
                                >Stock {{ product.stock }} · Reorder Point
                                {{ product.reorderPoint }}</small
                              >
                            </td>
                            <td>
                              ฿{{ product.price.toLocaleString("th-TH") }}
                            </td>
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
                            <td class="supplier-product-action">
                              <button
                                class="icon-button"
                                type="button"
                                title="เอาสินค้าออกจากซัพพลายเออร์"
                                :aria-label="`เอา ${product.name} ออกจากซัพพลายเออร์`"
                                @click="removeSupplierProduct(product)"
                              >
                                <SvgIcon name="close" size="16" />
                              </button>
                            </td>
                          </tr>
                          <tr v-if="!supplierProducts.length">
                            <td colspan="5" class="empty-state">
                              ยังไม่มีสินค้าที่ผูกกับซัพพลายเออร์รายนี้
                            </td>
                          </tr>
                        </tbody>
                      </table>
                      <TablePagination
                        :total="supplierProducts.length"
                        label="รายการสินค้า"
                      />
                      <div class="supplier-product-link">
                        <div>
                          <strong>ผูกสินค้าเข้ากับ Supplier</strong
                          ><small
                            >กำหนดแหล่งจัดซื้อให้แต่ละ SKU
                            เพื่อใช้กับงานสั่งซื้อและ Reorder</small
                          >
                        </div>
                        <div class="button-row">
                          <AppSelect
                            v-model="productToAssign"
                            class="supplier-product-select"
                            :options="
                              unassignedProducts.map((product) => ({
                                value: product.sku,
                                label: `${product.sku} · ${product.name}`,
                              }))
                            "
                            placeholder="เลือกสินค้า"
                            search-placeholder="ค้นหาสินค้า หรือ SKU"
                            aria-label="เลือกสินค้าที่จะผูก"
                          />
                          <button
                            class="button secondary"
                            type="button"
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
      <section id="purchase-orders" class="panel purchase-orders-panel">
        <div class="panel-toolbar purchase-orders-heading">
          <div>
            <h2 class="section-heading">รายการสั่งซื้อ</h2>
            <p class="section-caption">
              รายการที่สร้างจาก Reorder Point และส่งต่อให้ทีมจัดซื้อ
            </p>
          </div>
          <button
            class="button secondary"
            type="button"
            @click="showPurchaseHistory = !showPurchaseHistory"
          >
            {{
              showPurchaseHistory
                ? "ซ่อนประวัติการสั่งซื้อ"
                : "ดูประวัติการสั่งซื้อ"
            }}
          </button>
        </div>
        <div v-if="activePurchaseOrders.length" class="purchase-orders-list">
          <article
            v-for="order in activePurchaseOrders"
            :key="order.id"
            class="purchase-order-summary"
          >
            <div class="purchase-order-summary-head">
              <strong>{{ order.id }}</strong>
              <div class="purchase-order-summary-actions">
                <select
                  v-model="order.status"
                  class="table-status-select purchase-order-status-select"
                  :class="orderStatusClass(order.status)"
                  :aria-label="`เลือกสถานะ ${order.id}`"
                  @change="updatePurchaseOrderStatus(order)"
                >
                  <option v-for="status in purchaseOrderStatuses" :key="status">
                    {{ status }}
                  </option>
                </select>
                <button
                  v-if="order.status === 'รับของเรียบร้อยแล้ว'"
                  type="button"
                  class="button primary purchase-order-complete-button"
                  @click="completePurchaseOrder(order)"
                >
                  <SvgIcon name="check" size="14" />ยืนยันรับของและปิดรายการ
                </button>
              </div>
            </div>
            <small
              >สร้างเมื่อ
              {{ new Date(order.createdAt).toLocaleString("th-TH") }}</small
            >
            <ul>
              <li v-for="item in order.items" :key="item.sku">
                <span
                  >{{ item.name }} <em>{{ item.sku }}</em></span
                ><strong
                  >{{ item.quantity ?? item.qty }} {{ item.unit }}</strong
                >
              </li>
            </ul>
          </article>
        </div>
        <div v-else class="empty-state">
          ยังไม่มีรายการสั่งซื้อจากคลังสินค้า
        </div>
        <TablePagination
          :total="activePurchaseOrders.length"
          label="รายการสั่งซื้อ"
        />
        <div v-if="showPurchaseHistory" class="purchase-history-panel">
          <div class="panel-toolbar purchase-orders-heading">
            <div>
              <h3 class="section-heading">ประวัติการสั่งซื้อ</h3>
              <p class="section-caption">
                รายการสั่งซื้อที่รับของและปิดรายการสำเร็จแล้ว
              </p>
            </div>
            <span class="completed-jobs-count"
              >{{ completedPurchaseOrders.length }} รายการ</span
            >
          </div>
          <div
            v-if="completedPurchaseOrders.length"
            class="purchase-orders-list"
          >
            <article
              v-for="order in completedPurchaseOrders"
              :key="`history-${order.id}`"
              class="purchase-order-summary"
            >
              <div class="purchase-order-summary-head">
                <strong>{{ order.id }}</strong>
                <span :class="orderStatusClass(order.status)">{{
                  order.status
                }}</span>
              </div>
              <small
                >สร้างเมื่อ
                {{ new Date(order.createdAt).toLocaleString("th-TH") }} ·
                รับของเมื่อ
                {{
                  order.completedAt
                    ? new Date(order.completedAt).toLocaleString("th-TH")
                    : "—"
                }}</small
              >
              <ul>
                <li v-for="item in order.items" :key="item.sku">
                  <span
                    >{{ item.name }} <em>{{ item.sku }}</em></span
                  ><strong
                    >{{ item.quantity ?? item.qty }} {{ item.unit }}</strong
                  >
                </li>
              </ul>
            </article>
          </div>
          <div v-else class="empty-state">ยังไม่มีรายการสั่งซื้อที่สำเร็จ</div>
          <TablePagination
            :total="completedPurchaseOrders.length"
            label="ประวัติการสั่งซื้อ"
          />
        </div>
      </section>
    </div>
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <form
        class="modal product-modal supplier-modal"
        @submit.prevent="saveSupplier"
      >
        <div class="modal-heading">
          <div>
            <span class="eyebrow">SUPPLIER REGISTRATION</span>
            <h2>
              {{
                editingSupplier
                  ? "แก้ไขข้อมูลซัพพลายเออร์"
                  : "เพิ่มซัพพลายเออร์"
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
            >หมวดหมู่
            <div class="category-select-row">
              <AppSelect
                v-model="form.category"
                :options="
                  supplierCategoryOptions.map((category) => ({
                    value: category.name,
                    label: category.name,
                  }))
                "
                placeholder="เลือกหมวดหมู่ซัพพลายเออร์"
                aria-label="เลือกหมวดหมู่ซัพพลายเออร์"
                required
              >
                <template #menu-footer="{ close }">
                  <button
                    v-if="!isInventorySupplierFlow"
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
            >รายละเอียด<input
              v-model="form.description"
              placeholder="คำอธิบายและจุดเด่นของ Supplier" /></label
          ><label
            >ผู้ติดต่อหลัก<input
              v-model="form.contactName"
              required
              placeholder="ชื่อผู้ประสานงาน" /></label
          ><label
            >เบอร์โทรศัพท์ผู้ติดต่อ<input
              v-model="form.contactPhone"
              type="tel"
              required
              placeholder="เช่น 081-234-5678" /></label
          ><label
            >อีเมลผู้ติดต่อ<input
              v-model="form.contactEmail"
              type="email"
              placeholder="เช่น sales@example.com" /></label
          ><label
            >ระยะเวลาจัดส่ง<input
              v-model="form.delivery"
              required
              placeholder="เช่น 2-3 วัน" /></label
          ><label
            >เงื่อนไขชำระเงิน<input
              v-model="form.paymentTerms"
              required
              placeholder="เช่น เครดิต 30 วัน"
          /></label>
        </div>
        <div class="button-row end">
          <button type="button" class="button secondary" @click="close">
            ยกเลิก</button
          ><button type="submit" class="button primary">
            บันทึกข้อมูลซัพพลายเออร์
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
            <span class="eyebrow">SUPPLIER CATEGORY</span>
            <h2>เพิ่มหมวดหมู่ซัพพลายเออร์</h2>
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
            placeholder="เช่น อุปกรณ์โครงสร้างและติดตั้ง"
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
  >
</template>

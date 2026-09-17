<script setup>
// ไฟล์นี้แสดงข้อมูลลูกค้าและประวัติบริการ
import { ref, computed, onMounted } from "vue";
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

// รายชื่อลูกค้าที่โหลดจาก API
const customers = ref([]);
const customerTypes = ref(mockDb.get("customerTypes"));
const salesHistory = ref([]);
const installationHistory = ref([]);
const serviceHistory = ref([]);
const loading = ref(true);
onMounted(async () => {
  // โหลดลูกค้าและสินค้าใบเสนอราคาพร้อมกันเมื่อเปิดหน้า
  try {
    const [records, products, appointments, serviceTickets, sales] =
      await Promise.all([
        peopleApi.getCustomers(),
        inventoryApi.getProducts(),
        operationsApi.getAppointments(),
        operationsApi.getServiceTickets(),
        operationsApi.getSales(),
      ]);
    customers.value = records.map((item) => ({
      ...item,
      type: item.customer_type,
      system: item.system,
      contactName: item.contactName ?? item.contact_name ?? "",
      email: item.email ?? item.email_address ?? "",
      taxId: item.taxId ?? item.tax_id ?? "",
      address: item.address || emptyAddress(),
    }));
    customerTypes.value = mockDb.get("customerTypes").length
      ? mockDb.get("customerTypes")
      : mockDb.get("customerTypes");
    quoteProducts.value = products.map((item) => ({
      sku: item.sku,
      name: item.name,
      price: item.price,
      unit: item.unit,
    }));
    salesHistory.value = sales;
    installationHistory.value = appointments;
    serviceHistory.value = serviceTickets;
  } finally {
    loading.value = false;
  }
});
const activeId = ref("");
const selectedType = ref("ทั้งหมด");
const selectedStatus = ref("ทั้งหมด");
const customerQuery = ref("");
const { isOpen, open, close } = useModal();
const customerPanel = ref("profile");
const editingCustomer = ref(null);
const emptyAddress = () => ({
  houseNo: "",
  moo: "",
  soi: "",
  road: "",
  subdistrict: "",
  district: "",
  province: "",
  postalCode: "",
});
const customerForm = ref({
  name: "",
  phone: "",
  contactName: "",
  email: "",
  taxId: "",
  type: "บ้านพักอาศัย",
  address: emptyAddress(),
});
// รายการสินค้าที่เลือกไว้ในใบเสนอราคา
const quoteItems = ref([]);
const quoteProducts = ref([]);
const receiptIssued = ref(false);
const quoteTotal = computed(() =>
  quoteItems.value.reduce((sum, item) => sum + item.price * item.qty, 0),
);
const money = (value) => new Intl.NumberFormat("th-TH").format(value);
const selectedCustomer = computed(() =>
  customers.value.find((customer) => customer.id === activeId.value),
);
const selectedCustomerSales = computed(() =>
  salesHistory.value.filter(
    (sale) =>
      sale.customerCode === selectedCustomer.value?.code ||
      sale.customer === selectedCustomer.value?.name,
  ),
);
const selectedCustomerInstallations = computed(() =>
  installationHistory.value.filter(
    (item) => item.customer === selectedCustomer.value?.name,
  ),
);
const selectedCustomerServices = computed(() =>
  serviceHistory.value.filter(
    (item) => item.customer === selectedCustomer.value?.name,
  ),
);
const visibleCustomers = computed(() =>
  customers.value.filter((customer) => {
    const matchesType =
      selectedType.value === "ทั้งหมด" ||
      customer.type === selectedType.value ||
      (selectedType.value === "รอนัดตรวจเช็ก" &&
        customer.status === selectedType.value);
    const matchesQuery =
      `${customer.name} ${customer.code} ${customer.phone} ${customer.email || ""} ${customer.contactName || ""} ${customer.location}`
        .toLowerCase()
        .includes(customerQuery.value.toLowerCase());
    const matchesStatus =
      selectedStatus.value === "ทั้งหมด" ||
      customer.status === selectedStatus.value;
    return matchesType && matchesStatus && matchesQuery;
  }),
);
const customerTypeOptions = computed(() => ["ทั้งหมด", ...customerTypes.value]);
const customerStatusOptions = mockDb.get("customerStatuses");
const customerStatusClass = (status) =>
  status === "ชำระครบถ้วน" ? "success-tag" : "warning-tag";
const residentialCustomers = computed(
  () =>
    customers.value.filter((customer) => customer.type === "บ้านพักอาศัย")
      .length,
);
const businessCustomers = computed(
  () =>
    customers.value.filter((customer) => customer.type === "ธุรกิจ/โรงงาน")
      .length,
);

// เลือกลูกค้าเพื่อเปิดรายละเอียดแบบ inline ในแถวเดียวกัน
const selectCustomer = (id) => {
  // เปลี่ยนลูกค้าที่กำลังดูรายละเอียด
  if (activeId.value === id) {
    activeId.value = "";
    return;
  }
  activeId.value = id;
  customerPanel.value = "profile";
  quoteItems.value = [];
  receiptIssued.value = false;
};
const showNotice = (message) => window.alert(message);
function updateCustomerStatus(customer) {
  mockDb.set("customers", customers.value);
  showNotice(`อัปเดตสถานะบัญชี ${customer.name} แล้ว`);
}
const showCustomerTypeModal = ref(false);
const newCustomerType = ref("");
function openCreateCustomer() {
  editingCustomer.value = null;
  customerForm.value = {
    name: "",
    phone: "",
    contactName: "",
    email: "",
    taxId: "",
    type: "บ้านพักอาศัย",
    address: emptyAddress(),
  };
  open();
}
function openEditCustomer() {
  editingCustomer.value = selectedCustomer.value;
  customerForm.value = {
    name: selectedCustomer.value.name,
    phone: selectedCustomer.value.phone,
    contactName: selectedCustomer.value.contactName || "",
    email: selectedCustomer.value.email || "",
    taxId: selectedCustomer.value.taxId || "",
    type: selectedCustomer.value.type,
    address: {
      ...emptyAddress(),
      ...(selectedCustomer.value.address || {}),
      province:
        selectedCustomer.value.address?.province ||
        selectedCustomer.value.location ||
        "",
    },
  };
  open();
}
function openCustomerTypeModal() {
  newCustomerType.value = "";
  showCustomerTypeModal.value = true;
}
function saveCustomerType() {
  const type = newCustomerType.value.trim();
  if (!type) return;
  if (customerTypes.value.includes(type)) {
    showNotice("มีประเภทลูกค้านี้อยู่แล้ว");
    return;
  }
  customerTypes.value.push(type);
  mockDb.set("customerTypes", customerTypes.value);
  customerForm.value.type = type;
  showCustomerTypeModal.value = false;
}
function saveCustomer() {
  if (!customerForm.value.name.trim() || !customerForm.value.phone.trim())
    return;
  if (
    customerForm.value.type === "ธุรกิจ/โรงงาน" &&
    !customerForm.value.contactName.trim()
  ) {
    return showNotice("กรุณาระบุชื่อผู้ติดต่อของบริษัท");
  }
  const address = { ...customerForm.value.address };
  const location = [
    address.houseNo && `เลขที่ ${address.houseNo}`,
    address.moo && `หมู่ ${address.moo}`,
    address.soi && `ซอย ${address.soi}`,
    address.road && `ถนน ${address.road}`,
    address.subdistrict && `ต.${address.subdistrict}`,
    address.district && `อ.${address.district}`,
    address.province,
    address.postalCode,
  ]
    .filter(Boolean)
    .join(" ");
  const payload = { ...customerForm.value, address, location };
  if (editingCustomer.value) Object.assign(editingCustomer.value, payload);
  else {
    const id = String(90 + customers.value.length);
    const customer = {
      id,
      code: `CUST-2025-${id}`,
      status: "รอเปิดบัญชี",
      ...payload,
    };
    customers.value.unshift(customer);
    activeId.value = id;
  }
  mockDb.set("customers", customers.value);
  close();
}
function addQuote(product) {
  const item = quoteItems.value.find((row) => row.sku === product.sku);
  if (item) item.qty += 1;
  else quoteItems.value.push({ ...product, qty: 1 });
}
function createQuote() {
  if (!quoteItems.value.length)
    return showNotice("กรุณาเพิ่มสินค้าในใบเสนอราคา");
  customerPanel.value = "quote";
  showNotice("บันทึกใบเสนอราคา QT-25062 เรียบร้อย");
}
function issueReceipt() {
  if (!quoteTotal.value) return showNotice("ยังไม่มียอดสำหรับออกใบเสร็จ");
  receiptIssued.value = true;
}
</script>

<template>
  <AppShell>
    <AppPageHeader
      eyebrow="CUSTOMER & SERVICE"
      title="ระบบจัดการข้อมูลลูกค้าและประวัติการบริการ"
      description="Customer & Service History Management"
    />
    <section class="operations-table-section customer-directory-section">
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">รายการลูกค้า</h2>
          <p class="section-caption">
            จัดการข้อมูลลูกค้า ประวัติการสั่งซื้อ และงานบริการที่เกี่ยวข้อง
          </p>
        </div>
        <button
          class="button primary"
          type="button"
          @click="openCreateCustomer"
        >
          <SvgIcon name="plus" />ลงทะเบียนลูกค้าใหม่
        </button>
      </div>
      <div class="task-overview-grid">
        <div>
          <span>ลูกค้าทั้งหมด</span><strong>{{ customers.length }} ราย</strong
          ><small>ลูกค้าในระบบทั้งหมด</small>
        </div>
        <div>
          <span>บ้านพักอาศัย</span
          ><strong>{{ residentialCustomers }} ราย</strong
          ><small>กลุ่มลูกค้าบ้านพักอาศัย</small>
        </div>
        <div>
          <span>ธุรกิจและโรงงาน</span
          ><strong>{{ businessCustomers }} ราย</strong
          ><small>กลุ่มลูกค้าองค์กร</small>
        </div>
      </div>
      <div
        class="task-table-tools table-filters-below-overview customer-table-filters"
      >
        <AppSearchField
          v-model="customerQuery"
          class-name="table-filter-search"
          placeholder="ค้นหาชื่อลูกค้า, รหัสลูกค้า, เบอร์โทรศัพท์..."
          label="ค้นหาลูกค้า"
        />
        <div class="table-filter-select control-field app-select-filter">
          <span>ประเภทลูกค้า</span>
          <AppSelect
            v-model="selectedType"
            :options="customerTypeOptions"
            search-placeholder="ค้นหาประเภทลูกค้า"
            aria-label="กรองประเภทลูกค้า"
          />
        </div>
        <div class="table-filter-select control-field app-select-filter">
          <span>สถานะ</span>
          <AppSelect
            v-model="selectedStatus"
            :options="customerStatusOptions"
            search-placeholder="ค้นหาสถานะลูกค้า"
            aria-label="กรองสถานะลูกค้า"
          />
        </div>
      </div>
      <div class="table-scroll supplier-directory-table-wrap">
        <table
          class="data-table supplier-directory-table customer-directory-table"
        >
          <thead>
            <tr>
              <th>ลูกค้า</th>
              <th>รหัสลูกค้า</th>
              <th>ช่องทางติดต่อ</th>
              <th>ที่อยู่ / สถานที่ติดต่อ</th>
              <th>ประเภทลูกค้า</th>
              <th>สถานะบัญชี</th>
              <th aria-label="เปิดรายละเอียด"></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="customer in visibleCustomers" :key="customer.id">
              <tr
                class="supplier-table-row"
                :class="{ selected: activeId === customer.id }"
                :aria-expanded="activeId === customer.id"
                tabindex="0"
                @click="selectCustomer(customer.id)"
                @keydown.enter.prevent="selectCustomer(customer.id)"
                @keydown.space.prevent="selectCustomer(customer.id)"
              >
                <td>
                  <strong>{{ customer.name }}</strong>
                </td>
                <td>
                  <span class="code-tag">{{ customer.code }}</span>
                </td>
                <td>
                  <strong>{{ customer.contactName || customer.phone }}</strong>
                  <small class="table-subtext">{{
                    customer.contactName ? customer.phone : ""
                  }}</small>
                  <small v-if="customer.email" class="table-subtext">{{
                    customer.email
                  }}</small>
                </td>
                <td class="supplier-description">{{ customer.location }}</td>
                <td>{{ customer.type || "—" }}</td>
                <td>
                  <select
                    class="table-status-select"
                    :class="customerStatusClass(customer.status)"
                    v-model="customer.status"
                    aria-label="เลือกสถานะบัญชีลูกค้า"
                    @click.stop
                    @change="updateCustomerStatus(customer)"
                  >
                    <option
                      v-for="status in customerStatusOptions.slice(1)"
                      :key="status"
                    >
                      {{ status }}
                    </option>
                  </select>
                </td>
                <td class="supplier-table-action">
                  <button
                    class="icon-button"
                    :aria-label="`ดูรายละเอียด ${customer.name}`"
                    @click.stop="selectCustomer(customer.id)"
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
                v-if="activeId === customer.id"
                :id="`customer-detail-${customer.id}`"
                class="supplier-detail-row"
              >
                <td colspan="7">
                  <div
                    class="detail-card supplier-inline-detail customer-inline-detail"
                  >
                    <div class="detail-heading">
                      <div>
                        <span class="code-tag">{{ selectedCustomer.code }}</span
                        ><span class="success-tag">Tier-A VIP</span>
                        <h2>{{ selectedCustomer.name }}</h2>
                        <p>
                          {{ selectedCustomer.phone }} สถานที่ติดตั้ง:
                          {{ selectedCustomer.location }}
                        </p>
                      </div>
                      <div class="button-row">
                        <button
                          class="button secondary"
                          @click="openEditCustomer"
                        >
                          <SvgIcon name="edit" />แก้ไขข้อมูล
                        </button>
                      </div>
                    </div>
                    <div v-if="customerPanel === 'profile'" class="info-grid">
                      <div>
                        <small>ระบบที่ติดตั้ง</small
                        ><strong>{{ selectedCustomer.system }}</strong>
                      </div>
                      <div>
                        <small>สถานะบัญชี</small
                        ><strong class="text-success">{{
                          selectedCustomer.status
                        }}</strong>
                      </div>
                      <div>
                        <small>ประวัติการบริการ</small
                        ><strong>ตรวจเช็กครั้งล่าสุด 12 มิ.ย. 2025</strong>
                      </div>
                      <div>
                        <small>ผู้ติดต่อ</small
                        ><strong>{{
                          selectedCustomer.contactName || selectedCustomer.name
                        }}</strong>
                      </div>
                      <div>
                        <small>อีเมล</small
                        ><strong>{{
                          selectedCustomer.email || "ยังไม่ระบุ"
                        }}</strong>
                      </div>
                      <div>
                        <small>เลขประจำตัวผู้เสียภาษี</small
                        ><strong>{{
                          selectedCustomer.taxId || "ยังไม่ระบุ"
                        }}</strong>
                      </div>
                    </div>
                    <h3 v-if="customerPanel === 'profile'">นัดหมายติดตั้ง</h3>
                    <table
                      v-if="customerPanel === 'profile'"
                      class="data-table"
                    >
                      <thead>
                        <tr>
                          <th>เลขที่งาน</th>
                          <th>วันนัดหมาย</th>
                          <th>ช่วงเวลา</th>
                          <th>รายละเอียดงาน</th>
                          <th>สถานะ</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in selectedCustomerInstallations"
                          :key="item.id"
                        >
                          <td>
                            <span class="sku-code">{{ item.id }}</span>
                          </td>
                          <td>{{ item.date }}</td>
                          <td>{{ item.time }}</td>
                          <td>
                            {{ item.type
                            }}<small class="table-subtext">{{
                              item.site
                            }}</small>
                          </td>
                          <td>
                            <span
                              :class="
                                item.status === 'ยืนยันแล้ว'
                                  ? 'success-tag'
                                  : 'warning-tag'
                              "
                              >{{ item.status }}</span
                            >
                          </td>
                        </tr>
                        <tr v-if="!selectedCustomerInstallations.length">
                          <td colspan="5" class="empty-state">
                            ยังไม่มีนัดหมายติดตั้ง
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <TablePagination
                      v-if="customerPanel === 'profile'"
                      :total="selectedCustomerInstallations.length"
                      label="นัดหมายติดตั้ง"
                    />
                    <h3 v-if="customerPanel === 'profile'">บริการหลังการขาย</h3>
                    <table
                      v-if="customerPanel === 'profile'"
                      class="data-table"
                    >
                      <thead>
                        <tr>
                          <th>เลขที่งาน</th>
                          <th>วันที่นัดหมาย</th>
                          <th>รายละเอียด</th>
                          <th>ผู้รับผิดชอบ</th>
                          <th>สถานะ</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in selectedCustomerServices"
                          :key="item.id"
                        >
                          <td>
                            <span class="sku-code">{{ item.id }}</span>
                          </td>
                          <td>
                            {{ item.date
                            }}<small class="table-subtext">{{
                              item.time
                            }}</small>
                          </td>
                          <td>
                            {{ item.subject
                            }}<small class="table-subtext">{{
                              item.site
                            }}</small>
                          </td>
                          <td>{{ item.owner || item.crew || "รอมอบหมาย" }}</td>
                          <td>
                            <span
                              :class="
                                item.status === 'เสร็จสิ้น'
                                  ? 'success-tag'
                                  : 'warning-tag'
                              "
                              >{{ item.status }}</span
                            >
                          </td>
                        </tr>
                        <tr v-if="!selectedCustomerServices.length">
                          <td colspan="5" class="empty-state">
                            ยังไม่มีรายการบริการหลังการขาย
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <TablePagination
                      v-if="customerPanel === 'profile'"
                      :total="selectedCustomerServices.length"
                      label="บริการหลังการขาย"
                    />
                    <h3 v-if="customerPanel === 'profile'">
                      ประวัติการสั่งซื้อ
                    </h3>
                    <table
                      v-if="customerPanel === 'profile'"
                      class="data-table"
                    >
                      <thead>
                        <tr>
                          <th>เลขที่ขาย</th>
                          <th>รายการสินค้า</th>
                          <th>ยอดขาย</th>
                          <th>สถานะคำสั่งซื้อ</th>
                          <th>สถานะการชำระเงิน</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="sale in selectedCustomerSales"
                          :key="sale.id"
                        >
                          <td>
                            <span class="sku-code">{{ sale.id }}</span>
                          </td>
                          <td>
                            <strong>{{ sale.items[0]?.name }}</strong
                            ><small class="table-subtext">{{
                              sale.items.length > 1
                                ? `+${sale.items.length - 1} รายการ`
                                : `${sale.items[0]?.qty || 0} ${sale.items[0]?.unit || ""}`
                            }}</small>
                          </td>
                          <td class="mono">฿{{ money(sale.total) }}</td>
                          <td>
                            <span class="code-tag">{{
                              sale.orderStatus || "รอการยืนยัน"
                            }}</span>
                          </td>
                          <td>
                            <span
                              :class="
                                sale.paymentStatus === 'ชำระเรียบร้อย'
                                  ? 'success-tag'
                                  : 'warning-tag'
                              "
                              >{{ sale.paymentStatus }}</span
                            >
                          </td>
                        </tr>
                        <tr v-if="!selectedCustomerSales.length">
                          <td colspan="5" class="empty-state">
                            ยังไม่มีประวัติการสั่งซื้อ
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <TablePagination
                      v-if="customerPanel === 'profile'"
                      :total="selectedCustomerSales.length"
                      label="ประวัติการสั่งซื้อ"
                    />
                    <div
                      v-if="customerPanel === 'quote'"
                      class="customer-workspace"
                    >
                      <div class="workspace-heading">
                        <div>
                          <h3>สร้างใบเสนอราคา</h3>
                          <p>
                            เลือกสินค้าและจัดทำใบเสนอราคาให้
                            {{ selectedCustomer.name }}
                          </p>
                        </div>
                        <span class="code-tag">QT-25062 · ร่าง</span>
                      </div>
                      <div class="quote-product-grid">
                        <button
                          v-for="product in quoteProducts"
                          :key="product.sku"
                          class="quote-product"
                          @click="addQuote(product)"
                        >
                          <strong>{{ product.name }}</strong
                          ><small
                            >{{ product.sku }} · ฿{{ money(product.price) }} /
                            {{ product.unit }}</small
                          ><span><SvgIcon name="plus" />เพิ่มรายการ</span>
                        </button>
                      </div>
                      <table class="data-table">
                        <thead>
                          <tr>
                            <th>รายการ</th>
                            <th>จำนวน</th>
                            <th>รวม</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="item in quoteItems" :key="item.sku">
                            <td>{{ item.name }}</td>
                            <td>{{ item.qty }} {{ item.unit }}</td>
                            <td>฿{{ money(item.price * item.qty) }}</td>
                          </tr>
                          <tr v-if="!quoteItems.length">
                            <td colspan="3" class="empty-state">
                              ยังไม่มีรายการในใบเสนอราคา
                            </td>
                          </tr>
                        </tbody>
                      </table>
                      <TablePagination
                        :total="quoteItems.length"
                        label="รายการในใบเสนอราคา"
                      />
                      <div class="order-total">
                        <span>ยอดรวมใบเสนอราคา</span
                        ><strong>฿{{ money(quoteTotal) }}</strong>
                      </div>
                      <div class="button-row end">
                        <button
                          class="button secondary"
                          @click="customerPanel = 'profile'"
                        >
                          ยกเลิก</button
                        ><button class="button primary" @click="createQuote">
                          บันทึกใบเสนอราคา
                        </button>
                      </div>
                    </div>
                    <div
                      v-if="customerPanel === 'receipt'"
                      class="customer-workspace receipt-workspace"
                    >
                      <div class="workspace-heading">
                        <div>
                          <span class="success-tag">ชำระเงินสำเร็จ</span>
                          <h3>ออกใบเสร็จรับเงิน</h3>
                          <p>
                            สร้างใบเสร็จจากใบเสนอราคาที่บันทึกไว้สำหรับ
                            {{ selectedCustomer.name }}
                          </p>
                        </div>
                        <SvgIcon name="wallet" size="26" />
                      </div>
                      <div class="receipt-summary">
                        <span>เลขที่ใบเสร็จ</span
                        ><strong>{{
                          receiptIssued ? "RC-25062" : "รอออกเลขที่"
                        }}</strong
                        ><span>ยอดที่รับชำระ</span
                        ><strong>฿{{ money(quoteTotal || 174000) }}</strong
                        ><span>วันที่ออกเอกสาร</span><strong>วันนี้</strong>
                      </div>
                      <button
                        class="button primary full"
                        :disabled="receiptIssued"
                        @click="issueReceipt"
                      >
                        <SvgIcon name="check" />{{
                          receiptIssued ? "ออกใบเสร็จแล้ว" : "ออกใบเสร็จรับเงิน"
                        }}
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
      <TablePagination :total="visibleCustomers.length" label="รายการลูกค้า" />
    </section>
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <div class="modal product-form-modal">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">CUSTOMER REGISTRATION</span>
            <h2>ลงทะเบียนลูกค้าใหม่</h2>
          </div>
          <button class="icon-button" @click="close">
            <SvgIcon name="close" />
          </button>
        </div>
        <p class="modal-description">
          บันทึกข้อมูลสำหรับติดต่อ ออกเอกสาร และติดตามประวัติงานของลูกค้า
        </p>
        <label
          >ชื่อลูกค้า<input
            v-model="customerForm.name"
            required
            placeholder="กรอกชื่อลูกค้า"
        /></label>
        <label
          >เบอร์โทรศัพท์<input
            v-model="customerForm.phone"
            required
            placeholder="กรอกเบอร์โทรศัพท์"
        /></label>
        <div class="form-grid two customer-contact-fields">
          <label
            >อีเมลสำหรับติดต่อ<input
              v-model="customerForm.email"
              type="email"
              placeholder="เช่น contact@example.com"
          /></label>
          <label
            >เลขประจำตัวผู้เสียภาษี<input
              v-model="customerForm.taxId"
              inputmode="numeric"
              maxlength="13"
              pattern="[0-9]{13}"
              placeholder="13 หลัก (ถ้ามี)"
          /></label>
        </div>
        <label
          >ประเภทลูกค้า
          <div class="category-select-row">
            <AppSelect
              v-model="customerForm.type"
              :options="customerTypes"
              aria-label="เลือกประเภทลูกค้า"
            >
              <template #menu-footer="{ close }">
                <button
                  type="button"
                  class="app-select-add-action"
                  @click.stop="
                    close();
                    openCustomerTypeModal();
                  "
                >
                  <SvgIcon name="plus" size="15" />เพิ่มประเภทลูกค้า
                </button>
              </template>
            </AppSelect>
          </div></label
        >
        <label v-if="customerForm.type === 'ธุรกิจ/โรงงาน'"
          >ชื่อผู้ติดต่อบริษัท<input
            v-model="customerForm.contactName"
            required
            placeholder="เช่น คุณกิตติชัย มั่นคง"
        /></label>
        <div class="customer-address-fields">
          <p class="form-section-label">ที่อยู่ตามเอกสาร</p>
          <div class="form-grid two">
            <label
              >เลขที่บ้าน<input
                v-model="customerForm.address.houseNo"
                placeholder="เช่น 99/9"
            /></label>
            <label
              >หมู่ที่<input
                v-model="customerForm.address.moo"
                placeholder="เช่น 5"
            /></label>
            <label
              >ซอย<input
                v-model="customerForm.address.soi"
                placeholder="เช่น สุขุมวิท 21"
            /></label>
            <label
              >ถนน<input
                v-model="customerForm.address.road"
                placeholder="เช่น สุขุมวิท"
            /></label>
            <label
              >ตำบล / แขวง<input
                v-model="customerForm.address.subdistrict"
                placeholder="กรอกตำบลหรือแขวง"
            /></label>
            <label
              >อำเภอ / เขต<input
                v-model="customerForm.address.district"
                placeholder="กรอกอำเภอหรือเขต"
            /></label>
            <label
              >จังหวัด<input
                v-model="customerForm.address.province"
                placeholder="กรอกจังหวัด"
            /></label>
            <label
              >รหัสไปรษณีย์<input
                v-model="customerForm.address.postalCode"
                inputmode="numeric"
                maxlength="5"
                placeholder="เช่น 10110"
            /></label>
          </div>
        </div>
        <div class="button-row end">
          <button class="button secondary" @click="close">ยกเลิก</button
          ><button class="button primary" @click="saveCustomer">
            บันทึกลูกค้า
          </button>
        </div>
      </div>
    </div>
    <div
      v-if="showCustomerTypeModal"
      class="modal-backdrop"
      @click.self="showCustomerTypeModal = false"
    >
      <form class="modal category-modal" @submit.prevent="saveCustomerType">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">CUSTOMER TYPE</span>
            <h2>เพิ่มประเภทลูกค้า</h2>
          </div>
          <button
            type="button"
            class="icon-button"
            title="ปิด"
            @click="showCustomerTypeModal = false"
          >
            <SvgIcon name="close" />
          </button>
        </div>
        <label
          >ชื่อประเภทลูกค้า<input
            v-model="newCustomerType"
            required
            placeholder="เช่น โครงการ หรือหน่วยงานราชการ"
        /></label>
        <p class="form-helper">
          ประเภทจะถูกบันทึกและพร้อมเลือกใช้กับลูกค้ารายถัดไป
        </p>
        <div class="button-row end">
          <button
            type="button"
            class="button secondary"
            @click="showCustomerTypeModal = false"
          >
            ยกเลิก
          </button>
          <button type="submit" class="button primary">บันทึกประเภท</button>
        </div>
      </form>
    </div>
  </AppShell>
</template>

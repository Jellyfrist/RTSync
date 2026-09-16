<script setup>
// ไฟล์นี้แสดงข้อมูลลูกค้าและประวัติบริการ
import { ref, computed, onMounted } from "vue";
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

// รายชื่อลูกค้าที่โหลดจาก API
const customers = ref([]);
const salesHistory = ref([]);
const installationHistory = ref([]);
const serviceHistory = ref([]);
const loading = ref(true);
onMounted(async () => {
  // โหลดลูกค้าและสินค้าใบเสนอราคาพร้อมกันเมื่อเปิดหน้า
  try {
    const [records, products, appointments, serviceTickets, sales] = await Promise.all([
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
    }));
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
const customerForm = ref({
  name: "",
  phone: "",
  location: "",
  type: "บ้านพักอาศัย",
  system: "",
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
  salesHistory.value.filter((sale) =>
    sale.customerCode === selectedCustomer.value?.code ||
    sale.customer === selectedCustomer.value?.name,
  ),
);
const selectedCustomerInstallations = computed(() =>
  installationHistory.value.filter((item) => item.customer === selectedCustomer.value?.name),
);
const selectedCustomerServices = computed(() =>
  serviceHistory.value.filter((item) => item.customer === selectedCustomer.value?.name),
);
const visibleCustomers = computed(() =>
  customers.value.filter((customer) => {
    const matchesType =
      selectedType.value === "ทั้งหมด" ||
      customer.type === selectedType.value ||
      (selectedType.value === "รอนัดตรวจเช็ก" &&
        customer.status === selectedType.value);
    const matchesQuery = `${customer.name} ${customer.code} ${customer.phone} ${customer.location}`
      .toLowerCase()
      .includes(customerQuery.value.toLowerCase());
    const matchesStatus =
      selectedStatus.value === "ทั้งหมด" || customer.status === selectedStatus.value;
    return matchesType && matchesStatus && matchesQuery;
  }),
);
const customerTypeOptions = ["ทั้งหมด", "บ้านพักอาศัย", "ธุรกิจ/โรงงาน"];
const customerStatusOptions = ["ทั้งหมด", "ชำระครบถ้วน", "รอนัดตรวจเช็ก", "รอเปิดบัญชี"];
const residentialCustomers = computed(() => customers.value.filter((customer) => customer.type === "บ้านพักอาศัย").length);
const businessCustomers = computed(() => customers.value.filter((customer) => customer.type === "ธุรกิจ/โรงงาน").length);

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
function openCreateCustomer() {
  editingCustomer.value = null;
  customerForm.value = {
    name: "",
    phone: "",
    location: "",
    type: "บ้านพักอาศัย",
    system: "",
  };
  open();
}
function openEditCustomer() {
  editingCustomer.value = selectedCustomer.value;
  customerForm.value = {
    name: selectedCustomer.value.name,
    phone: selectedCustomer.value.phone,
    location: selectedCustomer.value.location,
    type: selectedCustomer.value.type,
    system: selectedCustomer.value.system,
  };
  open();
}
function saveCustomer() {
  if (!customerForm.value.name.trim() || !customerForm.value.phone.trim())
    return;
  if (editingCustomer.value)
    Object.assign(editingCustomer.value, customerForm.value);
  else {
    const id = String(90 + customers.value.length);
    const customer = {
      id,
      code: `CUST-2025-${id}`,
      status: "รอเปิดบัญชี",
      ...customerForm.value,
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
          <p class="section-caption">จัดการข้อมูลลูกค้า ประวัติการสั่งซื้อ และงานบริการที่เกี่ยวข้อง</p>
        </div>
        <button class="button primary" type="button" @click="openCreateCustomer">
          <SvgIcon name="plus" />ลงทะเบียนลูกค้าใหม่
        </button>
      </div>
      <div class="task-overview-grid">
        <div><span>ลูกค้าทั้งหมด</span><strong>{{ customers.length }} ราย</strong><small>ลูกค้าในระบบทั้งหมด</small></div>
        <div><span>บ้านพักอาศัย</span><strong>{{ residentialCustomers }} ราย</strong><small>กลุ่มลูกค้าบ้านพักอาศัย</small></div>
        <div><span>ธุรกิจและโรงงาน</span><strong>{{ businessCustomers }} ราย</strong><small>กลุ่มลูกค้าองค์กร</small></div>
      </div>
      <div class="task-table-tools table-filters-below-overview customer-table-filters">
        <AppSearchField v-model="customerQuery" class-name="table-filter-search" placeholder="ค้นหาชื่อลูกค้า, รหัสลูกค้า, เบอร์โทรศัพท์..." label="ค้นหาลูกค้า" />
        <div class="table-filter-select control-field"><span>ประเภทลูกค้า</span><select v-model="selectedType" aria-label="กรองประเภทลูกค้า"><option v-for="type in customerTypeOptions" :key="type">{{ type }}</option></select></div>
        <div class="table-filter-select control-field"><span>สถานะ</span><select v-model="selectedStatus" aria-label="กรองสถานะลูกค้า"><option v-for="status in customerStatusOptions" :key="status">{{ status }}</option></select></div>
      </div>
      <div class="table-scroll supplier-directory-table-wrap">
        <table class="data-table supplier-directory-table customer-directory-table">
          <thead>
            <tr>
              <th>ลูกค้า</th>
              <th>รหัสลูกค้า</th>
              <th>เบอร์โทรศัพท์</th>
              <th>ที่อยู่ / สถานที่ติดต่อ</th>
              <th>ประเภทลูกค้า</th>
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
                <td><strong>{{ customer.name }}</strong></td>
                <td><span class="code-tag">{{ customer.code }}</span></td>
                <td>{{ customer.phone }}</td>
                <td class="supplier-description">{{ customer.location }}</td>
                <td>{{ customer.type || "—" }}</td>
                <td class="supplier-table-action">
                  <button
                    class="icon-button"
                    :aria-label="`ดูรายละเอียด ${customer.name}`"
                    @click.stop="selectCustomer(customer.id)"
                  >
                    <SvgIcon class="supplier-table-chevron" name="chevron-right" size="20" />
                  </button>
                </td>
              </tr>
              <tr
                v-if="activeId === customer.id"
                :id="`customer-detail-${customer.id}`"
                class="supplier-detail-row"
              >
                <td colspan="6">
                  <div class="detail-card supplier-inline-detail customer-inline-detail">
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
            <button class="button secondary" @click="openEditCustomer">
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
            ><strong class="text-success">{{ selectedCustomer.status }}</strong>
          </div>
          <div>
            <small>ประวัติการบริการ</small
            ><strong>ตรวจเช็กครั้งล่าสุด 12 มิ.ย. 2025</strong>
          </div>
        </div>
        <h3 v-if="customerPanel === 'profile'">นัดหมายติดตั้ง</h3>
        <table v-if="customerPanel === 'profile'" class="data-table">
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
            <tr v-for="item in selectedCustomerInstallations" :key="item.id">
              <td><span class="sku-code">{{ item.id }}</span></td>
              <td>{{ item.date }}</td>
              <td>{{ item.time }}</td>
              <td>{{ item.type }}<small class="table-subtext">{{ item.site }}</small></td>
              <td><span :class="item.status === 'ยืนยันแล้ว' ? 'success-tag' : 'warning-tag'">{{ item.status }}</span></td>
            </tr>
            <tr v-if="!selectedCustomerInstallations.length"><td colspan="5" class="empty-state">ยังไม่มีนัดหมายติดตั้ง</td></tr>
          </tbody>
        </table>
        <TablePagination v-if="customerPanel === 'profile'" :total="selectedCustomerInstallations.length" label="นัดหมายติดตั้ง" />
        <h3 v-if="customerPanel === 'profile'">บริการหลังการขาย</h3>
        <table v-if="customerPanel === 'profile'" class="data-table">
          <thead><tr><th>เลขที่งาน</th><th>วันที่นัดหมาย</th><th>รายละเอียด</th><th>ผู้รับผิดชอบ</th><th>สถานะ</th></tr></thead>
          <tbody>
            <tr v-for="item in selectedCustomerServices" :key="item.id">
              <td><span class="sku-code">{{ item.id }}</span></td>
              <td>{{ item.date }}<small class="table-subtext">{{ item.time }}</small></td>
              <td>{{ item.subject }}<small class="table-subtext">{{ item.site }}</small></td>
              <td>{{ item.owner || item.crew || "รอมอบหมาย" }}</td>
              <td><span :class="item.status === 'เสร็จสิ้น' ? 'success-tag' : 'warning-tag'">{{ item.status }}</span></td>
            </tr>
            <tr v-if="!selectedCustomerServices.length"><td colspan="5" class="empty-state">ยังไม่มีรายการบริการหลังการขาย</td></tr>
          </tbody>
        </table>
        <TablePagination v-if="customerPanel === 'profile'" :total="selectedCustomerServices.length" label="บริการหลังการขาย" />
        <h3 v-if="customerPanel === 'profile'">ประวัติการสั่งซื้อ</h3>
        <table v-if="customerPanel === 'profile'" class="data-table">
          <thead>
            <tr><th>เลขที่ขาย</th><th>รายการสินค้า</th><th>ยอดขาย</th><th>สถานะคำสั่งซื้อ</th><th>สถานะการชำระเงิน</th></tr>
          </thead>
          <tbody>
            <tr v-for="sale in selectedCustomerSales" :key="sale.id">
              <td><span class="sku-code">{{ sale.id }}</span></td>
              <td><strong>{{ sale.items[0]?.name }}</strong><small class="table-subtext">{{ sale.items.length > 1 ? `+${sale.items.length - 1} รายการ` : `${sale.items[0]?.qty || 0} ${sale.items[0]?.unit || ''}` }}</small></td>
              <td class="mono">฿{{ money(sale.total) }}</td>
              <td><span class="code-tag">{{ sale.orderStatus || "รอการยืนยัน" }}</span></td>
              <td><span :class="sale.paymentStatus === 'ชำระเรียบร้อย' ? 'success-tag' : 'warning-tag'">{{ sale.paymentStatus }}</span></td>
            </tr>
            <tr v-if="!selectedCustomerSales.length"><td colspan="5" class="empty-state">ยังไม่มีประวัติการสั่งซื้อ</td></tr>
          </tbody>
        </table>
        <TablePagination v-if="customerPanel === 'profile'" :total="selectedCustomerSales.length" label="ประวัติการสั่งซื้อ" />
        <div v-if="customerPanel === 'quote'" class="customer-workspace">
          <div class="workspace-heading">
            <div>
              <h3>สร้างใบเสนอราคา</h3>
              <p>
                เลือกสินค้าและจัดทำใบเสนอราคาให้ {{ selectedCustomer.name }}
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
          <TablePagination :total="quoteItems.length" label="รายการในใบเสนอราคา" />
          <div class="order-total">
            <span>ยอดรวมใบเสนอราคา</span
            ><strong>฿{{ money(quoteTotal) }}</strong>
          </div>
          <div class="button-row end">
            <button class="button secondary" @click="customerPanel = 'profile'">
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
            ><strong>{{ receiptIssued ? "RC-25062" : "รอออกเลขที่" }}</strong
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
      <div class="modal">
        <div class="modal-heading">
          <h2>ลงทะเบียนลูกค้าใหม่</h2>
          <button class="icon-button" @click="close">
            <SvgIcon name="close" />
          </button>
        </div>
        <label
          >ชื่อลูกค้า<input
            v-model="customerForm.name"
            required
            placeholder="กรอกชื่อลูกค้า" /></label
        ><label
          >เบอร์โทรศัพท์<input
            v-model="customerForm.phone"
            required
            placeholder="กรอกเบอร์โทรศัพท์" /></label
        ><label
          >ประเภทลูกค้า<select v-model="customerForm.type">
            <option>บ้านพักอาศัย</option>
            <option>ธุรกิจ/โรงงาน</option>
          </select></label
        ><label
          >สถานที่ติดตั้ง<input
            v-model="customerForm.location"
            placeholder="กรอกจังหวัด/สถานที่" /></label
        ><label
          >ระบบที่ติดตั้ง<input
            v-model="customerForm.system"
            placeholder="เช่น 10 kWp On-Grid"
        /></label>
        <div class="button-row end">
          <button class="button secondary" @click="close">ยกเลิก</button
          ><button class="button primary" @click="saveCustomer">
            บันทึกลูกค้า
          </button>
        </div>
      </div>
    </div>
  </AppShell>
</template>

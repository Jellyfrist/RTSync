<script setup>
// ไฟล์นี้จัดการรายการขาย ใบเสนอราคา นัดหมายติดตั้ง และงานบริการหลังการขาย
import { computed, onMounted, ref, watch } from "vue";
import AppShell from "@/components/layout/AppShell.vue";
import AppPageHeader from "@/components/ui/AppPageHeader.vue";
import AppSearchField from "@/components/ui/AppSearchField.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import TablePagination from "@/components/TablePagination.vue";
import OperationsCalendar from "@/components/OperationsCalendar.vue";
import { operationsApi } from "@/api/operationsApi";
import { mockDb } from "@/api/mockDb";
import { pricingDecision } from "@/api/pricingPolicy";

const props = defineProps({ initialTab: { type: String, default: "sales" } });
const activeTab = ref(props.initialTab);
watch(
  () => props.initialTab,
  (nextTab) => {
    activeTab.value = nextTab;
  },
);
const pageMeta = computed(
  () =>
    ({
      sales: {
        eyebrow: "SALES & QUOTATIONS",
        title: "การขายและใบเสนอราคา",
        description:
          "ตรวจสอบ Stock ก่อนขาย ออกใบเสนอราคา รับมัดจำ และยืนยันคำสั่งซื้อ",
      },
      appointments: {
        eyebrow: "INSTALLATION SCHEDULE",
        title: "การติดตั้ง",
        description:
          "จัดตารางทีมช่าง นัดหมายลูกค้า เปลี่ยนวันนัด และติดตามสถานะหน้างาน",
      },
      service: {
        eyebrow: "AFTER-SALES SERVICE",
        title: "บริการหลังการขาย",
        description:
          "รับแจ้งปัญหา จัดคิวบริการ นัดหมายช่าง และเก็บประวัติการดูแลลูกค้า",
      },
    })[props.initialTab] || {
      eyebrow: "CUSTOMER OPERATIONS",
      title: "การขายและใบเสนอราคา",
      description: "จัดการงานลูกค้าตามขั้นตอนของ RTSync",
    },
);
const toast = ref("");
const showAppointmentForm = ref(false);
const showServiceForm = ref(false);
const showQuotationForm = ref(false);
const employeeOptions = [
  "ณัฐพล แสนสุข",
  "กิตติชัย มั่นคง",
  "วราภรณ์ วงศ์ศิริ",
];
const employeeSearch = ref("");
const filteredEmployeeOptions = computed(() => {
  const query = employeeSearch.value.trim().toLocaleLowerCase("th-TH");
  if (!query) return employeeOptions;
  return employeeOptions.filter((employee) =>
    employee.toLocaleLowerCase("th-TH").includes(query),
  );
});
const customerOptions = [
  "คุณสมศักดิ์ วัฒนกุล",
  "บริษัท พลังงานไทย จำกัด",
  "บจก. ธนทรัพย์ โลจิสติกส์",
  "คุณกมลชนก สุขใจ",
];
const customerSearch = ref("");
const filteredCustomerOptions = computed(() => {
  const query = customerSearch.value.trim().toLocaleLowerCase("th-TH");
  const matches = customerOptions.filter((customer) =>
    customer.toLocaleLowerCase("th-TH").includes(query),
  );
  const selectedCustomer = newAppointment.value.customer || newTicket.value.customer;
  if (selectedCustomer && !matches.includes(selectedCustomer)) {
    return [selectedCustomer, ...matches];
  }
  return matches;
});
const newAppointment = ref({
  customer: "คุณสมศักดิ์ วัฒนากุล",
  date: "",
  time: "09:00–12:00",
  employees: ["ณัฐพล แสนสุข"],
  type: "ติดตั้งระบบ",
});
// สินค้าแนะนำที่โหลดจาก API งานปฏิบัติการ
const catalog = [];
const bill = ref([]);
const quotationForm = ref({
  customer: "คุณสมศักดิ์ วัฒนกุล",
  quoteId: "QT-25061",
  issuedAt: new Date().toISOString().slice(0, 10),
  validUntil: "",
  notes: "",
});
const selectedQuoteSku = ref("");
const selectedQuoteQty = ref(1);
const salesOrders = ref([]);
const salesSearch = ref("");
const paymentStatusFilter = ref("ทั้งหมด");
const orderStatusFilter = ref("ทั้งหมด");
const paymentStatusOptions = [
  "ทั้งหมด",
  "ชำระเรียบร้อย",
  "ชำระมัดจำ",
  "รอชำระมัดจำ",
  "รอชำระส่วนที่เหลือ",
];
const orderStatusOptions = [
  "รอการยืนยัน",
  "ยืนยันคำสั่งซื้อ",
  "กำลังเตรียมสินค้า",
  "จัดส่งแล้ว",
  "ปิดการขาย",
  "ปฏิเสธการสั่งซื้อ",
  "ยกเลิกการขาย",
];
const filteredSalesOrders = computed(() => {
  const query = salesSearch.value.trim().toLocaleLowerCase("th-TH");
  return salesOrders.value.filter((order) => {
    const searchable = `${order.id} ${order.customer} ${order.items.map((item) => item.name).join(" ")}`.toLocaleLowerCase("th-TH");
    return (orderStatusFilter.value === "ทั้งหมด" || order.orderStatus === orderStatusFilter.value)
      && (paymentStatusFilter.value === "ทั้งหมด" || order.paymentStatus === paymentStatusFilter.value)
      && searchable.includes(query);
  });
});
// นัดหมายและใบงานที่โหลดจาก backend
const appointments = ref([]);
const serviceTickets = ref([]);
const pendingAppointments = computed(
  () => appointments.value.filter((item) => item.status !== "เสร็จสิ้น").length,
);
const openServiceTickets = computed(
  () => serviceTickets.value.filter((item) => item.status !== "เสร็จสิ้น").length,
);
const newTicket = ref({
  customer: "คุณสมศักดิ์ วัฒนากุล",
  subject: "",
  priority: "ปกติ",
  employees: ["ณัฐพล แสนสุข"],
});
const sortedAppointments = computed(() =>
  [...appointments.value].sort((a, b) => new Date(a.date) - new Date(b.date)),
);
const sortedServiceTickets = computed(() =>
  [...serviceTickets.value].sort((a, b) => new Date(a.date) - new Date(b.date)),
);
const appointmentSearch = ref("");
const appointmentStatusFilter = ref("ทั้งหมด");
const serviceSearch = ref("");
const serviceStatusFilter = ref("ทั้งหมด");
const appointmentStatusOptions = ["ทั้งหมด", "รอยืนยัน", "ยืนยันแล้ว", "เตรียมอุปกรณ์", "กำลังติดตั้ง", "เสร็จสิ้น"];
const serviceStatusOptions = ["ทั้งหมด", "รอเปิดงาน", "รอมอบหมาย", "นัดหมายแล้ว", "กำลังเข้าบริการ", "เสร็จสิ้น"];
const filteredAppointments = computed(() => {
  const query = appointmentSearch.value.trim().toLocaleLowerCase("th-TH");
  return sortedAppointments.value.filter((item) => {
    const searchable = `${item.id} ${item.customer} ${item.site} ${item.type} ${item.employees?.join(" ") || item.crew || ""}`.toLocaleLowerCase("th-TH");
    return (appointmentStatusFilter.value === "ทั้งหมด" || item.status === appointmentStatusFilter.value) && searchable.includes(query);
  });
});
const filteredServiceTickets = computed(() => {
  const query = serviceSearch.value.trim().toLocaleLowerCase("th-TH");
  return sortedServiceTickets.value.filter((item) => {
    const searchable = `${item.id} ${item.customer} ${item.subject} ${item.employees?.join(" ") || item.owner || ""}`.toLocaleLowerCase("th-TH");
    return (serviceStatusFilter.value === "ทั้งหมด" || item.status === serviceStatusFilter.value) && searchable.includes(query);
  });
});
const showEditModal = ref(false);
const editingType = ref("");
const editingJob = ref(null);
const editForm = ref({
  customer: "",
  subject: "",
  date: "",
  time: "",
  site: "",
  priority: "ปกติ",
  status: "",
});
onMounted(async () => {
  // โหลดสินค้า นัดหมาย และใบงานพร้อมกันเมื่อเปิดหน้า
  const [catalogRecords, appointmentRecords, ticketRecords, salesRecords] = await Promise.all(
    [
      operationsApi.getCatalog(),
      operationsApi.getAppointments(),
      operationsApi.getServiceTickets(),
      operationsApi.getSales(),
    ],
  );
  catalog.splice(0, catalog.length, ...catalogRecords);
  appointments.value = appointmentRecords;
  serviceTickets.value = ticketRecords;
  salesOrders.value = salesRecords;
});
const total = computed(() =>
  bill.value.reduce((sum, item) => sum + item.price * item.qty, 0),
);
const pricingAlerts = computed(() => bill.value.map((item) => ({
  ...item,
  ...pricingDecision(item.price, item),
})).filter((item) => item.isLoss || item.belowMinimumMargin));
const lossMakingItems = computed(() => pricingAlerts.value.filter((item) => item.isLoss));
const formatCurrency = (value) => new Intl.NumberFormat("th-TH").format(value);
const notify = (message) => {
  toast.value = message;
  setTimeout(() => {
    toast.value = "";
  }, 2600);
};
function openAppointmentForm() {
  employeeSearch.value = "";
  customerSearch.value = "";
  showAppointmentForm.value = true;
}
function openServiceForm() {
  employeeSearch.value = "";
  customerSearch.value = "";
  showServiceForm.value = true;
}
function openQuotationForm() {
  showQuotationForm.value = true;
}
function addToBill(product) {
  // เพิ่มสินค้าเข้าใบเสนอราคา
  const item = bill.value.find((row) => row.sku === product.sku);
  if (item) item.qty += 1;
  else bill.value.push({ ...product, qty: 1 });
  notify(`เพิ่ม ${product.name} ลงใบเสนอราคาแล้ว`);
}
function addSelectedQuoteProduct() {
  const product = catalog.find((item) => item.sku === selectedQuoteSku.value);
  if (!product) return;
  const existing = bill.value.find((item) => item.sku === product.sku);
  if (existing) existing.qty += Math.max(Number(selectedQuoteQty.value) || 1, 1);
  else bill.value.push({ ...product, qty: Math.max(Number(selectedQuoteQty.value) || 1, 1) });
  selectedQuoteSku.value = "";
  selectedQuoteQty.value = 1;
}
function removeItem(index) {
  bill.value.splice(index, 1);
}
function saveSale() {
  if (!bill.value.length) return notify("กรุณาเลือกสินค้าอย่างน้อย 1 รายการ");
  if (lossMakingItems.value.length) return notify("ไม่สามารถบันทึกการขายที่ราคาต่ำกว่าต้นทุนได้");
  const sale = {
    id: `SO-${new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 12)}`,
    customer: "คุณสมศักดิ์ วัฒนกุล",
    customerCode: "CUST-2025-001",
    items: bill.value.map(({ sku, name, qty, unit, price, costLots, costPrice }) => ({
      sku, name, qty, unit, price,
      costAtSale: pricingDecision(price, { costLots, costPrice }).cost,
    })),
    total: total.value,
    paymentStatus: "รอชำระมัดจำ",
    orderStatus: "รอดำเนินการ",
    createdAt: new Date().toISOString(),
  };
  salesOrders.value.unshift(sale);
  mockDb.set("sales", salesOrders.value);
  bill.value = [];
  notify("บันทึกรายการขายแล้ว — พร้อมสร้างนัดหมายติดตั้ง");
}
function saveQuotation() {
  if (!bill.value.length) return notify("กรุณาเพิ่มสินค้าอย่างน้อย 1 รายการ");
  if (lossMakingItems.value.length) return notify("ไม่สามารถออกใบเสนอราคาที่ราคาต่ำกว่าต้นทุนได้");
  const customerCode = `CUST-2025-${String(customerOptions.indexOf(quotationForm.value.customer) + 1).padStart(3, "0")}`;
  const quotation = {
    id: quotationForm.value.quoteId,
    customer: quotationForm.value.customer,
    customerCode,
    issuedAt: quotationForm.value.issuedAt,
    validUntil: quotationForm.value.validUntil,
    notes: quotationForm.value.notes,
    items: bill.value.map(({ sku, name, qty, unit, price, costLots, costPrice }) => ({
      sku, name, qty, unit, price,
      costAtQuote: pricingDecision(price, { costLots, costPrice }).cost,
    })),
    total: total.value,
    status: "ร่างใบเสนอราคา",
  };
  const existing = mockDb.get("quotations");
  mockDb.set("quotations", [quotation, ...existing.filter((item) => item.id !== quotation.id)]);
  const sale = {
    ...quotation,
    paymentStatus: "รอชำระมัดจำ",
    orderStatus: "รอการยืนยัน",
    createdAt: new Date().toISOString(),
  };
  salesOrders.value = [sale, ...salesOrders.value.filter((item) => item.id !== sale.id)];
  mockDb.set("sales", salesOrders.value);
  bill.value = [];
  showQuotationForm.value = false;
  notify(`บันทึกใบเสนอราคา ${quotation.id} และเพิ่มในรายการขายแล้ว`);
}
function updateSaleStatus(order) {
  mockDb.set("sales", salesOrders.value);
  notify(`${order.id} เปลี่ยนสถานะคำสั่งซื้อเป็น ${order.orderStatus}`);
}
function updatePaymentStatus(order) {
  mockDb.set("sales", salesOrders.value);
  notify(`${order.id} เปลี่ยนสถานะการชำระเงินเป็น ${order.paymentStatus}`);
}
function closeSale(order) {
  order.orderStatus = "ปิดการขาย";
  mockDb.set("sales", salesOrders.value);
  notify(`${order.id} ปิดการขายเรียบร้อยแล้ว`);
}
function cancelSale(order) {
  order.orderStatus = "ยกเลิกการขาย";
  mockDb.set("sales", salesOrders.value);
  notify(`${order.id} ยกเลิกการขายแล้ว`);
}
function cycleAppointment(item) {
  // เลื่อนสถานะนัดหมายไปขั้นถัดไป
  const flow = [
    "รอยืนยัน",
    "ยืนยันแล้ว",
    "เตรียมอุปกรณ์",
    "กำลังติดตั้ง",
    "เสร็จสิ้น",
  ];
  const next = flow[(flow.indexOf(item.status) + 1) % flow.length];
  item.status = next;
  notify(`${item.id} เปลี่ยนสถานะเป็น ${next}`);
}
function cycleServiceTicket(ticket) {
  const flow = ["รอเปิดงาน", "รอมอบหมาย", "นัดหมายแล้ว", "กำลังเข้าบริการ", "เสร็จสิ้น"];
  const next = flow[(flow.indexOf(ticket.status) + 1) % flow.length];
  ticket.status = next;
  notify(`${ticket.id} เปลี่ยนสถานะเป็น ${next}`);
}
function statusClass(status) {
  if (["เสร็จสิ้น", "ยืนยันแล้ว"].includes(status)) return "success-tag";
  if (["รอยืนยัน", "รอมอบหมาย", "รอเปิดงาน"].includes(status)) return "warning-tag";
  return "code-tag";
}
function paymentStatusClass(status) {
  if (status === "ชำระเรียบร้อย") return "success-tag";
  if (["ชำระมัดจำ", "รอชำระมัดจำ", "รอชำระส่วนที่เหลือ"].includes(status)) return "warning-tag";
  return "code-tag";
}
function formatJobDate(date) {
  if (!date) return "ยังไม่ระบุ";
  return new Intl.DateTimeFormat("th-TH-u-ca-gregory", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${date}T00:00:00`));
}
function openEditModal(item, type) {
  editingType.value = type;
  editingJob.value = item;
  editForm.value = {
    customer: item.customer || "",
    subject: item.subject || "",
    date: item.date || "",
    time: item.time || "",
    site: item.site || "",
    priority: item.priority || "ปกติ",
    status: item.status || "",
  };
  showEditModal.value = true;
}
function saveEdit() {
  if (!editingJob.value) return;
  Object.assign(editingJob.value, editForm.value);
  showEditModal.value = false;
  notify(`บันทึกรายละเอียด ${editingJob.value.id} แล้ว`);
}
function createTicket() {
  if (!newTicket.value.subject.trim()) return notify("กรุณาระบุหัวข้อปัญหา");
  if (!newTicket.value.employees.length)
    return notify("กรุณาเลือกพนักงานอย่างน้อย 1 คน");
  serviceTickets.value.unshift({
    id: `SRV-250${43 + serviceTickets.value.length}`,
    customer: newTicket.value.customer,
    subject: newTicket.value.subject,
    opened: "วันนี้",
    priority: newTicket.value.priority,
    status: "รับเรื่องใหม่",
    owner: "รอมอบหมาย",
    employees: [...newTicket.value.employees],
  });
  mockDb.set("serviceTickets", serviceTickets.value);
  newTicket.value.subject = "";
  newTicket.value.employees = ["ณัฐพล แสนสุข"];
  showServiceForm.value = false;
  notify("เปิดใบงานบริการหลังการขายแล้ว");
}
function closeTicket(ticket) {
  ticket.status = "เสร็จสิ้น";
  notify(`${ticket.id} ปิดงานเรียบร้อย`);
}
function createAppointment() {
  if (!newAppointment.value.date) return notify("กรุณาเลือกวันที่นัดหมาย");
  if (!newAppointment.value.employees.length)
    return notify("กรุณาเลือกพนักงานอย่างน้อย 1 คน");
  appointments.value.push({
    id: `INS-25062${appointments.value.length}`,
    customer: newAppointment.value.customer,
    site: "รอระบุสถานที่",
    date: newAppointment.value.date,
    time: newAppointment.value.time,
    crew: newAppointment.value.employees.join(" · "),
    employees: [...newAppointment.value.employees],
    status: "รอยืนยัน",
    type: newAppointment.value.type,
  });
  mockDb.set("appointments", appointments.value);
  showAppointmentForm.value = false;
  newAppointment.value.date = "";
  notify("สร้างนัดหมายใหม่แล้ว");
}
</script>

<template>
  <AppShell>
    <AppPageHeader
      :eyebrow="pageMeta.eyebrow"
      :title="pageMeta.title"
      :description="pageMeta.description"
    >
      <template #actions>
        <div class="button-row page-actions">
        </div>
      </template>
    </AppPageHeader>
    <OperationsCalendar
      v-if="activeTab === 'appointments'"
      :items="appointments"
      mode="installation"
      class="top-operations-calendar"
    ><template #detail-actions><button class="button primary full" type="button" @click="openAppointmentForm"><SvgIcon name="plus" />สร้างนัดหมาย</button></template></OperationsCalendar>
    <OperationsCalendar
      v-else-if="activeTab === 'service'"
      :items="serviceTickets"
      mode="service"
      class="top-operations-calendar"
    ><template #detail-actions><button class="button primary full" type="button" @click="openServiceForm"><SvgIcon name="plus" />เพิ่มงานบริการ</button></template></OperationsCalendar>
    <div v-if="!props.initialTab" class="section-divider">
      <span class="section-kicker">02</span>
      <div><strong>พื้นที่ปฏิบัติงาน</strong><small>จัดการงานตามโมดูลที่เลือกจากเมนูด้านข้าง</small></div>
    </div>
    <nav
      v-if="!props.initialTab"
      class="inventory-tabs operations-tabs"
      aria-label="เมนูงานลูกค้า"
    >
      <button
        :class="{ active: activeTab === 'sales' }"
        @click="activeTab = 'sales'"
      >
        <SvgIcon name="quote" />ขายสินค้า <span>ใบเสนอราคา</span></button
      ><button
        :class="{ active: activeTab === 'appointments' }"
        @click="activeTab = 'appointments'"
      >
        <SvgIcon name="solar" />นัดหมายติดตั้ง
        <span>{{ appointments.length }}</span></button
      ><button
        :class="{ active: activeTab === 'service' }"
        @click="activeTab = 'service'"
      >
        <SvgIcon name="settings" />บริการหลังการขาย
        <span>{{ serviceTickets.length }}</span>
      </button>
    </nav>
    <section v-if="activeTab === 'sales'" class="operations-table-section sales-orders-section">
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">รายการขาย</h2>
          <p class="section-caption">รายการขายที่เกิดขึ้นจริง ติดตามสินค้า ยอดขาย และสถานะการชำระเงิน</p>
        </div>
        <button class="button primary" type="button" @click="openQuotationForm">
          <SvgIcon name="plus" />ออกใบเสนอราคา
        </button>
      </div>
      <div class="task-overview-grid">
        <div><span>รายการขายทั้งหมด</span><strong>{{ filteredSalesOrders.length }}</strong><small>รายการในมุมมองนี้</small></div>
        <div><span>รอการชำระเงิน</span><strong>{{ filteredSalesOrders.filter((order) => order.paymentStatus !== 'ชำระเรียบร้อย').length }}</strong><small>ต้องติดตามต่อ</small></div>
        <div><span>ยอดขายรวม</span><strong>฿{{ formatCurrency(filteredSalesOrders.reduce((sum, order) => sum + order.total, 0)) }}</strong><small>จากรายการที่แสดง</small></div>
      </div>
      <div class="task-table-tools table-filters-below-overview sales-table-filters">
        <AppSearchField v-model="salesSearch" class-name="table-filter-search" placeholder="ค้นหาเลขที่ขาย ชื่อลูกค้า หรือสินค้า..." label="ค้นหารายการขาย" />
        <div class="table-filter-select control-field"><span>สถานะคำสั่งซื้อ</span><select v-model="orderStatusFilter" aria-label="กรองสถานะคำสั่งซื้อ"><option value="ทั้งหมด">ทั้งหมด</option><option v-for="status in orderStatusOptions" :key="status">{{ status }}</option></select></div>
        <div class="table-filter-select control-field"><span>สถานะการชำระเงิน</span><select v-model="paymentStatusFilter" aria-label="กรองสถานะการชำระเงิน"><option v-for="status in paymentStatusOptions" :key="status">{{ status }}</option></select></div>
      </div>
      <div class="table-scroll">
        <table class="data-table operations-table sales-orders-table">
          <thead><tr><th>เลขที่ขาย</th><th>ลูกค้า</th><th>รายการสินค้า</th><th>ยอดขาย</th><th>สถานะคำสั่งซื้อ</th><th>สถานะการชำระเงิน</th><th>จัดการ</th></tr></thead>
          <tbody>
            <tr v-for="order in filteredSalesOrders" :key="order.id">
              <td><span class="sku-code">{{ order.id }}</span><small class="table-subtext">{{ new Date(order.createdAt).toLocaleDateString('th-TH') }}</small></td>
              <td><strong>{{ order.customer }}</strong><small class="table-subtext">{{ order.customerCode }}</small></td>
              <td><strong>{{ order.items[0]?.name }}</strong><small class="table-subtext">{{ order.items.length > 1 ? `+${order.items.length - 1} รายการ` : `${order.items[0]?.qty || 0} ${order.items[0]?.unit || ''}` }}</small></td>
              <td class="mono">฿{{ formatCurrency(order.total) }}</td>
              <td><select class="table-status-select" :class="statusClass(order.orderStatus)" v-model="order.orderStatus" aria-label="เลือกสถานะคำสั่งซื้อ" @change="updateSaleStatus(order)"><option v-for="status in orderStatusOptions" :key="status">{{ status }}</option></select></td>
              <td><select class="table-status-select" :class="paymentStatusClass(order.paymentStatus)" v-model="order.paymentStatus" aria-label="เลือกสถานะการชำระเงิน" @change="updatePaymentStatus(order)"><option v-for="status in paymentStatusOptions.slice(1)" :key="status">{{ status }}</option></select></td>
              <td><button v-if="order.orderStatus !== 'ปฏิเสธการสั่งซื้อ'" class="button secondary table-button sales-status-button" type="button" @click="closeSale(order)"><SvgIcon name="check" size="14" />ปิดการขาย</button><button v-else class="button secondary table-button sales-status-button" type="button" @click="cancelSale(order)"><SvgIcon name="close" size="14" />ยกเลิกการขาย</button></td>
            </tr>
            <tr v-if="!filteredSalesOrders.length"><td colspan="7" class="empty-state">ยังไม่มีรายการขายที่ตรงกับตัวกรอง</td></tr>
          </tbody>
        </table>
      </div>
      <TablePagination :total="filteredSalesOrders.length" label="รายการขาย" />
    </section>
    <div v-if="activeTab === 'sales' && showQuotationForm" class="modal-backdrop" @click.self="showQuotationForm = false">
      <form class="modal quotation-modal" @submit.prevent="saveQuotation">
        <div class="modal-heading">
          <div>
            <h2>ออกใบเสนอราคา</h2>
            <p class="modal-caption">เลือกสินค้าและจัดทำใบเสนอราคาก่อนเปลี่ยนเป็นรายการขาย</p>
          </div>
          <button type="button" class="icon-button" title="ปิด" aria-label="ปิดฟอร์มออกใบเสนอราคา" @click="showQuotationForm = false">
            <SvgIcon name="close" />
          </button>
        </div>
        <div class="quotation-form">
        <div class="form-grid">
          <label>ลูกค้า<select v-model="quotationForm.customer" required><option v-for="customer in customerOptions" :key="customer">{{ customer }}</option></select></label>
          <label>เลขที่ใบเสนอราคา<input v-model="quotationForm.quoteId" required /></label>
          <label>วันที่ออกใบเสนอราคา<input v-model="quotationForm.issuedAt" type="date" required /></label>
          <label>วันหมดอายุ<input v-model="quotationForm.validUntil" type="date" /></label>
        </div>
        <label>หมายเหตุเพิ่มเติม<textarea v-model="quotationForm.notes" rows="3" placeholder="รายละเอียดเงื่อนไขการเสนอราคา หรือหมายเหตุถึงลูกค้า"></textarea></label>
        <div class="quotation-items-section">
          <div class="quotation-items-heading"><div><h3>รายการสินค้าในใบเสนอราคา</h3><p>เลือกสินค้าและระบุจำนวนที่ต้องการเสนอให้ลูกค้า</p></div></div>
          <div class="quotation-item-picker">
            <label>สินค้า<select v-model="selectedQuoteSku"><option value="">เลือกสินค้าจากคลัง</option><option v-for="product in catalog" :key="product.sku" :value="product.sku">{{ product.name }} · {{ product.sku }} · ฿{{ formatCurrency(product.price) }}</option></select></label>
            <label>จำนวน<input v-model.number="selectedQuoteQty" type="number" min="1" /></label>
            <button type="button" class="button secondary" :disabled="!selectedQuoteSku" @click="addSelectedQuoteProduct"><SvgIcon name="plus" />เพิ่มรายการ</button>
          </div>
          <div class="table-scroll">
            <table class="data-table">
              <thead><tr><th>รายการ</th><th>จำนวน</th><th>ราคา</th><th>รวม</th><th></th></tr></thead>
              <tbody>
                <tr v-for="(item, index) in bill" :key="item.sku"><td><strong>{{ item.name }}</strong><small class="table-subtext">{{ item.sku }}</small></td><td>{{ item.qty }} {{ item.unit }}</td><td>฿{{ formatCurrency(item.price) }}<small class="table-subtext pricing-meta">ต้นทุน ฿{{ formatCurrency(pricingDecision(item.price, item).cost) }} · กำไร {{ Math.round(pricingDecision(item.price, item).marginRate * 100) }}%</small></td><td>฿{{ formatCurrency(item.price * item.qty) }}</td><td><button type="button" class="icon-button" title="ลบรายการ" @click="removeItem(index)"><SvgIcon name="close" /></button></td></tr>
                <tr v-if="!bill.length"><td colspan="5" class="empty-state">ยังไม่มีรายการสินค้า กรุณาเลือกสินค้าด้านบน</td></tr>
              </tbody>
            </table>
          </div>
          <TablePagination :total="bill.length" label="รายการในใบเสนอราคา" />
        </div>
        <div v-if="pricingAlerts.length" class="form-helper pricing-warning" role="alert">
          <strong>ตรวจสอบกำไร</strong>
          <span v-for="item in pricingAlerts" :key="item.sku">{{ item.name }}: ต้นทุนเฉลี่ย ฿{{ formatCurrency(item.cost) }} · แนะนำราคาขายอย่างน้อย ฿{{ formatCurrency(item.recommendedPrice) }}</span>
        </div>
        <div class="order-total"><span>ยอดรวมทั้งสิ้น</span><strong>฿{{ formatCurrency(total) }}</strong></div>
          <div class="button-row end"><button type="button" class="button secondary" @click="bill = []">ล้างฟอร์ม</button><button class="button primary" type="submit"><SvgIcon name="check" />บันทึกใบเสนอราคา</button></div>
        </div>
      </form>
    </div>
    <div
      v-if="activeTab === 'appointments' && showAppointmentForm"
        class="modal-backdrop"
        @click.self="showAppointmentForm = false"
      >
        <form class="modal" @submit.prevent="createAppointment">
          <div class="modal-heading">
            <h2>สร้างนัดหมายติดตั้ง</h2>
            <button
              type="button"
              class="icon-button"
              title="ปิด"
              @click="showAppointmentForm = false"
            >
              <SvgIcon name="close" />
            </button>
          </div>
          <label
            >ลูกค้า<div class="assignment-search">
              <SvgIcon name="search" size="16" />
              <input v-model="customerSearch" type="search" aria-label="ค้นหาลูกค้าสำหรับนัดหมายติดตั้ง" placeholder="ค้นหาชื่อลูกค้า..." />
            </div>
            <select v-model="newAppointment.customer" required>
              <option v-for="customer in filteredCustomerOptions" :key="customer" :value="customer">{{ customer }}</option>
            </select></label
          ><label
            >วันที่นัดหมาย<input
              v-model="newAppointment.date"
              type="date"
              required /></label
          ><label
            >ช่วงเวลา<select v-model="newAppointment.time">
              <option>09:00–12:00</option>
              <option>13:00–16:00</option>
              <option>09:00–15:00</option>
            </select></label
          ><fieldset class="assignment-fieldset">
            <legend>พนักงานที่ส่งไปติดตั้ง</legend>
            <div class="assignment-search">
              <SvgIcon name="search" size="16" />
              <input
                v-model="employeeSearch"
                type="search"
                aria-label="ค้นหาพนักงานที่จะส่งไปติดตั้ง"
                placeholder="ค้นหาชื่อพนักงาน..."
              />
            </div>
            <p class="field-helper">เลือกได้มากกว่า 1 คน</p>
            <label v-for="employee in filteredEmployeeOptions" :key="employee" class="assignment-option">
              <input v-model="newAppointment.employees" type="checkbox" :value="employee" />
              <span>{{ employee }}</span>
            </label>
            <p v-if="!filteredEmployeeOptions.length" class="assignment-empty">ไม่พบพนักงานที่ค้นหา</p>
          </fieldset>
          <div class="button-row end">
            <button
              type="button"
              class="button secondary"
              @click="showAppointmentForm = false"
            >
              ยกเลิก</button
            ><button class="button primary" type="submit">บันทึกนัดหมาย</button>
          </div>
        </form>
    </div>
    <section v-if="activeTab === 'appointments'" class="operations-table-section">
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">งานติดตั้งทั้งหมด</h2>
          <p class="section-caption">เรียงจากกำหนดงานที่ใกล้ที่สุด เพื่อให้ทีมวางแผนหน้างานได้ทันเวลา</p>
        </div>
        <button class="button primary" type="button" @click="openAppointmentForm">
          <SvgIcon name="plus" />สร้างนัดหมาย
        </button>
      </div>
      <div class="task-overview-grid">
        <div><span>งานทั้งหมด</span><strong>{{ filteredAppointments.length }}</strong><small>งานในมุมมองนี้</small></div>
        <div><span>งานวันนี้</span><strong>{{ sortedAppointments.filter((item) => item.date === new Date().toISOString().slice(0, 10)).length }}</strong><small>ต้องเตรียมความพร้อม</small></div>
        <div><span>ใกล้ถึงกำหนด</span><strong>{{ sortedAppointments[0] ? formatJobDate(sortedAppointments[0].date) : '—' }}</strong><small>รายการแรกในคิว</small></div>
      </div>
      <div class="task-table-tools table-filters-below-overview">
        <AppSearchField v-model="appointmentSearch" class-name="table-filter-search" placeholder="ค้นหาเลขที่งาน ลูกค้า หรือพนักงาน..." label="ค้นหางานติดตั้ง" />
        <div class="table-filter-select control-field"><span>สถานะ</span><select v-model="appointmentStatusFilter" aria-label="กรองสถานะงานติดตั้ง"><option v-for="status in appointmentStatusOptions" :key="status">{{ status }}</option></select></div>
      </div>
      <div class="table-scroll">
        <table class="data-table operations-table">
          <thead><tr><th>เลขที่งาน</th><th>ลูกค้า / สถานที่</th><th>กำหนดงาน</th><th>พนักงาน</th><th>สถานะ</th><th>จัดการ</th></tr></thead>
          <tbody>
            <tr v-for="item in filteredAppointments" :key="item.id">
              <td><span class="sku-code">{{ item.id }}</span><small class="table-subtext">{{ item.type }}</small></td>
              <td><strong>{{ item.customer }}</strong><small class="table-subtext">{{ item.site }}</small></td>
              <td><strong>{{ formatJobDate(item.date) }}</strong><small class="table-subtext">{{ item.time }}</small></td>
              <td>{{ item.employees?.join(' · ') || item.crew }}</td>
              <td><span :class="statusClass(item.status)">{{ item.status }}</span></td>
              <td><div class="table-actions"><button class="button secondary table-button table-icon-button" title="แก้ไขรายละเอียดงาน" aria-label="แก้ไขรายละเอียดงาน" @click="openEditModal(item, 'appointment')"><SvgIcon name="edit" size="15" /></button><button class="button status-action table-button" title="อัพเดตสถานะงาน" aria-label="อัพเดตสถานะงาน" @click="cycleAppointment(item)"><SvgIcon name="refresh" size="15" /><span>สถานะ</span></button></div></td>
            </tr>
            <tr v-if="!filteredAppointments.length"><td colspan="6" class="empty-state">ไม่พบงานติดตั้งที่ตรงกับตัวกรอง</td></tr>
          </tbody>
        </table>
      </div>
      <TablePagination :total="filteredAppointments.length" label="งานติดตั้ง" />
    </section>
    <section v-if="activeTab === 'service'" class="operations-service">
      <div class="operations-table-section">
        <div class="task-table-heading">
          <div>
            <h2 class="section-heading">งานบริการหลังการขายทั้งหมด</h2>
            <p class="section-caption">เรียงจากกำหนดเข้าบริการที่ใกล้ที่สุด เพื่อไม่ให้พลาดงานสำคัญ</p>
          </div>
          <button class="button primary" type="button" @click="openServiceForm">
            <SvgIcon name="plus" />เพิ่มงานบริการ
          </button>
        </div>
        <div class="task-overview-grid">
          <div><span>งานทั้งหมด</span><strong>{{ filteredServiceTickets.length }}</strong><small>งานในมุมมองนี้</small></div>
          <div><span>งานเร่งด่วน</span><strong>{{ sortedServiceTickets.filter((item) => item.priority === 'สูง' || item.priority === 'เร่งด่วน').length }}</strong><small>ต้องติดตามเป็นพิเศษ</small></div>
          <div><span>ใกล้ถึงกำหนด</span><strong>{{ sortedServiceTickets[0] ? formatJobDate(sortedServiceTickets[0].date) : '—' }}</strong><small>รายการแรกในคิว</small></div>
        </div>
        <div class="task-table-tools table-filters-below-overview">
          <AppSearchField v-model="serviceSearch" class-name="table-filter-search" placeholder="ค้นหาเลขที่งาน ลูกค้า หรือพนักงาน..." label="ค้นหางานบริการหลังการขาย" />
          <div class="table-filter-select control-field"><span>สถานะ</span><select v-model="serviceStatusFilter" aria-label="กรองสถานะงานบริการหลังการขาย"><option v-for="status in serviceStatusOptions" :key="status">{{ status }}</option></select></div>
        </div>
        <div class="table-scroll">
          <table class="data-table operations-table">
            <thead><tr><th>เลขที่ใบงาน</th><th>ลูกค้า / รายละเอียด</th><th>กำหนดเข้าบริการ</th><th>พนักงาน</th><th>สถานะ</th><th>จัดการ</th></tr></thead>
            <tbody>
              <tr v-for="ticket in filteredServiceTickets" :key="ticket.id">
                <td><span class="sku-code">{{ ticket.id }}</span><small class="table-subtext">เปิด {{ ticket.opened }}</small></td>
                <td><strong>{{ ticket.customer }}</strong><small class="table-subtext">{{ ticket.subject }}</small></td>
                <td><strong>{{ formatJobDate(ticket.date) }}</strong><small class="table-subtext">{{ ticket.time }}</small></td>
                <td>{{ ticket.employees?.join(' · ') || ticket.owner }}</td>
                <td><span :class="statusClass(ticket.status)">{{ ticket.status }}</span></td>
                <td><div class="table-actions"><button class="button secondary table-button table-icon-button" title="แก้ไขรายละเอียดใบงาน" aria-label="แก้ไขรายละเอียดใบงาน" @click="openEditModal(ticket, 'service')"><SvgIcon name="edit" size="15" /></button><button class="button status-action table-button" title="อัพเดตสถานะใบงาน" aria-label="อัพเดตสถานะใบงาน" @click="cycleServiceTicket(ticket)"><SvgIcon name="refresh" size="15" /><span>สถานะ</span></button></div></td>
              </tr>
              <tr v-if="!filteredServiceTickets.length"><td colspan="6" class="empty-state">ไม่พบใบงานบริการที่ตรงกับตัวกรอง</td></tr>
            </tbody>
          </table>
        </div>
        <TablePagination :total="filteredServiceTickets.length" label="ใบงานบริการ" />
      </div>
      <div
        v-if="showServiceForm"
        class="modal-backdrop"
        @click.self="showServiceForm = false"
      >
        <form class="modal service-modal" @submit.prevent="createTicket">
          <div class="modal-heading">
            <div>
              <span class="eyebrow">SERVICE TICKET</span>
              <h2>เปิดใบงานบริการ</h2>
            </div>
            <button
              type="button"
              class="icon-button"
              title="ปิด"
              @click="showServiceForm = false"
            >
              <SvgIcon name="close" />
            </button>
          </div>
          <p class="modal-description">บันทึกข้อมูลปัญหาและนัดหมายเพื่อส่งต่องานให้ทีมบริการ</p>
          <label
            >ลูกค้า<div class="assignment-search">
              <SvgIcon name="search" size="16" />
              <input v-model="customerSearch" type="search" aria-label="ค้นหาลูกค้าสำหรับใบงานบริการ" placeholder="ค้นหาชื่อลูกค้า..." />
            </div>
            <select v-model="newTicket.customer" required>
              <option v-for="customer in filteredCustomerOptions" :key="customer" :value="customer">{{ customer }}</option>
            </select></label
          ><label
            >หัวข้อปัญหา<input
              v-model="newTicket.subject"
              placeholder="เช่น อินเวอร์เตอร์มี Error Code"
              required /></label
          ><label
            >ระดับความสำคัญ<select v-model="newTicket.priority">
              <option>ปกติ</option>
              <option>สูง</option>
              <option>เร่งด่วน</option>
            </select></label
          >
          <fieldset class="assignment-fieldset">
            <legend>พนักงานที่ส่งไปบริการ</legend>
            <div class="assignment-search">
              <SvgIcon name="search" size="16" />
              <input
                v-model="employeeSearch"
                type="search"
                aria-label="ค้นหาพนักงานที่จะส่งไปบริการ"
                placeholder="ค้นหาชื่อพนักงาน..."
              />
            </div>
            <p class="field-helper">เลือกได้มากกว่า 1 คน</p>
            <label v-for="employee in filteredEmployeeOptions" :key="employee" class="assignment-option">
              <input v-model="newTicket.employees" type="checkbox" :value="employee" />
              <span>{{ employee }}</span>
            </label>
            <p v-if="!filteredEmployeeOptions.length" class="assignment-empty">ไม่พบพนักงานที่ค้นหา</p>
          </fieldset>
          <div class="button-row end">
            <button
              type="button"
              class="button secondary"
              @click="showServiceForm = false"
            >ยกเลิก</button>
            <button class="button primary" type="submit">
              <SvgIcon name="check" />บันทึกใบงาน
            </button>
          </div>
        </form>
      </div>
    </section>
    <div v-if="showEditModal" class="modal-backdrop" @click.self="showEditModal = false">
      <form class="modal task-edit-modal" @submit.prevent="saveEdit">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">EDIT WORK ITEM</span>
            <h2>แก้ไขรายละเอียดงาน</h2>
          </div>
          <button type="button" class="icon-button" title="ปิด" @click="showEditModal = false">
            <SvgIcon name="close" />
          </button>
        </div>
        <p class="modal-description">แก้ไขข้อมูลสำคัญของงาน และอัพเดตสถานะให้ทีมเห็นความคืบหน้าล่าสุด</p>
        <label>ลูกค้า<input v-model="editForm.customer" required /></label>
        <label v-if="editingType === 'appointment'">สถานที่ปฏิบัติงาน<input v-model="editForm.site" required /></label>
        <label v-else>รายละเอียดปัญหา<input v-model="editForm.subject" required /></label>
        <div class="form-grid two">
          <label>วันที่กำหนด<input v-model="editForm.date" type="date" required /></label>
          <label>ช่วงเวลา<input v-model="editForm.time" placeholder="เช่น 09:00–12:00" required /></label>
        </div>
        <label v-if="editingType === 'service'">ความสำคัญ<select v-model="editForm.priority"><option>ปกติ</option><option>สูง</option><option>เร่งด่วน</option></select></label>
        <label>สถานะงาน<select v-model="editForm.status">
          <option v-if="editingType === 'appointment'">รอยืนยัน</option>
          <option v-if="editingType === 'appointment'">ยืนยันแล้ว</option>
          <option v-if="editingType === 'appointment'">เตรียมอุปกรณ์</option>
          <option v-if="editingType === 'appointment'">กำลังติดตั้ง</option>
          <option v-if="editingType === 'service'">รอเปิดงาน</option>
          <option v-if="editingType === 'service'">รอมอบหมาย</option>
          <option v-if="editingType === 'service'">นัดหมายแล้ว</option>
          <option v-if="editingType === 'service'">กำลังเข้าบริการ</option>
          <option>เสร็จสิ้น</option>
        </select></label>
        <div class="button-row end">
          <button type="button" class="button secondary" @click="showEditModal = false">ยกเลิก</button>
          <button type="submit" class="button primary"><SvgIcon name="check" />บันทึกการแก้ไข</button>
        </div>
      </form>
    </div>
    <div v-if="toast" class="toast"><SvgIcon name="check" />{{ toast }}</div>
  </AppShell>
</template>

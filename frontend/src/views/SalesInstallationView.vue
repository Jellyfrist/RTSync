<script setup>
// ไฟล์นี้จัดการรายการขาย ใบเสนอราคา นัดหมายติดตั้ง และงานบริการหลังการขาย
import { computed, onMounted, ref, watch } from "vue";
import AppShell from "@/components/layout/AppShell.vue";
import AppPageHeader from "@/components/ui/AppPageHeader.vue";
import AppSearchField from "@/components/ui/AppSearchField.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
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
const employeeOptions = ref(
  mockDb
    .get("employees")
    .map((employee) => employee.name)
    .filter(Boolean),
);
const employeeSearch = ref("");
const filteredEmployeeOptions = computed(() => {
  const query = employeeSearch.value.trim().toLocaleLowerCase("th-TH");
  if (!query) return employeeOptions.value;
  return employeeOptions.value.filter((employee) =>
    employee.toLocaleLowerCase("th-TH").includes(query),
  );
});
const customerOptions = ref(
  mockDb
    .get("customers")
    .map((customer) => customer.name)
    .filter(Boolean),
);
const defaultEmployee = employeeOptions.value[0] || "";
const defaultCustomer = customerOptions.value[0] || "";
const defaultAppointmentTime = mockDb.get("appointmentTimes")[0] || "";
const customerSearch = ref("");
const filteredCustomerOptions = computed(() => {
  const query = customerSearch.value.trim().toLocaleLowerCase("th-TH");
  const matches = customerOptions.value.filter((customer) =>
    customer.toLocaleLowerCase("th-TH").includes(query),
  );
  const selectedCustomer =
    quotationForm.value.customer ||
    newAppointment.value.customer ||
    newTicket.value.customer;
  if (selectedCustomer && !matches.includes(selectedCustomer)) {
    return [selectedCustomer, ...matches];
  }
  return matches;
});
const newAppointment = ref({
  customer: defaultCustomer,
  date: "",
  time: defaultAppointmentTime,
  employees: defaultEmployee ? [defaultEmployee] : [],
  type: "ติดตั้งระบบ",
});
const customAppointmentTime = ref("");
// สินค้าแนะนำที่โหลดจาก API งานปฏิบัติการ
const catalog = ref([]);
const bill = ref([]);
const quotationForm = ref({
  customer: defaultCustomer,
  quoteId: "QT-25061",
  issuedAt: new Date().toISOString().slice(0, 10),
  validUntil: "",
  notes: "",
});
const selectedQuoteSku = ref("");
const selectedQuoteQty = ref(1);
const selectedQuoteSearch = ref("");
const quoteServices = ref([]);
const selectedServiceKey = ref("");
const showServiceTypeModal = ref(false);
const newServiceType = ref({ name: "", defaultPrice: 0 });
const serviceOptions = ref(mockDb.get("serviceTypes"));
const selectedServicePrice = computed(
  () =>
    serviceOptions.value.find(
      (service) => service.value === selectedServiceKey.value,
    )?.defaultPrice || 0,
);
const filteredQuoteProducts = computed(() => {
  const query = selectedQuoteSearch.value.trim().toLocaleLowerCase("th-TH");
  if (!query) return catalog.value;
  return catalog.value.filter((product) =>
    `${product.name} ${product.sku} ${product.category || ""}`
      .toLocaleLowerCase("th-TH")
      .includes(query),
  );
});
const salesOrders = ref([]);
const salesSearch = ref("");
const paymentStatusFilter = ref("ทั้งหมด");
const orderStatusFilter = ref("ทั้งหมด");
const paymentStatusOptions = mockDb.get("paymentStatuses");
const orderStatusOptions = mockDb.get("orderStatuses");
const orderStatusFilterOptions = ["ทั้งหมด", ...orderStatusOptions];
const appointmentTimeOptions = mockDb.get("appointmentTimes");
const closedSalesOrders = computed(() =>
  salesOrders.value
    .filter((order) => order.orderStatus === "ปิดการขาย")
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)),
);
const filteredSalesOrders = computed(() => {
  const query = salesSearch.value.trim().toLocaleLowerCase("th-TH");
  return salesOrders.value.filter((order) => {
    if (order.orderStatus === "ปิดการขาย") return false;
    const searchable =
      `${order.id} ${order.customer} ${order.items.map((item) => item.name).join(" ")}`.toLocaleLowerCase(
        "th-TH",
      );
    return (
      (orderStatusFilter.value === "ทั้งหมด" ||
        order.orderStatus === orderStatusFilter.value) &&
      (paymentStatusFilter.value === "ทั้งหมด" ||
        order.paymentStatus === paymentStatusFilter.value) &&
      searchable.includes(query)
    );
  });
});
// นัดหมายและใบงานที่โหลดจาก backend
const appointments = ref([]);
const serviceTickets = ref([]);
const pendingAppointments = computed(
  () => appointments.value.filter((item) => item.status !== "เสร็จสิ้น").length,
);
const openServiceTickets = computed(
  () =>
    serviceTickets.value.filter((item) => item.status !== "เสร็จสิ้น").length,
);
const newTicket = ref({
  customer: defaultCustomer,
  subject: "",
  date: "",
  time: defaultAppointmentTime,
  employees: defaultEmployee ? [defaultEmployee] : [],
});
const customServiceTime = ref("");
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
const appointmentStatusOptions = mockDb.get("appointmentStatuses");
const serviceStatusOptions = mockDb.get("serviceStatuses");
const servicePriorityOptions = mockDb.get("servicePriorities");
const editStatusOptions = computed(() =>
  editingType.value === "service"
    ? serviceStatusOptions.slice(1)
    : appointmentStatusOptions.slice(1),
);
const filteredAppointments = computed(() => {
  const query = appointmentSearch.value.trim().toLocaleLowerCase("th-TH");
  return sortedAppointments.value.filter((item) => {
    if (item.status === "เสร็จสิ้น" || item.closedAt) return false;
    const searchable =
      `${item.id} ${item.customer} ${item.site} ${item.type} ${item.employees?.join(" ") || item.crew || ""}`.toLocaleLowerCase(
        "th-TH",
      );
    return (
      (appointmentStatusFilter.value === "ทั้งหมด" ||
        item.status === appointmentStatusFilter.value) &&
      searchable.includes(query)
    );
  });
});
const closedAppointments = computed(() =>
  sortedAppointments.value
    .filter((item) => item.status === "เสร็จสิ้น" || item.closedAt)
    .sort(
      (a, b) => new Date(b.closedAt || b.date) - new Date(a.closedAt || a.date),
    ),
);
const filteredServiceTickets = computed(() => {
  const query = serviceSearch.value.trim().toLocaleLowerCase("th-TH");
  return sortedServiceTickets.value.filter((item) => {
    if (item.status === "เสร็จสิ้น" || item.closedAt) return false;
    const searchable =
      `${item.id} ${item.customer} ${item.subject} ${item.employees?.join(" ") || item.owner || ""}`.toLocaleLowerCase(
        "th-TH",
      );
    return (
      (serviceStatusFilter.value === "ทั้งหมด" ||
        item.status === serviceStatusFilter.value) &&
      searchable.includes(query)
    );
  });
});
const closedServiceTickets = computed(() =>
  sortedServiceTickets.value
    .filter((item) => item.status === "เสร็จสิ้น" || item.closedAt)
    .sort(
      (a, b) => new Date(b.closedAt || b.date) - new Date(a.closedAt || a.date),
    ),
);
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
const customEditTime = ref("");
onMounted(async () => {
  // โหลดสินค้า นัดหมาย และใบงานพร้อมกันเมื่อเปิดหน้า
  const [catalogRecords, appointmentRecords, ticketRecords, salesRecords] =
    await Promise.all([
      operationsApi.getCatalog(),
      operationsApi.getAppointments(),
      operationsApi.getServiceTickets(),
      operationsApi.getSales(),
    ]);
  catalog.value.splice(0, catalog.value.length, ...catalogRecords);
  appointments.value = appointmentRecords;
  serviceTickets.value = ticketRecords;
  salesOrders.value = salesRecords;
});
const total = computed(() =>
  [...bill.value, ...quoteServices.value].reduce(
    (sum, item) => sum + item.price * item.qty,
    0,
  ),
);
const pricingAlerts = computed(() =>
  bill.value
    .map((item) => ({
      ...item,
      ...pricingDecision(item.price, item),
    }))
    .filter((item) => item.isLoss || item.belowMinimumMargin),
);
const lossMakingItems = computed(() =>
  pricingAlerts.value.filter((item) => item.isLoss),
);
const formatCurrency = (value) => new Intl.NumberFormat("th-TH").format(value);
const getOrderLines = (order) => [
  ...(order.items || []),
  ...(order.services || []),
];
const getOrderLineSummary = (order) => {
  const lines = getOrderLines(order);
  const first = lines[0];
  if (!first) return { name: "ยังไม่มีรายการ", detail: "" };
  return {
    name: first.name,
    detail:
      lines.length > 1
        ? `+${lines.length - 1} รายการ`
        : `${first.qty || 0} ${first.unit || "งาน"}`,
  };
};
const notify = (message) => {
  toast.value = message;
  setTimeout(() => {
    toast.value = "";
  }, 2600);
};
function openAppointmentForm(date = "") {
  employeeSearch.value = "";
  customerSearch.value = "";
  if (date) newAppointment.value.date = date;
  showAppointmentForm.value = true;
}
function openServiceForm(date = "") {
  employeeSearch.value = "";
  customerSearch.value = "";
  if (date) newTicket.value.date = date;
  showServiceForm.value = true;
}
function openQuotationForm() {
  customerSearch.value = "";
  selectedQuoteSearch.value = "";
  showQuotationForm.value = true;
}
function addToBill(product) {
  // เพิ่มสินค้าเข้าใบเสนอราคา
  const item = bill.value.find((row) => row.sku === product.sku);
  if (item) item.qty += 1;
  else
    bill.value.push({
      ...product,
      price: Number(product.salePrice ?? product.price) || 0,
      qty: 1,
    });
  notify(`เพิ่ม ${product.name} ลงใบเสนอราคาแล้ว`);
}
function addSelectedQuoteProduct() {
  const product = catalog.value.find(
    (item) => item.sku === selectedQuoteSku.value,
  );
  if (!product) return;
  const existing = bill.value.find((item) => item.sku === product.sku);
  if (existing)
    existing.qty += Math.max(Number(selectedQuoteQty.value) || 1, 1);
  else
    bill.value.push({
      ...product,
      price: Number(product.salePrice ?? product.price) || 0,
      qty: Math.max(Number(selectedQuoteQty.value) || 1, 1),
    });
  selectedQuoteSku.value = "";
  selectedQuoteQty.value = 1;
}
function removeItem(index) {
  bill.value.splice(index, 1);
}
function addQuoteService() {
  const service = serviceOptions.value.find(
    (item) => item.value === selectedServiceKey.value,
  );
  if (!service) return;
  const existing = quoteServices.value.find(
    (item) => item.serviceKey === service.value,
  );
  if (existing) existing.qty += 1;
  else
    quoteServices.value.push({
      kind: "service",
      serviceKey: service.value,
      sku: `SVC-${service.value.toUpperCase()}`,
      name: service.label,
      qty: 1,
      unit: "งาน",
      price: service.defaultPrice,
    });
  selectedServiceKey.value = "";
}
function removeQuoteService(index) {
  quoteServices.value.splice(index, 1);
}
async function saveSale() {
  if (!bill.value.length) return notify("กรุณาเลือกสินค้าอย่างน้อย 1 รายการ");
  if (lossMakingItems.value.length)
    return notify("ไม่สามารถบันทึกการขายที่ราคาต่ำกว่าต้นทุนได้");
  const sale = {
    id: `SO-${new Date()
      .toISOString()
      .replace(/[-:TZ.]/g, "")
      .slice(0, 12)}`,
    customer: "คุณสมศักดิ์ วัฒนกุล",
    customerCode: "CUST-2025-001",
    items: bill.value.map(
      ({ sku, name, qty, unit, price, costLots, costPrice }) => ({
        sku,
        name,
        qty,
        unit,
        price,
        costAtSale: pricingDecision(price, { costLots, costPrice }).cost,
      }),
    ),
    total: total.value,
    paymentStatus: "รอชำระมัดจำ",
    orderStatus: "รอการยืนยัน",
    createdAt: new Date().toISOString(),
  };
  salesOrders.value.unshift(await operationsApi.create("sales", sale));
  bill.value = [];
  quoteServices.value = [];
  notify("บันทึกรายการขายแล้ว — พร้อมสร้างนัดหมายติดตั้ง");
}
async function saveQuotation() {
  if (!bill.value.length && !quoteServices.value.length)
    return notify("กรุณาเพิ่มสินค้า หรือค่าบริการอย่างน้อย 1 รายการ");
  if (lossMakingItems.value.length)
    return notify("ไม่สามารถออกใบเสนอราคาที่ราคาต่ำกว่าต้นทุนได้");
  const customer = mockDb
    .get("customers")
    .find((item) => item.name === quotationForm.value.customer);
  const customerCode = customer?.code || "";
  const quotation = {
    id: quotationForm.value.quoteId,
    customer: quotationForm.value.customer,
    customerCode,
    issuedAt: quotationForm.value.issuedAt,
    validUntil: quotationForm.value.validUntil,
    notes: quotationForm.value.notes,
    items: bill.value.map(
      ({ sku, name, qty, unit, price, costLots, costPrice }) => ({
        sku,
        name,
        qty,
        unit,
        price,
        costAtQuote: pricingDecision(price, { costLots, costPrice }).cost,
      }),
    ),
    services: quoteServices.value.map(
      ({ serviceKey, name, qty, unit, price }) => ({
        serviceKey,
        name,
        qty,
        unit,
        price,
      }),
    ),
    total: total.value,
    status: "ร่างใบเสนอราคา",
  };
  await operationsApi.create("quotations", quotation);
  const sale = {
    ...quotation,
    paymentStatus: "รอชำระมัดจำ",
    orderStatus: "รอการยืนยัน",
    createdAt: new Date().toISOString(),
  };
  salesOrders.value = [
    sale,
    ...salesOrders.value.filter((item) => item.id !== sale.id),
  ];
  await operationsApi.create("sales", sale);
  bill.value = [];
  quoteServices.value = [];
  showQuotationForm.value = false;
  notify(`บันทึกใบเสนอราคา ${quotation.id} และเพิ่มในรายการขายแล้ว`);
}
function openServiceTypeModal() {
  newServiceType.value = { name: "", defaultPrice: 0 };
  showServiceTypeModal.value = true;
}
function saveServiceType() {
  const name = newServiceType.value.name.trim();
  if (!name) return;
  const value = `custom-${Date.now()}`;
  serviceOptions.value.push({
    value,
    label: name,
    defaultPrice: Number(newServiceType.value.defaultPrice) || 0,
  });
  mockDb.set("serviceTypes", serviceOptions.value);
  selectedServiceKey.value = value;
  showServiceTypeModal.value = false;
  notify(`เพิ่มประเภทค่าบริการ ${name} แล้ว`);
}
async function updateSaleStatus(order) {
  await operationsApi.update("sales", order.id, order);
  notify(`${order.id} เปลี่ยนสถานะคำสั่งซื้อเป็น ${order.orderStatus}`);
}
async function updatePaymentStatus(order) {
  await operationsApi.update("sales", order.id, order);
  notify(`${order.id} เปลี่ยนสถานะการชำระเงินเป็น ${order.paymentStatus}`);
}
async function closeSale(order) {
  order.previousOrderStatus = order.orderStatus;
  order.orderStatus = "ปิดการขาย";
  order.closedAt = new Date().toISOString();
  await operationsApi.update("sales", order.id, order);
  notify(`${order.id} ปิดการขายเรียบร้อยแล้ว`);
}
async function reopenSale(order) {
  order.orderStatus = order.previousOrderStatus || "รอการยืนยัน";
  delete order.previousOrderStatus;
  delete order.closedAt;
  await operationsApi.update("sales", order.id, order);
  notify(`${order.id} ยกเลิกการปิดการขายแล้ว`);
}
async function cancelSale(order) {
  order.orderStatus = "ยกเลิกการขาย";
  await operationsApi.update("sales", order.id, order);
  notify(`${order.id} ยกเลิกการขายแล้ว`);
}
async function updateAppointmentStatus(item) {
  if (item.status === "เสร็จสิ้น")
    item.closedAt = item.closedAt || new Date().toISOString();
  await operationsApi.update("appointments", item.id, item);
  notify(`${item.id} เปลี่ยนสถานะเป็น ${item.status}`);
}
async function closeAppointment(item) {
  item.previousStatus = item.status;
  item.status = "เสร็จสิ้น";
  item.closedAt = new Date().toISOString();
  await operationsApi.update("appointments", item.id, item);
  notify(`${item.id} ปิดงานเรียบร้อย`);
}
async function reopenAppointment(item) {
  item.status = item.previousStatus || "รอยืนยัน";
  delete item.previousStatus;
  delete item.closedAt;
  await operationsApi.update("appointments", item.id, item);
  notify(`${item.id} ยกเลิกการปิดงานแล้ว`);
}
async function updateServiceStatus(ticket) {
  if (ticket.status === "เสร็จสิ้น")
    ticket.closedAt = ticket.closedAt || new Date().toISOString();
  await operationsApi.update("serviceTickets", ticket.id, ticket);
  notify(`${ticket.id} เปลี่ยนสถานะเป็น ${ticket.status}`);
}
async function closeServiceTicket(ticket) {
  ticket.previousStatus = ticket.status;
  ticket.status = "เสร็จสิ้น";
  ticket.closedAt = new Date().toISOString();
  await operationsApi.update("serviceTickets", ticket.id, ticket);
  notify(`${ticket.id} ปิดงานเรียบร้อย`);
}
async function reopenServiceTicket(ticket) {
  ticket.status = ticket.previousStatus || "รอเปิดงาน";
  delete ticket.previousStatus;
  delete ticket.closedAt;
  await operationsApi.update("serviceTickets", ticket.id, ticket);
  notify(`${ticket.id} ยกเลิกการปิดงานแล้ว`);
}
function statusClass(status) {
  if (["เสร็จสิ้น", "ยืนยันแล้ว"].includes(status)) return "success-tag";
  if (["รอยืนยัน", "รอมอบหมาย", "รอเปิดงาน"].includes(status))
    return "warning-tag";
  return "code-tag";
}
function paymentStatusClass(status) {
  if (status === "ชำระเรียบร้อย") return "success-tag";
  if (["ชำระมัดจำ", "รอชำระมัดจำ", "รอชำระส่วนที่เหลือ"].includes(status))
    return "warning-tag";
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
  const isPresetTime = appointmentTimeOptions.includes(item.time);
  customEditTime.value = isPresetTime ? "" : item.time || "";
  editForm.value = {
    customer: item.customer || "",
    subject: item.subject || "",
    date: item.date || "",
    time: isPresetTime ? item.time : "กำหนดเอง",
    site: item.site || "",
    priority: item.priority || "ปกติ",
    status: item.status || "",
  };
  showEditModal.value = true;
}
async function saveEdit() {
  if (!editingJob.value) return;
  if (editForm.value.time === "กำหนดเอง" && !customEditTime.value.trim())
    return notify("กรุณาระบุช่วงเวลา");
  if (editForm.value.time === "กำหนดเอง")
    editForm.value.time = customEditTime.value.trim();
  Object.assign(editingJob.value, editForm.value);
  if (editingType.value === "service")
    await operationsApi.update("serviceTickets", editingJob.value.id, editingJob.value);
  if (editingType.value === "appointment")
    await operationsApi.update("appointments", editingJob.value.id, editingJob.value);
  showEditModal.value = false;
  notify(`บันทึกรายละเอียด ${editingJob.value.id} แล้ว`);
}
async function createTicket() {
  if (!newTicket.value.subject.trim()) return notify("กรุณาระบุหัวข้อปัญหา");
  if (!newTicket.value.date) return notify("กรุณาเลือกวันที่เข้าบริการ");
  if (newTicket.value.time === "กำหนดเอง" && !customServiceTime.value.trim())
    return notify("กรุณาระบุช่วงเวลาเข้าบริการ");
  if (!newTicket.value.employees.length)
    return notify("กรุณาเลือกพนักงานอย่างน้อย 1 คน");
  const ticket = {
    id: `SRV-250${43 + serviceTickets.value.length}`,
    customer: newTicket.value.customer,
    subject: newTicket.value.subject,
    opened: "วันนี้",
    date: newTicket.value.date,
    time:
      newTicket.value.time === "กำหนดเอง"
        ? customServiceTime.value.trim()
        : newTicket.value.time,
    priority: "ปกติ",
    status: "รับเรื่องใหม่",
    owner: "รอมอบหมาย",
    employees: [...newTicket.value.employees],
  };
  serviceTickets.value.unshift(await operationsApi.create("serviceTickets", ticket));
  newTicket.value.subject = "";
  newTicket.value.date = "";
  newTicket.value.time = "09:00–12:00";
  customServiceTime.value = "";
  newTicket.value.employees = ["ณัฐพล แสนสุข"];
  showServiceForm.value = false;
  notify("เปิดใบงานบริการหลังการขายแล้ว");
}
function closeTicket(ticket) {
  ticket.status = "เสร็จสิ้น";
  notify(`${ticket.id} ปิดงานเรียบร้อย`);
}
async function createAppointment() {
  if (!newAppointment.value.date) return notify("กรุณาเลือกวันที่นัดหมาย");
  if (!newAppointment.value.employees.length)
    return notify("กรุณาเลือกพนักงานอย่างน้อย 1 คน");
  const appointment = {
    id: `INS-25062${appointments.value.length}`,
    customer: newAppointment.value.customer,
    site: "รอระบุสถานที่",
    date: newAppointment.value.date,
    time:
      newAppointment.value.time === "กำหนดเอง"
        ? customAppointmentTime.value
        : newAppointment.value.time,
    crew: newAppointment.value.employees.join(" · "),
    employees: [...newAppointment.value.employees],
    status: "รอยืนยัน",
    type: newAppointment.value.type,
  };
  appointments.value.push(await operationsApi.create("appointments", appointment));
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
        <div class="button-row page-actions"></div>
      </template>
    </AppPageHeader>
    <OperationsCalendar
      v-if="activeTab === 'appointments'"
      :items="appointments"
      mode="installation"
      class="top-operations-calendar"
      ><template #detail-actions="{ date }"
        ><button
          class="button primary full"
          type="button"
          @click="openAppointmentForm(date)"
        >
          <SvgIcon name="plus" />สร้างนัดหมาย
        </button></template
      ></OperationsCalendar
    >
    <OperationsCalendar
      v-else-if="activeTab === 'service'"
      :items="serviceTickets"
      mode="service"
      class="top-operations-calendar"
      ><template #detail-actions="{ date }"
        ><button
          class="button primary full"
          type="button"
          @click="openServiceForm(date)"
        >
          <SvgIcon name="plus" />เพิ่มงานบริการ
        </button></template
      ></OperationsCalendar
    >
    <div v-if="!props.initialTab" class="section-divider">
      <span class="section-kicker">02</span>
      <div>
        <strong>พื้นที่ปฏิบัติงาน</strong
        ><small>จัดการงานตามโมดูลที่เลือกจากเมนูด้านข้าง</small>
      </div>
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
    <section
      v-if="activeTab === 'sales'"
      class="operations-table-section sales-orders-section"
    >
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">รายการขาย</h2>
          <p class="section-caption">
            รายการขายที่เกิดขึ้นจริง ติดตามสินค้า ยอดขาย และสถานะการชำระเงิน
          </p>
        </div>
        <button class="button primary" type="button" @click="openQuotationForm">
          <SvgIcon name="plus" />ออกใบเสนอราคา
        </button>
      </div>
      <div class="task-overview-grid">
        <div>
          <span>รายการขายทั้งหมด</span
          ><strong>{{ filteredSalesOrders.length }}</strong
          ><small>รายการในมุมมองนี้</small>
        </div>
        <div>
          <span>รอการชำระเงิน</span
          ><strong>{{
            filteredSalesOrders.filter(
              (order) => order.paymentStatus !== "ชำระเรียบร้อย",
            ).length
          }}</strong
          ><small>ต้องติดตามต่อ</small>
        </div>
        <div>
          <span>ยอดขายรวม</span
          ><strong
            >฿{{
              formatCurrency(
                filteredSalesOrders.reduce(
                  (sum, order) => sum + order.total,
                  0,
                ),
              )
            }}</strong
          ><small>จากรายการที่แสดง</small>
        </div>
      </div>
      <div
        class="task-table-tools table-filters-below-overview sales-table-filters"
      >
        <AppSearchField
          v-model="salesSearch"
          class-name="table-filter-search"
          placeholder="ค้นหาเลขที่ขาย ชื่อลูกค้า หรือสินค้า..."
          label="ค้นหารายการขาย"
        />
        <div class="table-filter-select control-field app-select-filter">
          <span>สถานะคำสั่งซื้อ</span>
          <AppSelect
            v-model="orderStatusFilter"
            :options="orderStatusFilterOptions"
            search-placeholder="ค้นหาสถานะคำสั่งซื้อ"
            aria-label="กรองสถานะคำสั่งซื้อ"
          />
        </div>
        <div class="table-filter-select control-field app-select-filter">
          <span>สถานะการชำระเงิน</span>
          <AppSelect
            v-model="paymentStatusFilter"
            :options="paymentStatusOptions"
            search-placeholder="ค้นหาสถานะการชำระเงิน"
            aria-label="กรองสถานะการชำระเงิน"
          />
        </div>
      </div>
      <div class="table-scroll">
        <table class="data-table operations-table sales-orders-table">
          <thead>
            <tr>
              <th>เลขที่ขาย</th>
              <th>ลูกค้า</th>
              <th>รายการสินค้า</th>
              <th>ยอดขาย</th>
              <th>สถานะคำสั่งซื้อ</th>
              <th>สถานะการชำระเงิน</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in filteredSalesOrders" :key="order.id">
              <td>
                <span class="sku-code">{{ order.id }}</span
                ><small class="table-subtext">{{
                  new Date(order.createdAt).toLocaleDateString("th-TH")
                }}</small>
              </td>
              <td>
                <strong>{{ order.customer }}</strong
                ><small class="table-subtext">{{ order.customerCode }}</small>
              </td>
              <td>
                <strong>{{ getOrderLineSummary(order).name }}</strong
                ><small class="table-subtext">{{
                  getOrderLineSummary(order).detail
                }}</small>
              </td>
              <td class="mono">฿{{ formatCurrency(order.total) }}</td>
              <td>
                <select
                  class="table-status-select"
                  :class="statusClass(order.orderStatus)"
                  v-model="order.orderStatus"
                  aria-label="เลือกสถานะคำสั่งซื้อ"
                  @change="updateSaleStatus(order)"
                >
                  <option v-for="status in orderStatusOptions" :key="status">
                    {{ status }}
                  </option>
                </select>
              </td>
              <td>
                <select
                  class="table-status-select"
                  :class="paymentStatusClass(order.paymentStatus)"
                  v-model="order.paymentStatus"
                  aria-label="เลือกสถานะการชำระเงิน"
                  @change="updatePaymentStatus(order)"
                >
                  <option
                    v-for="status in paymentStatusOptions.slice(1)"
                    :key="status"
                  >
                    {{ status }}
                  </option>
                </select>
              </td>
              <td>
                <button
                  v-if="order.orderStatus !== 'ปฏิเสธการสั่งซื้อ'"
                  class="button secondary table-button sales-status-button"
                  type="button"
                  @click="closeSale(order)"
                >
                  <SvgIcon name="check" size="14" />ปิดการขาย</button
                ><button
                  v-else
                  class="button secondary table-button sales-status-button"
                  type="button"
                  @click="cancelSale(order)"
                >
                  <SvgIcon name="close" size="14" />ยกเลิกการขาย
                </button>
              </td>
            </tr>
            <tr v-if="!filteredSalesOrders.length">
              <td colspan="7" class="empty-state">
                ยังไม่มีรายการขายที่ตรงกับตัวกรอง
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <TablePagination :total="filteredSalesOrders.length" label="รายการขาย" />
    </section>
    <section
      v-if="activeTab === 'sales'"
      class="operations-table-section sales-closed-section"
    >
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">รายการขายที่ปิดแล้ว</h2>
          <p class="section-caption">
            ประวัติการขายที่ดำเนินการเสร็จสิ้นแล้ว สำหรับตรวจสอบย้อนหลัง
          </p>
        </div>
      </div>
      <div class="table-scroll">
        <table class="data-table operations-table sales-orders-table">
          <thead>
            <tr>
              <th>เลขที่ขาย</th>
              <th>ลูกค้า</th>
              <th>รายการสินค้า</th>
              <th>ยอดขาย</th>
              <th>สถานะคำสั่งซื้อ</th>
              <th>สถานะการชำระเงิน</th>
              <th>ปิดการขายเมื่อ</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in closedSalesOrders" :key="order.id">
              <td>
                <span class="sku-code">{{ order.id }}</span
                ><small class="table-subtext">{{
                  new Date(order.createdAt).toLocaleDateString("th-TH")
                }}</small>
              </td>
              <td>
                <strong>{{ order.customer }}</strong
                ><small class="table-subtext">{{ order.customerCode }}</small>
              </td>
              <td>
                <strong>{{ getOrderLineSummary(order).name }}</strong
                ><small class="table-subtext">{{
                  getOrderLineSummary(order).detail
                }}</small>
              </td>
              <td class="mono">฿{{ formatCurrency(order.total) }}</td>
              <td><span class="success-tag">ปิดการขาย</span></td>
              <td>
                <span :class="paymentStatusClass(order.paymentStatus)">{{
                  order.paymentStatus
                }}</span>
              </td>
              <td>
                {{
                  new Date(
                    order.closedAt || order.createdAt,
                  ).toLocaleDateString("th-TH")
                }}
              </td>
              <td>
                <button
                  class="button secondary table-button sales-status-button"
                  type="button"
                  title="ยกเลิกการปิดการขาย"
                  @click="reopenSale(order)"
                >
                  <SvgIcon name="refresh" size="14" />ยกเลิกการปิดการขาย
                </button>
              </td>
            </tr>
            <tr v-if="!closedSalesOrders.length">
              <td colspan="8" class="empty-state">
                ยังไม่มีรายการขายที่ปิดแล้ว
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <TablePagination
        :total="closedSalesOrders.length"
        label="รายการขายที่ปิดแล้ว"
      />
    </section>
    <div
      v-if="activeTab === 'sales' && showQuotationForm"
      class="modal-backdrop"
      @click.self="showQuotationForm = false"
    >
      <form class="modal quotation-modal" @submit.prevent="saveQuotation">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">QUOTATION FORM</span>
            <h2>ออกใบเสนอราคา</h2>
            <p class="modal-caption">
              เลือกสินค้าและจัดทำใบเสนอราคาก่อนเปลี่ยนเป็นรายการขาย
            </p>
          </div>
          <button
            type="button"
            class="icon-button"
            title="ปิด"
            aria-label="ปิดฟอร์มออกใบเสนอราคา"
            @click="showQuotationForm = false"
          >
            <SvgIcon name="close" />
          </button>
        </div>
        <div class="quotation-form">
          <div class="form-grid">
            <label
              >ลูกค้า<AppSelect
                v-model="quotationForm.customer"
                :options="customerOptions"
                placeholder="เลือกลูกค้า"
                search-placeholder="ค้นหาชื่อลูกค้า..."
                aria-label="เลือกลูกค้าสำหรับใบเสนอราคา"
                required
            /></label>
            <label
              >เลขที่ใบเสนอราคา<input v-model="quotationForm.quoteId" required
            /></label>
            <label
              >วันที่ออกใบเสนอราคา<input
                v-model="quotationForm.issuedAt"
                type="date"
                required
            /></label>
            <label
              >วันหมดอายุ<input v-model="quotationForm.validUntil" type="date"
            /></label>
          </div>
          <label
            >หมายเหตุเพิ่มเติม<textarea
              v-model="quotationForm.notes"
              rows="3"
              placeholder="รายละเอียดเงื่อนไขการเสนอราคา หรือหมายเหตุถึงลูกค้า"
            ></textarea>
          </label>
          <div class="quotation-items-section">
            <div class="quotation-items-heading">
              <div>
                <h3>รายการสินค้าในใบเสนอราคา</h3>
                <p>เลือกสินค้าและระบุจำนวนที่ต้องการเสนอให้ลูกค้า</p>
              </div>
            </div>
            <div class="quotation-item-picker">
              <label
                >สินค้า<AppSelect
                  v-model="selectedQuoteSku"
                  :options="
                    filteredQuoteProducts.map((product) => ({
                      value: product.sku,
                      label: `${product.name} · ${product.sku} · ฿${formatCurrency(product.price)}`,
                    }))
                  "
                  placeholder="เลือกสินค้าจากคลัง"
                  search-placeholder="ค้นหาชื่อสินค้า หรือ SKU..."
                  aria-label="เลือกสินค้าสำหรับใบเสนอราคา"
              /></label>
              <label
                >จำนวน<input
                  v-model.number="selectedQuoteQty"
                  type="number"
                  min="1"
              /></label>
              <button
                type="button"
                class="button secondary"
                :disabled="!selectedQuoteSku"
                @click="addSelectedQuoteProduct"
              >
                <SvgIcon name="plus" />เพิ่มรายการ
              </button>
            </div>
            <div class="table-scroll">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>รายการ</th>
                    <th>จำนวน</th>
                    <th>ราคาที่เสนอ / หน่วย</th>
                    <th>รวม</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in bill" :key="item.sku">
                    <td>
                      <strong>{{ item.name }}</strong
                      ><small class="table-subtext">{{ item.sku }}</small>
                    </td>
                    <td>{{ item.qty }} {{ item.unit }}</td>
                    <td>
                      <input
                        v-model.number="item.price"
                        class="quotation-price-input"
                        type="number"
                        min="0"
                        step="1"
                        :aria-label="`ราคาที่เสนอสำหรับ ${item.name}`"
                      /><small class="table-subtext pricing-meta"
                        >ต้นทุน ฿{{
                          formatCurrency(pricingDecision(item.price, item).cost)
                        }}
                        · กำไร
                        {{
                          Math.round(
                            pricingDecision(item.price, item).marginRate * 100,
                          )
                        }}%</small
                      >
                    </td>
                    <td>฿{{ formatCurrency(item.price * item.qty) }}</td>
                    <td>
                      <button
                        type="button"
                        class="icon-button"
                        title="ลบรายการ"
                        @click="removeItem(index)"
                      >
                        <SvgIcon name="close" />
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!bill.length">
                    <td colspan="5" class="empty-state">
                      ยังไม่มีรายการสินค้า กรุณาเลือกสินค้าด้านบน
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <TablePagination :total="bill.length" label="รายการในใบเสนอราคา" />
          </div>
          <div class="quotation-items-section quotation-services-section">
            <div class="quotation-items-heading">
              <div>
                <h3>ค่าบริการ</h3>
                <p>
                  เพิ่มค่าติดตั้ง ค่าบริการหลังการขาย หรือค่าใช้จ่ายประกอบการขาย
                </p>
              </div>
            </div>
            <div class="quotation-item-picker">
              <label
                >ประเภทค่าบริการ<AppSelect
                  v-model="selectedServiceKey"
                  :options="serviceOptions"
                  placeholder="เลือกค่าบริการ"
                  aria-label="เลือกประเภทค่าบริการ"
                >
                  <template #menu-footer>
                    <button
                      type="button"
                      class="app-select-add-action"
                      @click.stop="openServiceTypeModal"
                    >
                      <SvgIcon name="plus" size="15" />เพิ่มประเภทค่าบริการ
                    </button>
                  </template>
                </AppSelect></label
              >
              <label
                >ราคา / หน่วย<input
                  :value="selectedServicePrice"
                  type="number"
                  readonly
                  aria-label="ราคาตั้งต้นของค่าบริการ"
              /></label>
              <button
                type="button"
                class="button secondary"
                :disabled="!selectedServiceKey"
                @click="addQuoteService"
              >
                <SvgIcon name="plus" />เพิ่มค่าบริการ
              </button>
            </div>
            <div class="table-scroll">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>รายการ</th>
                    <th>จำนวน</th>
                    <th>ราคา / หน่วย</th>
                    <th>รวม</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(service, index) in quoteServices"
                    :key="service.serviceKey"
                  >
                    <td>
                      <strong>{{ service.name }}</strong
                      ><small class="table-subtext">ค่าบริการ</small>
                    </td>
                    <td>{{ service.qty }} {{ service.unit }}</td>
                    <td>
                      <input
                        v-model.number="service.price"
                        class="quotation-price-input"
                        type="number"
                        min="0"
                        step="1"
                        :aria-label="`ราคาค่าบริการ ${service.name}`"
                      />
                    </td>
                    <td>฿{{ formatCurrency(service.price * service.qty) }}</td>
                    <td>
                      <button
                        type="button"
                        class="icon-button"
                        title="ลบค่าบริการ"
                        @click="removeQuoteService(index)"
                      >
                        <SvgIcon name="close" />
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!quoteServices.length">
                    <td colspan="5" class="empty-state">
                      ยังไม่มีค่าบริการ เพิ่มได้จากรายการด้านบน
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <TablePagination
              :total="quoteServices.length"
              label="รายการค่าบริการ"
            />
          </div>
          <div
            v-if="pricingAlerts.length"
            class="form-helper pricing-warning"
            role="alert"
          >
            <strong>ตรวจสอบกำไร</strong>
            <span v-for="item in pricingAlerts" :key="item.sku"
              >{{ item.name }}: ต้นทุนเฉลี่ย ฿{{ formatCurrency(item.cost) }} ·
              แนะนำราคาขายอย่างน้อย ฿{{
                formatCurrency(item.recommendedPrice)
              }}</span
            >
          </div>
          <div class="order-total">
            <span>ยอดรวมทั้งสิ้น</span
            ><strong>฿{{ formatCurrency(total) }}</strong>
          </div>
          <div class="button-row end">
            <button
              type="button"
              class="button secondary"
              @click="
                bill = [];
                quoteServices = [];
              "
            >
              ล้างฟอร์ม</button
            ><button class="button primary" type="submit">
              <SvgIcon name="check" />บันทึกใบเสนอราคา
            </button>
          </div>
        </div>
      </form>
    </div>
    <div
      v-if="activeTab === 'appointments' && showAppointmentForm"
      class="modal-backdrop"
      @click.self="showAppointmentForm = false"
    >
      <form
        class="modal product-form-modal"
        @submit.prevent="createAppointment"
      >
        <div class="modal-heading">
          <div>
            <span class="eyebrow">INSTALLATION APPOINTMENT</span>
            <h2>สร้างนัดหมายติดตั้ง</h2>
          </div>
          <button
            type="button"
            class="icon-button"
            title="ปิด"
            @click="showAppointmentForm = false"
          >
            <SvgIcon name="close" />
          </button>
        </div>
        <p class="modal-description">
          กำหนดลูกค้า วันเวลา และทีมช่างสำหรับงานติดตั้งครั้งนี้
        </p>
        <label
          >ลูกค้า
          <AppSelect
            v-model="newAppointment.customer"
            :options="customerOptions"
            placeholder="เลือกลูกค้า"
            search-placeholder="ค้นหาชื่อลูกค้า..."
            aria-label="เลือกลูกค้าสำหรับนัดหมายติดตั้ง"
            required /></label
        ><label
          >วันที่นัดหมาย<input
            v-model="newAppointment.date"
            type="date"
            required /></label
        ><label
          >ช่วงเวลา<AppSelect
            v-model="newAppointment.time"
            :options="appointmentTimeOptions"
            placeholder="เลือกช่วงเวลา"
            aria-label="เลือกช่วงเวลานัดหมาย" /></label
        ><label v-if="newAppointment.time === 'กำหนดเอง'"
          >กรอกช่วงเวลาเอง<input
            v-model="customAppointmentTime"
            placeholder="เช่น 09:00–12:00"
            required
        /></label>
        <fieldset class="assignment-fieldset">
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
          <div class="assignment-summary">
            <span>เลือกผู้ปฏิบัติงานได้มากกว่า 1 คน</span
            ><strong>{{ newAppointment.employees.length }} คน</strong>
          </div>
          <div
            v-if="newAppointment.employees.length"
            class="assignment-selected-list"
            aria-label="พนักงานที่เลือก"
          >
            <span
              v-for="employee in newAppointment.employees"
              :key="`selected-install-${employee}`"
              >{{ employee }}</span
            >
          </div>
          <label
            v-for="employee in filteredEmployeeOptions"
            :key="employee"
            class="assignment-option"
          >
            <input
              v-model="newAppointment.employees"
              type="checkbox"
              :value="employee"
            />
            <span>{{ employee }}</span>
          </label>
          <p v-if="!filteredEmployeeOptions.length" class="assignment-empty">
            ไม่พบพนักงานที่ค้นหา
          </p>
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
    <section
      v-if="activeTab === 'appointments'"
      class="operations-table-section"
    >
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">งานติดตั้งทั้งหมด</h2>
          <p class="section-caption">
            เรียงจากกำหนดงานที่ใกล้ที่สุด เพื่อให้ทีมวางแผนหน้างานได้ทันเวลา
          </p>
        </div>
        <button
          class="button primary"
          type="button"
          @click="openAppointmentForm"
        >
          <SvgIcon name="plus" />สร้างนัดหมาย
        </button>
      </div>
      <div class="task-overview-grid">
        <div>
          <span>งานทั้งหมด</span
          ><strong>{{ filteredAppointments.length }}</strong
          ><small>งานในมุมมองนี้</small>
        </div>
        <div>
          <span>งานวันนี้</span
          ><strong>{{
            sortedAppointments.filter(
              (item) => item.date === new Date().toISOString().slice(0, 10),
            ).length
          }}</strong
          ><small>ต้องเตรียมความพร้อม</small>
        </div>
        <div>
          <span>ใกล้ถึงกำหนด</span
          ><strong>{{
            sortedAppointments[0]
              ? formatJobDate(sortedAppointments[0].date)
              : "—"
          }}</strong
          ><small>รายการแรกในคิว</small>
        </div>
      </div>
      <div class="task-table-tools table-filters-below-overview">
        <AppSearchField
          v-model="appointmentSearch"
          class-name="table-filter-search"
          placeholder="ค้นหาเลขที่งาน ลูกค้า หรือพนักงาน..."
          label="ค้นหางานติดตั้ง"
        />
        <div class="table-filter-select control-field app-select-filter">
          <span>สถานะ</span>
          <AppSelect
            v-model="appointmentStatusFilter"
            :options="appointmentStatusOptions"
            search-placeholder="ค้นหาสถานะงานติดตั้ง"
            aria-label="กรองสถานะงานติดตั้ง"
          />
        </div>
      </div>
      <div class="table-scroll">
        <table class="data-table operations-table">
          <thead>
            <tr>
              <th>เลขที่งาน</th>
              <th>ลูกค้า / สถานที่</th>
              <th>กำหนดงาน</th>
              <th>พนักงาน</th>
              <th>สถานะ</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredAppointments" :key="item.id">
              <td>
                <span class="sku-code">{{ item.id }}</span
                ><small class="table-subtext">{{ item.type }}</small>
              </td>
              <td>
                <strong>{{ item.customer }}</strong
                ><small class="table-subtext">{{ item.site }}</small>
              </td>
              <td>
                <strong>{{ formatJobDate(item.date) }}</strong
                ><small class="table-subtext">{{ item.time }}</small>
              </td>
              <td>{{ item.employees?.join(" · ") || item.crew }}</td>
              <td>
                <select
                  class="table-status-select"
                  :class="statusClass(item.status)"
                  v-model="item.status"
                  aria-label="เลือกสถานะงานติดตั้ง"
                  @change="updateAppointmentStatus(item)"
                >
                  <option
                    v-for="status in appointmentStatusOptions.slice(1, -1)"
                    :key="status"
                  >
                    {{ status }}
                  </option>
                  <option>เสร็จสิ้น</option>
                </select>
              </td>
              <td>
                <button
                  class="button secondary table-button table-icon-button"
                  title="แก้ไขรายละเอียดงาน"
                  aria-label="แก้ไขรายละเอียดงาน"
                  @click="openEditModal(item, 'appointment')"
                >
                  <SvgIcon name="edit" size="15" />
                </button>
              </td>
            </tr>
            <tr v-if="!filteredAppointments.length">
              <td colspan="6" class="empty-state">
                ไม่พบงานติดตั้งที่ตรงกับตัวกรอง
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <TablePagination
        :total="filteredAppointments.length"
        label="งานติดตั้ง"
      />
    </section>
    <section v-if="activeTab === 'service'" class="operations-service">
      <div class="operations-table-section">
        <div class="task-table-heading">
          <div>
            <h2 class="section-heading">งานบริการหลังการขายทั้งหมด</h2>
            <p class="section-caption">
              เรียงจากกำหนดเข้าบริการที่ใกล้ที่สุด เพื่อไม่ให้พลาดงานสำคัญ
            </p>
          </div>
          <button class="button primary" type="button" @click="openServiceForm">
            <SvgIcon name="plus" />เพิ่มงานบริการ
          </button>
        </div>
        <div class="task-overview-grid">
          <div>
            <span>งานทั้งหมด</span
            ><strong>{{ filteredServiceTickets.length }}</strong
            ><small>งานในมุมมองนี้</small>
          </div>
          <div>
            <span>งานเร่งด่วน</span
            ><strong>{{
              sortedServiceTickets.filter(
                (item) =>
                  item.priority === "สูง" || item.priority === "เร่งด่วน",
              ).length
            }}</strong
            ><small>ต้องติดตามเป็นพิเศษ</small>
          </div>
          <div>
            <span>ใกล้ถึงกำหนด</span
            ><strong>{{
              sortedServiceTickets[0]
                ? formatJobDate(sortedServiceTickets[0].date)
                : "—"
            }}</strong
            ><small>รายการแรกในคิว</small>
          </div>
        </div>
        <div class="task-table-tools table-filters-below-overview">
          <AppSearchField
            v-model="serviceSearch"
            class-name="table-filter-search"
            placeholder="ค้นหาเลขที่งาน ลูกค้า หรือพนักงาน..."
            label="ค้นหางานบริการหลังการขาย"
          />
          <div class="table-filter-select control-field app-select-filter">
            <span>สถานะ</span>
            <AppSelect
              v-model="serviceStatusFilter"
              :options="serviceStatusOptions"
              search-placeholder="ค้นหาสถานะงานบริการ"
              aria-label="กรองสถานะงานบริการหลังการขาย"
            />
          </div>
        </div>
        <div class="table-scroll">
          <table class="data-table operations-table">
            <thead>
              <tr>
                <th>เลขที่ใบงาน</th>
                <th>ลูกค้า / รายละเอียด</th>
                <th>กำหนดเข้าบริการ</th>
                <th>พนักงาน</th>
                <th>สถานะ</th>
                <th>จัดการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ticket in filteredServiceTickets" :key="ticket.id">
                <td>
                  <span class="sku-code">{{ ticket.id }}</span
                  ><small class="table-subtext">เปิด {{ ticket.opened }}</small>
                </td>
                <td>
                  <strong>{{ ticket.customer }}</strong
                  ><small class="table-subtext">{{ ticket.subject }}</small>
                </td>
                <td>
                  <strong>{{ formatJobDate(ticket.date) }}</strong
                  ><small class="table-subtext">{{ ticket.time }}</small>
                </td>
                <td>{{ ticket.employees?.join(" · ") || ticket.owner }}</td>
                <td>
                  <select
                    class="table-status-select"
                    :class="statusClass(ticket.status)"
                    v-model="ticket.status"
                    aria-label="เลือกสถานะงานบริการหลังการขาย"
                    @change="updateServiceStatus(ticket)"
                  >
                    <option
                      v-for="status in serviceStatusOptions.slice(1, -1)"
                      :key="status"
                    >
                      {{ status }}
                    </option>
                    <option>เสร็จสิ้น</option>
                  </select>
                </td>
                <td>
                  <button
                    class="button secondary table-button table-icon-button"
                    title="แก้ไขรายละเอียดใบงาน"
                    aria-label="แก้ไขรายละเอียดใบงาน"
                    @click="openEditModal(ticket, 'service')"
                  >
                    <SvgIcon name="edit" size="15" />
                  </button>
                </td>
              </tr>
              <tr v-if="!filteredServiceTickets.length">
                <td colspan="6" class="empty-state">
                  ไม่พบใบงานบริการที่ตรงกับตัวกรอง
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <TablePagination
          :total="filteredServiceTickets.length"
          label="ใบงานบริการ"
        />
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
          <p class="modal-description">
            บันทึกข้อมูลปัญหาและนัดหมายเพื่อส่งต่องานให้ทีมบริการ
          </p>
          <label
            >ลูกค้า
            <AppSelect
              v-model="newTicket.customer"
              :options="customerOptions"
              placeholder="เลือกลูกค้า"
              search-placeholder="ค้นหาชื่อลูกค้า..."
              aria-label="เลือกลูกค้าสำหรับใบงานบริการ"
              required /></label
          ><label
            >หัวข้อปัญหา<input
              v-model="newTicket.subject"
              placeholder="เช่น อินเวอร์เตอร์มี Error Code"
              required /></label
          ><label
            >วันที่เข้าบริการ<input
              v-model="newTicket.date"
              type="date"
              required /></label
          ><label
            >ช่วงเวลาเข้าบริการ<AppSelect
              v-model="newTicket.time"
              :options="appointmentTimeOptions"
              placeholder="เลือกช่วงเวลา"
              aria-label="เลือกช่วงเวลาเข้าบริการ" /></label
          ><label v-if="newTicket.time === 'กำหนดเอง'"
            >กรอกช่วงเวลาเอง<input
              v-model="customServiceTime"
              placeholder="เช่น 09:00–12:00"
              required
          /></label>
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
            <div class="assignment-summary">
              <span>เลือกผู้ปฏิบัติงานได้มากกว่า 1 คน</span
              ><strong>{{ newTicket.employees.length }} คน</strong>
            </div>
            <div
              v-if="newTicket.employees.length"
              class="assignment-selected-list"
              aria-label="พนักงานที่เลือก"
            >
              <span
                v-for="employee in newTicket.employees"
                :key="`selected-service-${employee}`"
                >{{ employee }}</span
              >
            </div>
            <label
              v-for="employee in filteredEmployeeOptions"
              :key="employee"
              class="assignment-option"
            >
              <input
                v-model="newTicket.employees"
                type="checkbox"
                :value="employee"
              />
              <span>{{ employee }}</span>
            </label>
            <p v-if="!filteredEmployeeOptions.length" class="assignment-empty">
              ไม่พบพนักงานที่ค้นหา
            </p>
          </fieldset>
          <div class="button-row end">
            <button
              type="button"
              class="button secondary"
              @click="showServiceForm = false"
            >
              ยกเลิก
            </button>
            <button class="button primary" type="submit">
              <SvgIcon name="check" />บันทึกใบงาน
            </button>
          </div>
        </form>
      </div>
    </section>
    <div
      v-if="showServiceTypeModal"
      class="modal-backdrop"
      @click.self="showServiceTypeModal = false"
    >
      <form class="modal service-type-modal" @submit.prevent="saveServiceType">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">SERVICE TYPE</span>
            <h2>เพิ่มประเภทค่าบริการ</h2>
          </div>
          <button
            type="button"
            class="icon-button"
            title="ปิด"
            @click="showServiceTypeModal = false"
          >
            <SvgIcon name="close" />
          </button>
        </div>
        <p class="modal-description">
          เพิ่มประเภทใหม่สำหรับใช้ในใบเสนอราคา พร้อมกำหนดราคาตั้งต้นได้
        </p>
        <label
          >ชื่อประเภทค่าบริการ<input
            v-model="newServiceType.name"
            required
            placeholder="เช่น ค่าตรวจหน้างาน"
        /></label>
        <label
          >ราคาตั้งต้น / หน่วย<input
            v-model.number="newServiceType.defaultPrice"
            type="number"
            min="0"
            step="1"
            placeholder="0"
        /></label>
        <div class="button-row end">
          <button
            type="button"
            class="button secondary"
            @click="showServiceTypeModal = false"
          >
            ยกเลิก
          </button>
          <button type="submit" class="button primary">
            <SvgIcon name="check" />เพิ่มประเภทค่าบริการ
          </button>
        </div>
      </form>
    </div>
    <div
      v-if="showEditModal"
      class="modal-backdrop"
      @click.self="showEditModal = false"
    >
      <form class="modal task-edit-modal" @submit.prevent="saveEdit">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">EDIT WORK ITEM</span>
            <h2>แก้ไขรายละเอียดงาน</h2>
          </div>
          <button
            type="button"
            class="icon-button"
            title="ปิด"
            @click="showEditModal = false"
          >
            <SvgIcon name="close" />
          </button>
        </div>
        <p class="modal-description">
          แก้ไขข้อมูลสำคัญของงาน และอัพเดตสถานะให้ทีมเห็นความคืบหน้าล่าสุด
        </p>
        <label>ลูกค้า<input v-model="editForm.customer" required /></label>
        <label v-if="editingType === 'appointment'"
          >สถานที่ปฏิบัติงาน<input v-model="editForm.site" required
        /></label>
        <label v-else
          >รายละเอียดปัญหา<input v-model="editForm.subject" required
        /></label>
        <div class="form-grid two">
          <label
            >วันที่กำหนด<input v-model="editForm.date" type="date" required
          /></label>
          <label
            >ช่วงเวลา<AppSelect
              v-model="editForm.time"
              :options="appointmentTimeOptions"
              placeholder="เลือกช่วงเวลา"
              aria-label="เลือกช่วงเวลางาน"
          /></label>
          <label v-if="editForm.time === 'กำหนดเอง'"
            >กรอกช่วงเวลาเอง<input
              v-model="customEditTime"
              placeholder="เช่น 09:00–12:00"
              required
          /></label>
        </div>
        <label v-if="editingType === 'service'"
          >ความสำคัญ<AppSelect
            v-model="editForm.priority"
            :options="servicePriorityOptions"
            aria-label="เลือกระดับความสำคัญของงาน"
        /></label>
        <label
          >สถานะงาน<AppSelect
            v-model="editForm.status"
            :options="editStatusOptions"
            aria-label="เลือกสถานะงาน"
        /></label>
        <div class="button-row end">
          <button
            type="button"
            class="button secondary"
            @click="showEditModal = false"
          >
            ยกเลิก
          </button>
          <button type="submit" class="button primary">
            <SvgIcon name="check" />บันทึกการแก้ไข
          </button>
        </div>
      </form>
    </div>
    <div v-if="toast" class="toast"><SvgIcon name="check" />{{ toast }}</div>
  </AppShell>
</template>

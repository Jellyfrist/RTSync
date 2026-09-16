<script setup>
// ศูนย์กลางสำหรับจัดการเบิกค่าน้ำมันของงานหน้างานทั้งสองประเภท
import { computed, onMounted, ref, watch } from "vue";
import AppShell from "@/components/layout/AppShell.vue";
import AppPageHeader from "@/components/ui/AppPageHeader.vue";
import AppSearchField from "@/components/ui/AppSearchField.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import TablePagination from "@/components/TablePagination.vue";
import { operationsApi } from "@/api/operationsApi";
import { mockDb } from "@/api/mockDb";

const formatISODate = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};
const today = new Date();
const dateFromToday = (offset) => {
  const date = new Date(today);
  date.setHours(0, 0, 0, 0);
  date.setDate(date.getDate() + offset);
  return formatISODate(date);
};
const formatCurrency = (value) => new Intl.NumberFormat("th-TH").format(value);

const claims = ref([]);
/*
  {
    id: "FUEL-260916-01",
    source: "ติดตั้ง",
    employee: "ณัฐพล แสนสุข",
    job: "INS-260916",
    date: dateFromToday(0),
    amount: 680,
    receipt: "RC-260916-01",
    status: "รอตรวจสอบ",
  },
  {
    id: "FUEL-260913-02",
    source: "บริการหลังการขาย",
    employee: "กิตติชัย มั่นคง",
    job: "SRV-260913",
    date: dateFromToday(-3),
    amount: 420,
    receipt: "RC-260913-02",
    status: "อนุมัติแล้ว",
  },
  {
    id: "FUEL-260906-03",
    source: "ติดตั้ง",
    employee: "วราภรณ์ วงศ์ศิริ",
    job: "INS-260906",
    date: dateFromToday(-10),
    amount: 560,
    receipt: "RC-260906-03",
    status: "อนุมัติแล้ว",
  },
  {
    id: "FUEL-260923-04",
    source: "บริการหลังการขาย",
    employee: "ณัฐพล แสนสุข",
    job: "SRV-260923",
    date: dateFromToday(7),
    amount: 390,
    receipt: "รอแนบใบเสร็จ",
    status: "รอเอกสาร",
  },
]); */
const claimSearch = ref("");
const claimStatusFilter = ref("ทั้งหมด");
const claimStatusOptions = ["ทั้งหมด", "รอตรวจสอบ", "อนุมัติแล้ว", "รอเอกสาร", "ไม่อนุมัติ"];
const showForm = ref(false);
const showEditModal = ref(false);
const editingClaim = ref(null);
const toast = ref("");
const employeeOptions = [
  "ณัฐพล แสนสุข",
  "กิตติชัย มั่นคง",
  "วราภรณ์ วงศ์ศิริ",
];
const employeeSearch = ref("");
const jobSearch = ref("");
const workItems = ref([]);
const form = ref({
  source: "ติดตั้ง",
  employee: "ณัฐพล แสนสุข",
  job: "",
  date: dateFromToday(0),
  amount: 0,
  receipt: "",
});
const editForm = ref({
  source: "ติดตั้ง",
  employee: "",
  job: "",
  date: "",
  amount: 0,
  receipt: "",
  status: "รอตรวจสอบ",
});
const filteredEmployeeOptions = computed(() => {
  const query = employeeSearch.value.trim().toLocaleLowerCase("th-TH");
  const matches = employeeOptions.filter((employee) =>
    employee.toLocaleLowerCase("th-TH").includes(query),
  );
  if (form.value.employee && !matches.includes(form.value.employee)) {
    return [form.value.employee, ...matches];
  }
  return matches;
});
const availableJobOptions = computed(() => {
  const query = jobSearch.value.trim().toLocaleLowerCase("th-TH");
  const claimedJobs = new Set(
    claims.value
      .filter((claim) => claim.employee === form.value.employee)
      .map((claim) => claim.job),
  );
  return workItems.value
    .filter((item) => {
      const source = item.type === "ติดตั้งระบบ" || item.type === "ตรวจหน้างาน"
        ? "ติดตั้ง"
        : "บริการหลังการขาย";
      const searchable = `${item.id} ${item.customer} ${item.subject || item.type}`.toLocaleLowerCase("th-TH");
      return source === form.value.source &&
        item.employees?.includes(form.value.employee) &&
        !claimedJobs.has(item.id) &&
        searchable.includes(query);
    })
    .sort((a, b) => new Date(a.date) - new Date(b.date));
});
const jobOptionLabel = (item) =>
  `${item.id} · ${item.customer} · ${item.date}`;

onMounted(async () => {
  const [appointments, serviceTickets, fuelClaims] = await Promise.all([
    operationsApi.getAppointments(),
    operationsApi.getServiceTickets(),
    operationsApi.getFuelClaims(),
  ]);
  claims.value = fuelClaims;
  workItems.value = [
    ...appointments,
    ...serviceTickets,
  ];
});
watch(
  [() => form.value.employee, () => form.value.source, jobSearch, availableJobOptions],
  () => {
    if (!availableJobOptions.value.some((item) => item.id === form.value.job)) {
      form.value.job = "";
    }
  },
  { deep: true },
);

const filteredClaims = computed(() => {
  const query = claimSearch.value.trim().toLocaleLowerCase("th-TH");
  return claims.value.filter((claim) => {
    const searchable = `${claim.id} ${claim.source} ${claim.employee} ${claim.job} ${claim.receipt}`.toLocaleLowerCase("th-TH");
    return (claimStatusFilter.value === "ทั้งหมด" || claim.status === claimStatusFilter.value) &&
      searchable.includes(query);
  });
});
const pendingCount = computed(
  () => claims.value.filter((claim) => claim.status !== "อนุมัติแล้ว").length,
);
const totalAmount = computed(() =>
  claims.value.reduce((total, claim) => total + Number(claim.amount), 0),
);
const statusClass = (status) =>
  status === "อนุมัติแล้ว" ? "success-tag" : status === "รอเอกสาร" ? "code-tag" : "warning-tag";
const sourceClass = (source) =>
  source === "ติดตั้ง" ? "fuel-source installation" : "fuel-source service";
function notify(message) {
  toast.value = message;
  setTimeout(() => {
    toast.value = "";
  }, 2800);
}
function openClaimForm() {
  employeeSearch.value = "";
  jobSearch.value = "";
  form.value = {
    source: "ติดตั้ง",
    employee: "ณัฐพล แสนสุข",
    job: "",
    date: dateFromToday(0),
    amount: 0,
    receipt: "",
  };
  showForm.value = true;
}
function saveClaim() {
  if (!form.value.job.trim() || !form.value.amount || !form.value.receipt.trim()) {
    notify("กรุณากรอกเลขที่งาน ยอดเงิน และเลขที่ใบเสร็จ");
    return;
  }
  const compactDate = form.value.date.replaceAll("-", "").slice(2);
  claims.value.unshift({
    id: `FUEL-${compactDate}-${String(claims.value.length + 1).padStart(2, "0")}`,
    ...form.value,
    amount: Number(form.value.amount),
    status: "รอตรวจสอบ",
  });
  mockDb.set("fuelClaims", claims.value);
  showForm.value = false;
  notify("บันทึกรายการเบิกค่าน้ำมันแล้ว");
}
function openClaimEdit(claim) {
  editingClaim.value = claim;
  editForm.value = { ...claim };
  showEditModal.value = true;
}
function saveClaimEdit() {
  if (!editingClaim.value) return;
  Object.assign(editingClaim.value, {
    ...editForm.value,
    amount: Number(editForm.value.amount),
  });
  mockDb.set("fuelClaims", claims.value);
  showEditModal.value = false;
  notify(`บันทึกรายละเอียด ${editingClaim.value.id} แล้ว`);
}
function cycleClaimStatus(claim) {
  const flow = ["รอตรวจสอบ", "อนุมัติแล้ว", "รอเอกสาร", "ไม่อนุมัติ"];
  const next = flow[(flow.indexOf(claim.status) + 1) % flow.length];
  claim.status = next;
  mockDb.set("fuelClaims", claims.value);
  notify(`${claim.id} เปลี่ยนสถานะเป็น ${next}`);
}
</script>

<template>
  <AppShell>
    <AppPageHeader
      eyebrow="FIELD EXPENSES"
      title="เบิกค่าน้ำมัน"
      description="จัดการคำขอเบิกค่าเดินทางของทีมงานติดตั้งและบริการหลังการขายในที่เดียว"
    />

    <section class="operations-table-section fuel-claims-panel">
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">รายการเบิกค่าน้ำมัน</h2>
          <p class="section-caption">เลือกดูรายการตามประเภทงาน และตรวจสอบใบเสร็จก่อนอนุมัติ</p>
        </div>
        <button class="button primary" type="button" @click="openClaimForm">
          <SvgIcon name="plus" />เปิดรายการเบิก
        </button>
      </div>
      <div class="task-overview-grid">
        <div><span>รายการเบิกทั้งหมด</span><strong>{{ filteredClaims.length }}</strong><small>รายการในมุมมองนี้</small></div>
        <div><span>รอตรวจสอบ</span><strong>{{ pendingCount }}</strong><small>ต้องตรวจเอกสารและอนุมัติ</small></div>
        <div><span>ยอดเบิกรวม</span><strong>฿{{ formatCurrency(totalAmount) }}</strong><small>จากรายการทั้งหมด</small></div>
      </div>
      <div class="task-table-tools table-filters-below-overview">
        <AppSearchField v-model="claimSearch" class-name="table-filter-search" placeholder="ค้นหาเลขที่เบิก งาน หรือพนักงาน..." label="ค้นหารายการเบิกค่าน้ำมัน" />
        <div class="table-filter-select control-field">
          <span>สถานะ</span>
          <select v-model="claimStatusFilter" aria-label="กรองสถานะรายการเบิก"><option v-for="status in claimStatusOptions" :key="status">{{ status }}</option></select>
        </div>
      </div>
      <div class="table-scroll">
        <table class="data-table operations-table fuel-claims-table">
          <thead>
            <tr><th>เลขที่เบิก</th><th>ขอเบิกจาก</th><th>พนักงาน</th><th>เลขที่งาน</th><th>วันที่เดินทาง</th><th>ยอดเบิก</th><th>ใบเสร็จ</th><th>สถานะ</th><th>จัดการ</th></tr>
          </thead>
          <tbody>
            <tr v-for="claim in filteredClaims" :key="claim.id">
              <td><span class="sku-code">{{ claim.id }}</span></td>
              <td><span :class="sourceClass(claim.source)">{{ claim.source }}</span></td>
              <td>{{ claim.employee }}</td>
              <td>{{ claim.job }}</td>
              <td>{{ claim.date }}</td>
              <td>฿{{ formatCurrency(claim.amount) }}</td>
              <td>{{ claim.receipt }}</td>
              <td><span :class="statusClass(claim.status)">{{ claim.status }}</span></td>
              <td><div class="table-actions"><button class="button secondary table-button table-icon-button" title="แก้ไขรายละเอียดการเบิก" aria-label="แก้ไขรายละเอียดการเบิก" @click="openClaimEdit(claim)"><SvgIcon name="edit" size="15" /></button><button class="button status-action table-button" title="อัพเดตสถานะการเบิก" aria-label="อัพเดตสถานะการเบิก" @click="cycleClaimStatus(claim)"><SvgIcon name="refresh" size="15" /><span>สถานะ</span></button></div></td>
            </tr>
            <tr v-if="!filteredClaims.length"><td colspan="9" class="empty-state">ยังไม่มีรายการเบิกในประเภทงานนี้</td></tr>
          </tbody>
        </table>
      </div>
      <TablePagination :total="filteredClaims.length" label="รายการเบิกค่าน้ำมัน" />
    </section>

    <div v-if="showEditModal" class="modal-backdrop" @click.self="showEditModal = false">
      <form class="modal fuel-claim-modal" @submit.prevent="saveClaimEdit">
        <div class="modal-heading">
          <div><span class="eyebrow">EDIT EXPENSE</span><h2>แก้ไขรายการเบิกค่าน้ำมัน</h2></div>
          <button type="button" class="icon-button" title="ปิด" @click="showEditModal = false"><SvgIcon name="close" /></button>
        </div>
        <p class="modal-description">แก้ไขข้อมูลการเดินทาง ยอดเบิก และสถานะเอกสารของรายการนี้</p>
        <label>ขอเบิกจาก<select v-model="editForm.source" required><option>ติดตั้ง</option><option>บริการหลังการขาย</option></select></label>
        <label>พนักงาน<input v-model="editForm.employee" required /></label>
        <label>เลขที่งาน<input v-model="editForm.job" required /></label>
        <label>วันที่เดินทาง<input v-model="editForm.date" type="date" required /></label>
        <label>ยอดเงิน (บาท)<input v-model="editForm.amount" type="number" min="1" required /></label>
        <label>เลขที่ใบเสร็จ<input v-model="editForm.receipt" required /></label>
        <label>สถานะ<select v-model="editForm.status" required><option>รอตรวจสอบ</option><option>อนุมัติแล้ว</option><option>รอเอกสาร</option><option>ไม่อนุมัติ</option></select></label>
        <div class="button-row end"><button type="button" class="button secondary" @click="showEditModal = false">ยกเลิก</button><button class="button primary" type="submit"><SvgIcon name="check" />บันทึกการแก้ไข</button></div>
      </form>
    </div>

    <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
      <form class="modal fuel-claim-modal" @submit.prevent="saveClaim">
        <div class="modal-heading">
          <div><span class="eyebrow">FUEL CLAIM</span><h2>เปิดรายการเบิกค่าน้ำมัน</h2></div>
          <button type="button" class="icon-button" title="ปิด" @click="showForm = false"><SvgIcon name="close" /></button>
        </div>
        <p class="modal-description">เลือกประเภทงานให้ตรงกับภารกิจ และแนบเลขที่ใบเสร็จทุกครั้ง</p>
        <label>ขอเบิกจาก<select v-model="form.source" required><option>ติดตั้ง</option><option>บริการหลังการขาย</option></select></label>
        <label class="employee-select-field">
          <span>พนักงาน</span>
          <div class="assignment-search">
            <SvgIcon name="search" size="16" />
            <input v-model="employeeSearch" type="search" aria-label="ค้นหาพนักงานสำหรับเบิกค่าน้ำมัน" placeholder="ค้นหาชื่อพนักงาน..." />
          </div>
          <select v-model="form.employee" required>
            <option v-for="employee in filteredEmployeeOptions" :key="employee" :value="employee">{{ employee }}</option>
          </select>
        </label>
        <label class="job-select-field">
          <span>เลขที่งาน</span>
          <div class="assignment-search">
            <SvgIcon name="search" size="16" />
            <input v-model="jobSearch" type="search" aria-label="ค้นหาเลขที่งานสำหรับเบิกค่าน้ำมัน" placeholder="ค้นหาเลขที่งาน หรือลูกค้า..." />
          </div>
          <select v-model="form.job" required :disabled="!availableJobOptions.length">
            <option value="" disabled>{{ availableJobOptions.length ? "เลือกงานที่ได้รับมอบหมาย" : "ไม่มีงานที่ขอเบิกได้" }}</option>
            <option v-for="item in availableJobOptions" :key="item.id" :value="item.id">{{ jobOptionLabel(item) }}</option>
          </select>
          <small class="field-helper">แสดงเฉพาะงานของพนักงานคนนี้ที่ยังไม่เคยขอเบิกค่าน้ำมัน</small>
        </label>
        <label>วันที่เดินทาง<input v-model="form.date" type="date" required /></label>
        <label>ยอดเงิน (บาท)<input v-model="form.amount" type="number" min="1" required /></label>
        <label>เลขที่ใบเสร็จ<input v-model="form.receipt" placeholder="เช่น RC-260916-01" required /></label>
        <div class="button-row end"><button type="button" class="button secondary" @click="showForm = false">ยกเลิก</button><button class="button primary" type="submit"><SvgIcon name="check" />บันทึกการเบิก</button></div>
      </form>
    </div>
    <div v-if="toast" class="toast"><SvgIcon name="check" />{{ toast }}</div>
  </AppShell>
</template>

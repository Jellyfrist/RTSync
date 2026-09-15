<script setup>
// ไฟล์นี้แสดงพนักงานและคำนวณเงินเดือนกับค่าล่วงเวลา
import { computed, onMounted, ref } from "vue";
import AppShell from "@/components/AppShell.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import { peopleApi } from "@/api/peopleApi";

// รายชื่อพนักงานจาก API
const employees = ref([]);
const activeId = ref("");
const collapsed = ref(false);
const search = ref("");
const toast = ref("");
const showModal = ref(false);
const editingEmployee = ref(null);
const form = ref({
  name: "",
  role: "",
  salary: 0,
  otHours: 0,
  otRate: 200,
  allowance: 0,
  deduction: 0,
});
onMounted(async () => {
  // โหลดข้อมูลพนักงานเมื่อเปิดหน้า
  employees.value = await peopleApi.getEmployees();
  if (employees.value.length) activeId.value = employees.value[0].id;
});
const visibleEmployees = computed(() =>
  employees.value.filter((item) =>
    `${item.name} ${item.role}`
      .toLowerCase()
      .includes(search.value.toLowerCase()),
  ),
);
const activeEmployee = computed(() =>
  employees.value.find((item) => item.id === activeId.value),
);
// คำนวณค่าล่วงเวลา ยอดก่อนหัก และยอดสุทธิของพนักงานที่เลือก
const payroll = computed(() => {
  const e = activeEmployee.value;
  if (!e) return { ot: 0, gross: 0, net: 0 };
  const ot = e.otHours * e.otRate;
  const gross = e.salary + ot + e.allowance;
  return { ot, gross, net: gross - e.deduction };
});
const money = (value) =>
  `฿${Number(value).toLocaleString("th-TH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const notify = (message) => {
  toast.value = message;
  setTimeout(() => {
    toast.value = "";
  }, 2600);
};
function resetForm() {
  form.value = {
    name: "",
    role: "",
    salary: 0,
    otHours: 0,
    otRate: 200,
    allowance: 0,
    deduction: 0,
  };
  editingEmployee.value = null;
}
function openAdd() {
  resetForm();
  showModal.value = true;
}
function openEdit() {
  const e = activeEmployee.value;
  form.value = {
    name: e.name,
    role: e.role,
    salary: e.salary,
    otHours: e.otHours,
    otRate: e.otRate,
    allowance: e.allowance,
    deduction: e.deduction,
  };
  editingEmployee.value = e;
  showModal.value = true;
}
function saveEmployee() {
  // บันทึกข้อมูลพนักงานใน state ของหน้าจอ
  if (!form.value.name.trim() || !form.value.role.trim()) return;
  const values = {
    ...form.value,
    salary: Number(form.value.salary),
    otHours: Number(form.value.otHours),
    otRate: Number(form.value.otRate),
    allowance: Number(form.value.allowance),
    deduction: Number(form.value.deduction),
  };
  if (editingEmployee.value) Object.assign(editingEmployee.value, values);
  else {
    const id = `EMP-TH-${String(20 + employees.value.length).padStart(3, "0")}`;
    employees.value.push({ ...values, id, initials: values.name.slice(0, 2) });
    activeId.value = id;
  }
  showModal.value = false;
  notify(
    editingEmployee.value ? "บันทึกข้อมูลพนักงานแล้ว" : "เพิ่มพนักงานใหม่แล้ว",
  );
}
function calculatePayroll() {
  notify(
    `คำนวณค่าจ้าง ${activeEmployee.value.name} แล้ว · สุทธิ ${money(payroll.value.net)}`,
  );
}
</script>

<template>
  <AppShell placeholder="ค้นหาพนักงาน, รหัสพนักงาน...">
    <div class="page-title">
      <div>
        <span class="eyebrow">PEOPLE & PAYROLL</span>
        <h1>ค่าตอบแทนและ OT พนักงาน</h1>
        <p>จัดการข้อมูลพนักงาน คำนวณค่าแรง ค่าล่วงเวลา และค่าจ้างรายเดือน</p>
      </div>
      <button class="button primary" @click="openAdd">
        <SvgIcon name="plus" />เพิ่มพนักงาน
      </button>
    </div>
    <section class="kpi-grid four">
      <article class="kpi-card">
        <div>
          <span>พนักงานทั้งหมด</span
          ><strong>{{ employees.length }} <small>คน</small></strong
          ><em>Active employee records</em>
        </div>
        <SvgIcon name="user" />
      </article>
      <article class="kpi-card">
        <div>
          <span>ชั่วโมง OT รวม</span
          ><strong
            >{{ employees.reduce((sum, e) => sum + e.otHours, 0) }}
            <small>ชม.</small></strong
          ><em>รอบเงินเดือน มิ.ย. 2025</em>
        </div>
        <SvgIcon name="settings" />
      </article>
      <article class="kpi-card warning">
        <div>
          <span>ยอดค่า OT รวม</span
          ><strong>{{
            money(employees.reduce((sum, e) => sum + e.otHours * e.otRate, 0))
          }}</strong
          ><em>รอตรวจสอบ 4 รายการ</em>
        </div>
        <SvgIcon name="wallet" />
      </article>
      <article class="kpi-card">
        <div>
          <span>ค่าจ้างรวมสุทธิ</span
          ><strong>{{
            money(
              employees.reduce(
                (sum, e) =>
                  sum +
                  e.salary +
                  e.otHours * e.otRate +
                  e.allowance -
                  e.deduction,
                0,
              ),
            )
          }}</strong
          ><em>คำนวณจากข้อมูลปัจจุบัน</em>
        </div>
        <SvgIcon name="wallet" />
      </article>
    </section>
    <section class="payroll-workbench">
      <div class="employee-list" :class="{ collapsed }">
        <div class="panel-toolbar">
          <strong>รายชื่อพนักงาน</strong
          ><button
            class="icon-button"
            title="ย่อ/ขยายรายชื่อ"
            @click="collapsed = !collapsed"
          >
            <SvgIcon name="grid" />
          </button>
        </div>
        <div class="search-inline" v-if="!collapsed">
          <SvgIcon name="search" /><input
            v-model="search"
            placeholder="ค้นหาพนักงาน"
          />
        </div>
        <button
          v-for="employee in visibleEmployees"
          :key="employee.id"
          class="employee-card"
          :class="{ selected: activeId === employee.id }"
          @click="activeId = employee.id"
        >
          <span class="employee-avatar">{{ employee.initials }}</span
          ><span v-if="!collapsed"
            ><strong>{{ employee.name }}</strong
            ><small>{{ employee.role }}</small
            ><em>OT {{ employee.otHours }} ชม.</em></span
          >
        </button>
      </div>
      <div class="detail-card" v-if="activeEmployee">
        <div class="detail-heading">
          <div>
            <span class="code-tag">{{ activeEmployee.id }}</span
            ><span class="success-tag">กำลังทำงาน</span>
            <h2>{{ activeEmployee.name }}</h2>
            <p>{{ activeEmployee.role }}</p>
          </div>
          <div class="button-row">
            <button class="button secondary" @click="openEdit">
              <SvgIcon name="edit" />แก้ไขข้อมูล</button
            ><button class="button primary" @click="calculatePayroll">
              คำนวณค่าจ้าง
            </button>
          </div>
        </div>
        <div class="info-grid">
          <div>
            <small>เงินเดือนพื้นฐาน</small
            ><strong>{{ money(activeEmployee.salary) }}</strong>
          </div>
          <div>
            <small>ค่า OT เดือนนี้</small
            ><strong
              >{{ money(payroll.ot) }}
              <small>({{ activeEmployee.otHours }} ชม.)</small></strong
            >
          </div>
          <div>
            <small>ค่าจ้างสุทธิ</small
            ><strong class="text-success">{{ money(payroll.net) }}</strong>
          </div>
        </div>
        <h3>รายละเอียดค่าตอบแทนประจำเดือน</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>รายการ</th>
              <th>ฐานคำนวณ</th>
              <th>ยอดเงิน</th>
              <th>สถานะ</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>เงินเดือนพื้นฐาน</td>
              <td>1 งวด</td>
              <td>{{ money(activeEmployee.salary) }}</td>
              <td><span class="success-tag">พร้อมจ่าย</span></td>
            </tr>
            <tr>
              <td>ค่าล่วงเวลา (OT)</td>
              <td>
                {{ activeEmployee.otHours }} ชม. ×
                {{ money(activeEmployee.otRate) }}
              </td>
              <td>{{ money(payroll.ot) }}</td>
              <td><span class="warning-tag">รอตรวจสอบ</span></td>
            </tr>
            <tr>
              <td>ค่าเบี้ยเลี้ยง/ค่าจ้างเพิ่มเติม</td>
              <td>รอบเดือนนี้</td>
              <td>{{ money(activeEmployee.allowance) }}</td>
              <td><span class="success-tag">พร้อมจ่าย</span></td>
            </tr>
            <tr>
              <td>รายการหัก</td>
              <td>ประกันสังคม/อื่น ๆ</td>
              <td class="text-danger">
                -{{ money(activeEmployee.deduction) }}
              </td>
              <td><span class="code-tag">ตรวจสอบแล้ว</span></td>
            </tr>
          </tbody>
        </table>
        <div class="payroll-total">
          <div>
            <span>รวมก่อนหัก</span><strong>{{ money(payroll.gross) }}</strong>
          </div>
          <div>
            <span>ค่าจ้างสุทธิ</span><strong>{{ money(payroll.net) }}</strong>
          </div>
        </div>
      </div>
    </section>
    <div
      v-if="showModal"
      class="modal-backdrop"
      @click.self="showModal = false"
    >
      <form class="modal employee-modal" @submit.prevent="saveEmployee">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">EMPLOYEE PROFILE</span>
            <h2>
              {{ editingEmployee ? "แก้ไขข้อมูลพนักงาน" : "เพิ่มพนักงาน" }}
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
            >ชื่อ-นามสกุล<input
              v-model="form.name"
              required
              placeholder="กรอกชื่อพนักงาน" /></label
          ><label
            >ตำแหน่ง<input
              v-model="form.role"
              required
              placeholder="เช่น ช่างติดตั้ง" /></label
          ><label
            >เงินเดือนพื้นฐาน<input
              v-model="form.salary"
              type="number"
              min="0" /></label
          ><label
            >ชั่วโมง OT<input
              v-model="form.otHours"
              type="number"
              min="0"
              step="0.5" /></label
          ><label
            >อัตรา OT ต่อชั่วโมง<input
              v-model="form.otRate"
              type="number"
              min="0" /></label
          ><label
            >ค่าเบี้ยเลี้ยง/ค่าจ้างเพิ่ม<input
              v-model="form.allowance"
              type="number"
              min="0" /></label
          ><label
            >รายการหัก<input v-model="form.deduction" type="number" min="0"
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
            บันทึกข้อมูลพนักงาน
          </button>
        </div>
      </form>
    </div>
    <div v-if="toast" class="toast"><SvgIcon name="check" />{{ toast }}</div>
  </AppShell>
</template>

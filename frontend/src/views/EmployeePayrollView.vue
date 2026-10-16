<script setup>
// ไฟล์นี้แสดงข้อมูลพนักงาน เงินเดือน และตารางงาน
import { computed, onMounted, ref } from "vue";
import AppShell from "@/components/layout/AppShell.vue";
import AppPageHeader from "@/components/ui/AppPageHeader.vue";
import AppSearchField from "@/components/ui/AppSearchField.vue";
import AppSelect from "@/components/ui/AppSelect.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import TablePagination from "@/components/TablePagination.vue";
import { peopleApi } from "@/api/peopleApi";
import { mockDb } from "@/api/mockDb";

// รายชื่อพนักงานจาก API
const employees = ref([]);
const activeId = ref("");
const collapsed = ref(false);
const search = ref("");
const roleFilter = ref("ทั้งหมด");
const toast = ref("");
const showModal = ref(false);
const editingEmployee = ref(null);
const employeeRoleOptions = ref(
  mockDb.get("employeeRoles").length ? mockDb.get("employeeRoles") : [],
);
const showRoleModal = ref(false);
const newRole = ref("");
const form = ref({
  name: "",
  role: "",
  phone: "",
  email: "",
  startDate: "",
  salary: 0,
  allowance: 0,
  deduction: 0,
});
onMounted(async () => {
  // โหลดข้อมูลพนักงานเมื่อเปิดหน้า
  employees.value = await peopleApi.getEmployees();
  if (employees.value.length) activeId.value = employees.value[0].id;
});
const visibleEmployees = computed(() =>
  employees.value.filter(
    (item) =>
      (roleFilter.value === "ทั้งหมด" || item.role === roleFilter.value) &&
      `${item.name} ${item.role} ${item.id}`
        .toLowerCase()
        .includes(search.value.toLowerCase()),
  ),
);
const roleOptions = computed(() => [
  "ทั้งหมด",
  ...employeeRoleOptions.value.filter((role) => role !== "ทั้งหมด"),
]);
const totalNetPayroll = computed(() =>
  employees.value.reduce(
    (sum, employee) =>
      sum + employee.salary + employee.allowance - employee.deduction,
    0,
  ),
);
const activeEmployee = computed(() =>
  employees.value.find((item) => item.id === activeId.value),
);
// คำนวณยอดก่อนหักและยอดสุทธิของพนักงานที่เลือก (ไม่มีระบบ OT)
const payroll = computed(() => {
  const e = activeEmployee.value;
  if (!e) return { gross: 0, net: 0 };
  const gross = e.salary + e.allowance;
  return { gross, net: gross - e.deduction };
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
    phone: "",
    email: "",
    startDate: "",
    salary: 0,
    allowance: 0,
    deduction: 0,
  };
  editingEmployee.value = null;
}
function openAdd() {
  resetForm();
  showModal.value = true;
}
function openRoleModal() {
  newRole.value = "";
  showRoleModal.value = true;
}
function saveRole() {
  const role = newRole.value.trim();
  if (!role) return;
  if (employeeRoleOptions.value.includes(role)) {
    notify("มีตำแหน่งนี้อยู่แล้ว");
    return;
  }
  employeeRoleOptions.value.push(role);
  mockDb.set("employeeRoles", employeeRoleOptions.value);
  form.value.role = role;
  showRoleModal.value = false;
  notify(`เพิ่มตำแหน่ง ${role} แล้ว`);
}
function openEdit(employee = activeEmployee.value) {
  const e = employee;
  if (!e) return;
  form.value = {
    name: e.name,
    role: e.role,
    phone: e.phone || "",
    email: e.email || "",
    startDate: e.startDate || "",
    salary: e.salary,
    allowance: e.allowance,
    deduction: e.deduction,
  };
  editingEmployee.value = e;
  showModal.value = true;
}
async function saveEmployee() {
  if (!form.value.name.trim() || !form.value.role.trim()) return;
  const values = {
    ...form.value,
    salary: Number(form.value.salary),
    allowance: Number(form.value.allowance),
    deduction: Number(form.value.deduction),
  };
  try {
    const saved = editingEmployee.value
      ? await peopleApi.updateEmployee(editingEmployee.value.id, values)
      : await peopleApi.createEmployee(values);
    if (editingEmployee.value) Object.assign(editingEmployee.value, saved);
    else {
      employees.value.push({ ...saved, initials: saved.name.slice(0, 2) });
      activeId.value = saved.id;
    }
    showModal.value = false;
    notify(
      editingEmployee.value ? "บันทึกข้อมูลพนักงานแล้ว" : "เพิ่มพนักงานใหม่แล้ว",
    );
  } catch (error) {
    notify(error?.message || "บันทึกข้อมูลพนักงานไม่สำเร็จ");
  }
}
function calculatePayroll() {
  notify(
    `คำนวณเงินเดือน ${activeEmployee.value.name} แล้ว · สุทธิ ${money(payroll.value.net)}`,
  );
}
</script>

<template>
  <AppShell>
    <AppPageHeader
      eyebrow="PEOPLE & PAYROLL"
      title="ข้อมูลพนักงานและเงินเดือน"
      description="จัดการข้อมูลพนักงาน เงินเดือน ตารางงาน และการเบิกค่าน้ำมัน"
    />
    <section class="operations-table-section employee-directory-section">
      <div class="task-table-heading">
        <div>
          <h2 class="section-heading">รายชื่อพนักงาน</h2>
          <p class="section-caption">
            จัดการข้อมูลบุคลากรและเปิดดูรายละเอียดค่าตอบแทนรายบุคคล
          </p>
        </div>
        <button class="button primary" type="button" @click="openAdd">
          <SvgIcon name="plus" />เพิ่มพนักงาน
        </button>
      </div>
      <div class="task-overview-grid">
        <div>
          <span>พนักงานทั้งหมด</span><strong>{{ employees.length }} คน</strong
          ><small>ข้อมูลบุคลากรในระบบ</small>
        </div>
        <div>
          <span>พร้อมมอบหมายงาน</span><strong>{{ employees.length }} คน</strong
          ><small>ทีมติดตั้งและบริการ</small>
        </div>
        <div>
          <span>ค่าจ้างรวมสุทธิ</span
          ><strong>{{ money(totalNetPayroll) }}</strong
          ><small>คำนวณจากข้อมูลปัจจุบัน</small>
        </div>
      </div>
      <div
        class="task-table-tools table-filters-below-overview employee-table-filters"
      >
        <AppSearchField
          v-model="search"
          class-name="table-filter-search"
          placeholder="ค้นหาชื่อพนักงาน รหัส หรือ ตำแหน่ง..."
          label="ค้นหาพนักงาน"
        />
        <div class="table-filter-select control-field employee-role-filter">
          <span>ตำแหน่ง</span>
          <AppSelect
            v-model="roleFilter"
            :options="roleOptions"
            search-placeholder="ค้นหาตำแหน่ง"
            aria-label="กรองตำแหน่งพนักงาน"
          />
        </div>
      </div>
      <div class="table-scroll employee-directory-table-wrap">
        <table class="data-table employee-directory-table">
          <thead>
            <tr>
              <th>รหัสพนักงาน</th>
              <th>ชื่อ-นามสกุล</th>
              <th>ตำแหน่ง</th>
              <th>เงินเดือนพื้นฐาน</th>
              <th>สถานะ</th>
              <th aria-label="การจัดการ"></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="employee in visibleEmployees" :key="employee.id">
              <tr class="employee-directory-row">
                <td>
                  <span class="code-tag">{{ employee.id }}</span>
                </td>
                <td>
                  <strong>{{ employee.name }}</strong>
                  <small class="table-subtext">{{
                    employee.phone || "ยังไม่ระบุเบอร์โทร"
                  }}</small>
                </td>
                <td>
                  {{ employee.role }}
                  <small class="table-subtext"
                    >เริ่มงาน {{ employee.startDate || "ยังไม่ระบุ" }}</small
                  >
                </td>
                <td class="mono">{{ money(employee.salary) }}</td>
                <td><span class="success-tag">กำลังทำงาน</span></td>
                <td class="employee-table-action">
                  <button
                    class="button secondary table-edit-button"
                    type="button"
                    :aria-label="`แก้ไขข้อมูล ${employee.name}`"
                    @click="openEdit(employee)"
                  >
                    <SvgIcon name="edit" size="16" />แก้ไข
                  </button>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
      <TablePagination :total="visibleEmployees.length" label="รายการพนักงาน" />
    </section>
    <div v-if="false">
      <div class="section-divider">
        <span class="section-kicker">01</span>
        <div>
          <strong>ภาพรวมทีมงาน</strong
          ><small>สถานะพนักงาน ค่าจ้าง และค่าใช้จ่ายที่ต้องติดตาม</small>
        </div>
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
            <span>พนักงานมีตารางงาน</span
            ><strong>{{ employees.length }} <small>คน</small></strong
            ><em>พร้อมมอบหมายงานติดตั้ง/บริการ</em>
          </div>
          <SvgIcon name="settings" />
        </article>
        <article class="kpi-card warning">
          <div>
            <span>เบิกค่าน้ำมันเดือนนี้</span><strong>{{ money(3250) }}</strong
            ><em>รอตรวจสอบ 2 รายการ</em>
          </div>
          <SvgIcon name="wallet" />
        </article>
        <article class="kpi-card">
          <div>
            <span>ค่าจ้างรวมสุทธิ</span
            ><strong>{{
              money(
                employees.reduce(
                  (sum, e) => sum + e.salary + e.allowance - e.deduction,
                  0,
                ),
              )
            }}</strong
            ><em>คำนวณจากข้อมูลปัจจุบัน</em>
          </div>
          <SvgIcon name="wallet" />
        </article>
      </section>
      <div class="section-divider">
        <span class="section-kicker">02</span>
        <div>
          <strong>พื้นที่จัดการพนักงาน</strong
          ><small>เลือกพนักงานเพื่อดูข้อมูลเงินเดือนและตารางงาน</small>
        </div>
      </div>
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
          <AppSearchField
            v-if="!collapsed"
            v-model="search"
            placeholder="ค้นหาพนักงาน"
            label="ค้นหาพนักงาน"
          />
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
              ><em>เงินเดือน {{ money(employee.salary) }}</em></span
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
                คำนวณเงินเดือน
              </button>
            </div>
          </div>
          <div class="info-grid">
            <div>
              <small>เงินเดือนพื้นฐาน</small
              ><strong>{{ money(activeEmployee.salary) }}</strong>
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
          <TablePagination :total="3" label="รายการค่าตอบแทน" />
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
    </div>
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
          ><label class="employee-role-field"
            ><span>ตำแหน่ง</span
            ><AppSelect
              v-model="form.role"
              :options="employeeRoleOptions"
              placeholder="เลือกตำแหน่ง"
              aria-label="เลือกตำแหน่งพนักงาน"
              required
              ><template #menu-footer="{ close }"
                ><button
                  type="button"
                  class="app-select-add-action"
                  @click.stop="
                    close();
                    openRoleModal();
                  "
                >
                  <SvgIcon name="plus" size="15" />เพิ่มตำแหน่ง
                </button></template
              ></AppSelect
            ></label
          ><label
            >เบอร์โทรศัพท์<input
              v-model="form.phone"
              type="tel"
              required
              placeholder="เช่น 081-234-5678" /></label
          ><label
            >อีเมล<input
              v-model="form.email"
              type="email"
              placeholder="เช่น name@rtsat.co.th" /></label
          ><label
            >วันที่เริ่มงาน<input
              v-model="form.startDate"
              type="date"
              required /></label
          ><label
            >เงินเดือนพื้นฐาน<input
              v-model="form.salary"
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
    <div
      v-if="showRoleModal"
      class="modal-backdrop"
      @click.self="showRoleModal = false"
    >
      <form class="modal category-modal" @submit.prevent="saveRole">
        <div class="modal-heading">
          <div>
            <span class="eyebrow">EMPLOYEE ROLE</span>
            <h2>เพิ่มตำแหน่ง</h2>
          </div>
          <button
            type="button"
            class="icon-button"
            title="ปิด"
            @click="showRoleModal = false"
          >
            <SvgIcon name="close" />
          </button>
        </div>
        <p class="modal-description">
          เพิ่มตำแหน่งสำหรับใช้ในข้อมูลพนักงานและการมอบหมายงาน
        </p>
        <label
          >ชื่อตำแหน่ง<input
            v-model="newRole"
            required
            placeholder="เช่น ผู้ประสานงานโครงการ"
        /></label>
        <div class="button-row end">
          <button
            type="button"
            class="button secondary"
            @click="showRoleModal = false"
          >
            ยกเลิก</button
          ><button class="button primary" type="submit">
            <SvgIcon name="check" />บันทึกตำแหน่ง
          </button>
        </div>
      </form>
    </div>
    <div v-if="toast" class="toast"><SvgIcon name="check" />{{ toast }}</div>
  </AppShell>
</template>

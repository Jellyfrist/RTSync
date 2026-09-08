<script setup>
import { ref, computed } from "vue";
import AppShell from "@/components/AppShell.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import { useModal } from "@/composables/useModal";

const customers = ref([
  {
    id: "089",
    code: "CUST-2024-089",
    name: "คุณสมศักดิ์ วัฒนากุล",
    phone: "081-924-XXXX",
    location: "อ.บางพลี จ.สมุทรปราการ",
    type: "บ้านพักอาศัย",
    status: "ชำระครบถ้วน",
    system: "10 kWp On-Grid (Huawei + Jinko)",
  },
  {
    id: "088",
    code: "CUST-2024-088",
    name: "บจก. ธนทรัพย์ โลจิสติกส์",
    phone: "089-455-XXXX",
    location: "นิคมฯ ลาดกระบัง กทม.",
    type: "ธุรกิจ/โรงงาน",
    status: "รอตรวจรับงวด 2",
    system: "120 kWp Zero-Export (Solis + Longi)",
  },
  {
    id: "087",
    code: "CUST-2024-087",
    name: "คุณกมลชนก สุขใจ",
    phone: "086-321-XXXX",
    location: "อ.เมือง จ.นนทบุรี",
    type: "บ้านพักอาศัย",
    status: "ชำระครบถ้วน",
    system: "5 kWp On-Grid (Huawei + Longi)",
  },
  {
    id: "086",
    code: "CUST-2024-086",
    name: "บริษัท พลังงานไทย จำกัด",
    phone: "082-888-XXXX",
    location: "อ.บางปะอิน จ.อยุธยา",
    type: "ธุรกิจ/โรงงาน",
    status: "รอนัดตรวจเช็ก",
    system: "80 kWp On-Grid (SMA + Jinko)",
  },
]);
const activeId = ref("089");
const selectedType = ref("ทั้งหมด");
const { isOpen, open, close } = useModal();
const selectedCustomer = computed(() =>
  customers.value.find((customer) => customer.id === activeId.value),
);
const visibleCustomers = computed(() =>
  selectedType.value === "ทั้งหมด"
    ? customers.value
    : customers.value.filter(
        (customer) =>
          customer.type === selectedType.value ||
          (selectedType.value === "รอนัดตรวจเช็ก" &&
            customer.status === selectedType.value),
      ),
);

// เลือกลูกค้าเพื่ออัปเดต master-detail panel
const selectCustomer = (id) => {
  activeId.value = id;
};
// แสดงการทำงานเดิมของปุ่มลงทะเบียนลูกค้าใหม่ด้วย dialog แบบ reactive
const showNotice = (message) => window.alert(message);
</script>

<template>
  <AppShell placeholder="ค้นหาชื่อลูกค้า, รหัส CUST, เลขที่สัญญา..."
    ><div class="page-title">
      <div>
        <h1>ระบบจัดการข้อมูลลูกค้าและประวัติการบริการ</h1>
        <p>Customer & Service History Management</p>
      </div>
      <div class="button-row">
        <button
          class="button secondary"
          @click="showNotice('ส่งออกรายชื่อลูกค้า Excel เรียบร้อย')"
        >
          <SvgIcon name="download" />ส่งออก Excel</button
        ><button class="button primary" @click="open">
          <SvgIcon name="plus" />ลงทะเบียนลูกค้าใหม่
        </button>
      </div>
    </div>
    <section class="kpi-grid">
      <article class="kpi-card">
        <div>
          <span>ลูกค้าทั้งหมดในระบบ</span><strong>184 <small>ราย</small></strong
          ><em>บ้านพักอาศัย 142 ราย ธุรกิจและโรงงาน 42 ราย</em>
        </div>
        <SvgIcon name="user" size="26" />
      </article>
      <article class="kpi-card warning">
        <div>
          <span>งานตรวจเช็ก & บริการคงค้าง</span
          ><strong>8 <small>รายการ</small></strong
          ><em>นัดหมายล่วงหน้าสัปดาห์นี้ 8 ไซต์งาน</em>
        </div>
        <SvgIcon name="settings" size="26" />
      </article>
    </section>
    <section class="master-detail">
      <div class="list-column">
        <div class="filter-tabs">
          <button
            v-for="type in [
              'ทั้งหมด',
              'บ้านพักอาศัย',
              'ธุรกิจ/โรงงาน',
              'รอนัดตรวจเช็ก',
            ]"
            :key="type"
            :class="{ selected: selectedType === type }"
            @click="selectedType = type"
          >
            {{ type }}
          </button>
        </div>
        <button
          v-for="customer in visibleCustomers"
          :key="customer.id"
          class="customer-card"
          :class="{ selected: activeId === customer.id }"
          @click="selectCustomer(customer.id)"
        >
          <div class="card-top">
            <b>{{ customer.code }}</b
            ><span
              :class="
                customer.status === 'ชำระครบถ้วน' ? 'success' : 'warning-tag'
              "
              >{{ customer.status }}</span
            >
          </div>
          <strong>{{ customer.name }}</strong
          ><small
            >{{ customer.phone }} <span>{{ customer.location }}</span></small
          >
          <div class="card-footer">
            <span>{{ customer.system }}</span
            ><span>{{ customer.type }}</span>
          </div>
        </button>
      </div>
      <div class="detail-card" v-if="selectedCustomer">
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
              @click="showNotice('แก้ไขข้อมูลลูกค้า')"
            >
              <SvgIcon name="edit" />แก้ไข</button
            ><button
              class="button primary"
              @click="showNotice('เปิดคำสั่งงานบริการใหม่')"
            >
              <SvgIcon name="plus" />งานบริการใหม่
            </button>
          </div>
        </div>
        <div class="info-grid">
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
        <h3>ประวัติการบริการล่าสุด</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>วันที่</th>
              <th>ประเภทงาน</th>
              <th>รายละเอียด</th>
              <th>สถานะ</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>12 มิ.ย. 2025</td>
              <td>ตรวจเช็กประจำปี</td>
              <td>ตรวจสอบแผงและอินเวอร์เตอร์</td>
              <td><span class="success-tag">เสร็จสิ้น</span></td>
            </tr>
            <tr>
              <td>18 ม.ค. 2025</td>
              <td>แจ้งซ่อม</td>
              <td>ปรับปรุงระบบ monitoring</td>
              <td><span class="success-tag">เสร็จสิ้น</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <div class="modal">
        <div class="modal-heading">
          <h2>ลงทะเบียนลูกค้าใหม่</h2>
          <button class="icon-button" @click="close">
            <SvgIcon name="close" />
          </button>
        </div>
        <label>ชื่อลูกค้า<input placeholder="กรอกชื่อลูกค้า" /></label
        ><label>เบอร์โทรศัพท์<input placeholder="กรอกเบอร์โทรศัพท์" /></label>
        <div class="button-row end">
          <button class="button secondary" @click="close">ยกเลิก</button
          ><button class="button primary" @click="close">บันทึกลูกค้า</button>
        </div>
      </div>
    </div>
  </AppShell>
</template>

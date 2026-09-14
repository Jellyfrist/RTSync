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
const customerPanel = ref('profile');
const editingCustomer = ref(null);
const customerForm = ref({ name: '', phone: '', location: '', type: 'บ้านพักอาศัย', system: '' });
const quoteItems = ref([]);
const receiptIssued = ref(false);
const quoteProducts = [
  { sku: 'SP-JA-550M', name: 'แผงโซลาร์ JA Solar 550W', price: 4150, unit: 'แผง' },
  { sku: 'INV-HW-10K3P', name: 'Huawei SUN2000-10KTL-M1', price: 58900, unit: 'เครื่อง' },
  { sku: 'BAT-BYD-10', name: 'แบตเตอรี่ BYD 10.2kWh', price: 165000, unit: 'ชุด' },
];
const quoteTotal = computed(() => quoteItems.value.reduce((sum, item) => sum + item.price * item.qty, 0));
const money = value => new Intl.NumberFormat('th-TH').format(value);
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
  customerPanel.value = 'profile'; quoteItems.value = []; receiptIssued.value = false;
};
const showNotice = (message) => window.alert(message);
function openCreateCustomer() { editingCustomer.value = null; customerForm.value = { name: '', phone: '', location: '', type: 'บ้านพักอาศัย', system: '' }; open(); }
function openEditCustomer() { editingCustomer.value = selectedCustomer.value; customerForm.value = { name: selectedCustomer.value.name, phone: selectedCustomer.value.phone, location: selectedCustomer.value.location, type: selectedCustomer.value.type, system: selectedCustomer.value.system }; open(); }
function saveCustomer() {
  if (!customerForm.value.name.trim() || !customerForm.value.phone.trim()) return;
  if (editingCustomer.value) Object.assign(editingCustomer.value, customerForm.value);
  else { const id = String(90 + customers.value.length); const customer = { id, code: `CUST-2025-${id}`, status: 'รอเปิดบัญชี', ...customerForm.value }; customers.value.unshift(customer); activeId.value = id; }
  close();
}
function addQuote(product) { const item = quoteItems.value.find(row => row.sku === product.sku); if (item) item.qty += 1; else quoteItems.value.push({ ...product, qty: 1 }); }
function createQuote() { if (!quoteItems.value.length) return showNotice('กรุณาเพิ่มสินค้าในใบเสนอราคา'); customerPanel.value = 'quote'; showNotice('บันทึกใบเสนอราคา QT-25062 เรียบร้อย'); }
function issueReceipt() { if (!quoteTotal.value) return showNotice('ยังไม่มียอดสำหรับออกใบเสร็จ'); receiptIssued.value = true; }
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
        ><button class="button primary" @click="openCreateCustomer">
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
              @click="openEditCustomer"
            >
              <SvgIcon name="edit" />แก้ไข</button
            ><button
              class="button primary"
              @click="customerPanel = 'quote'"
            >
              <SvgIcon name="quote" />ทำใบเสนอราคา
            </button>
          </div>
        </div>
        <nav class="inventory-tabs customer-tabs" aria-label="เมนูข้อมูลลูกค้า"><button :class="{ active: customerPanel === 'profile' }" @click="customerPanel = 'profile'"><SvgIcon name="user" />ข้อมูลลูกค้า</button><button :class="{ active: customerPanel === 'quote' }" @click="customerPanel = 'quote'"><SvgIcon name="quote" />ใบเสนอราคา</button><button :class="{ active: customerPanel === 'receipt' }" @click="customerPanel = 'receipt'"><SvgIcon name="wallet" />ใบเสร็จ</button></nav>
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
        <h3 v-if="customerPanel === 'profile'">ประวัติการบริการล่าสุด</h3>
        <table v-if="customerPanel === 'profile'" class="data-table">
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
        <div v-if="customerPanel === 'quote'" class="customer-workspace"><div class="workspace-heading"><div><h3>สร้างใบเสนอราคา</h3><p>เลือกสินค้าและจัดทำใบเสนอราคาให้ {{ selectedCustomer.name }}</p></div><span class="code-tag">QT-25062 · ร่าง</span></div><div class="quote-product-grid"><button v-for="product in quoteProducts" :key="product.sku" class="quote-product" @click="addQuote(product)"><strong>{{ product.name }}</strong><small>{{ product.sku }} · ฿{{ money(product.price) }} / {{ product.unit }}</small><span><SvgIcon name="plus" />เพิ่มรายการ</span></button></div><table class="data-table"><thead><tr><th>รายการ</th><th>จำนวน</th><th>รวม</th></tr></thead><tbody><tr v-for="item in quoteItems" :key="item.sku"><td>{{ item.name }}</td><td>{{ item.qty }} {{ item.unit }}</td><td>฿{{ money(item.price * item.qty) }}</td></tr><tr v-if="!quoteItems.length"><td colspan="3" class="empty-state">ยังไม่มีรายการในใบเสนอราคา</td></tr></tbody></table><div class="order-total"><span>ยอดรวมใบเสนอราคา</span><strong>฿{{ money(quoteTotal) }}</strong></div><div class="button-row end"><button class="button secondary" @click="customerPanel = 'profile'">ยกเลิก</button><button class="button primary" @click="createQuote">บันทึกใบเสนอราคา</button></div></div>
        <div v-if="customerPanel === 'receipt'" class="customer-workspace receipt-workspace"><div class="workspace-heading"><div><span class="success-tag">ชำระเงินสำเร็จ</span><h3>ออกใบเสร็จรับเงิน</h3><p>สร้างใบเสร็จจากใบเสนอราคาที่บันทึกไว้สำหรับ {{ selectedCustomer.name }}</p></div><SvgIcon name="wallet" size="26" /></div><div class="receipt-summary"><span>เลขที่ใบเสร็จ</span><strong>{{ receiptIssued ? 'RC-25062' : 'รอออกเลขที่' }}</strong><span>ยอดที่รับชำระ</span><strong>฿{{ money(quoteTotal || 174000) }}</strong><span>วันที่ออกเอกสาร</span><strong>วันนี้</strong></div><button class="button primary full" :disabled="receiptIssued" @click="issueReceipt"><SvgIcon name="check" />{{ receiptIssued ? 'ออกใบเสร็จแล้ว' : 'ออกใบเสร็จรับเงิน' }}</button></div>
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
        <label>ชื่อลูกค้า<input v-model="customerForm.name" required placeholder="กรอกชื่อลูกค้า" /></label
        ><label>เบอร์โทรศัพท์<input v-model="customerForm.phone" required placeholder="กรอกเบอร์โทรศัพท์" /></label
        ><label>ประเภทลูกค้า<select v-model="customerForm.type"><option>บ้านพักอาศัย</option><option>ธุรกิจ/โรงงาน</option></select></label
        ><label>สถานที่ติดตั้ง<input v-model="customerForm.location" placeholder="กรอกจังหวัด/สถานที่" /></label
        ><label>ระบบที่ติดตั้ง<input v-model="customerForm.system" placeholder="เช่น 10 kWp On-Grid" /></label>
        <div class="button-row end">
          <button class="button secondary" @click="close">ยกเลิก</button
          ><button class="button primary" @click="saveCustomer">บันทึกลูกค้า</button>
        </div>
      </div>
    </div>
  </AppShell>
</template>

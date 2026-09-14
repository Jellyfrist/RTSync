<script setup>
import { ref, computed } from "vue";
import AppShell from "@/components/AppShell.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import { useModal } from "@/composables/useModal";
const suppliers = ref([
  {
    id: "SUP-TH-001",
    name: "บจก. ซันไซน์ โซล่า โซลูชั่น",
    category: "Solar Panels",
    description: "ตัวแทนหลัก Tier-1 แผงโซล่าเซลล์เกรดเอ",
    delivery: "2-3 วัน",
    sku: 48,
  },
  {
    id: "SUP-TH-004",
    name: "บจก. สยาม ซีเคียวริตี้ ซัพพลาย",
    category: "CCTV & Security",
    description: "ศูนย์จำหน่ายอุปกรณ์กล้องวงจรปิด AI CCTV",
    delivery: "1-2 วัน",
    sku: 64,
  },
  {
    id: "SUP-TH-012",
    name: "บมจ. กรีนเทค อิเล็คทริค อินดัสทรี",
    category: "Electrical & Mounting",
    description: "ผู้ผลิตตู้ Combiner Box และอุปกรณ์จับยึด",
    delivery: "3-5 วัน",
    sku: 82,
  },
  {
    id: "SUP-TH-019",
    name: "บจก. ซันพาวเวอร์ ซัพพลาย แอนด์ เอ็นจิเนียริ่ง",
    category: "Cabling & Protection",
    description: "ตัวแทนจำหน่าย Inverter และ Energy Storage",
    delivery: "1 วัน",
    sku: 36,
  },
]);
const selectedId = ref("SUP-TH-001");
const filter = ref("");
const { isOpen, open, close } = useModal();
const editingSupplier = ref(null);
const form = ref({ name: '', category: '', description: '', delivery: '2-3 วัน' });
const products = ref([
  { sku: 'SP-JA-550M', name: 'JA Solar 550W', supplierId: 'SUP-TH-001', price: 4150, stock: 140, reorderPoint: 40, status: 'พร้อมสั่งซื้อ' },
  { sku: 'SP-LN-585X', name: 'Longi Hi-MO 6 585W', supplierId: 'SUP-TH-001', price: 4350, stock: 84, reorderPoint: 35, status: 'พร้อมสั่งซื้อ' },
  { sku: 'INV-HW-10K3P', name: 'Huawei SUN2000-10KTL', supplierId: 'SUP-TH-019', price: 58900, stock: 6, reorderPoint: 10, status: 'ต้องสั่งเพิ่ม' },
  { sku: 'CB-DC-6MM', name: 'สายไฟโซลาร์ DC 6mm', supplierId: 'SUP-TH-012', price: 1850, stock: 210, reorderPoint: 100, status: 'พร้อมสั่งซื้อ' },
]);
const visibleSuppliers = computed(() =>
  suppliers.value.filter((item) =>
    `${item.name} ${item.category}`
      .toLowerCase()
      .includes(filter.value.toLowerCase()),
  ),
);
const selectedSupplier = computed(() =>
  suppliers.value.find((item) => item.id === selectedId.value),
);
const supplierProducts = computed(() => products.value.filter(item => item.supplierId === selectedId.value));
const unassignedProducts = computed(() => products.value.filter(item => item.supplierId !== selectedId.value));
const productToAssign = ref('');
function resetForm() { form.value = { name: '', category: '', description: '', delivery: '2-3 วัน' }; editingSupplier.value = null; }
function openAdd() { resetForm(); open(); }
function openEdit() { form.value = { ...selectedSupplier.value }; editingSupplier.value = selectedSupplier.value; open(); }
function saveSupplier() {
  if (!form.value.name.trim() || !form.value.category.trim()) return;
  if (editingSupplier.value) Object.assign(editingSupplier.value, form.value);
  else { const id = `SUP-TH-${String(20 + suppliers.value.length).padStart(3, '0')}`; suppliers.value.push({ ...form.value, id, sku: 0 }); selectedId.value = id; }
  close();
}
function assignProduct() { const product = products.value.find(item => item.sku === productToAssign.value); if (!product) return; product.supplierId = selectedId.value; productToAssign.value = ''; }
</script>

<template>
  <AppShell placeholder="ค้นหาซัพพลายเออร์, SKU..."
    ><div class="page-title">
      <div>
        <h1>ศูนย์จัดการซัพพลายเออร์และสินค้า</h1>
        <p>Suppliers & Sourcing Hub</p>
      </div>
      <button class="button primary" @click="openAdd">
        <SvgIcon name="plus" />เพิ่มซัพพลายเออร์
      </button>
    </div>
    <section class="master-detail">
      <div class="list-column">
        <div class="search-inline">
          <SvgIcon name="search" /><input
            v-model="filter"
            placeholder="ค้นหาซัพพลายเออร์"
          />
        </div>
        <button
          v-for="supplier in visibleSuppliers"
          :key="supplier.id"
          class="customer-card"
          :class="{ selected: selectedId === supplier.id }"
          @click="selectedId = supplier.id"
        >
          <strong>{{ supplier.name }}</strong
          ><span class="code-tag">{{ supplier.category }}</span
          ><small>{{ supplier.description }}</small>
          <div class="card-footer">
            <span>ส่งมอบ {{ supplier.delivery }}</span
            ><span>{{ supplier.sku }} SKU</span>
          </div>
        </button>
      </div>
      <div class="detail-card" v-if="selectedSupplier">
        <div class="detail-heading">
          <div>
            <span class="code-tag">{{ selectedSupplier.id }}</span>
            <h2>{{ selectedSupplier.name }}</h2>
            <p>{{ selectedSupplier.description }}</p>
          </div>
          <button class="button secondary" @click="openEdit">
            <SvgIcon name="edit" />แก้ไขข้อมูล
          </button>
        </div>
        <div class="info-grid">
          <div>
            <small>หมวดหมู่หลัก</small
            ><strong>{{ selectedSupplier.category }}</strong>
          </div>
          <div>
            <small>ระยะเวลาจัดส่ง</small
            ><strong>{{ selectedSupplier.delivery }}</strong>
          </div>
          <div>
            <small>จำนวน SKU</small
            ><strong>{{ selectedSupplier.sku }} รายการ</strong>
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
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in supplierProducts" :key="product.sku">
              <td class="mono">{{ product.sku }}</td>
              <td><strong>{{ product.name }}</strong><small class="table-subtext">Stock {{ product.stock }} · Reorder Point {{ product.reorderPoint }}</small></td>
              <td>฿{{ product.price.toLocaleString('th-TH') }}</td>
              <td><span :class="product.status === 'ต้องสั่งเพิ่ม' ? 'warning-tag' : 'success-tag'">{{ product.status }}</span></td>
            </tr>
            <tr v-if="!supplierProducts.length"><td colspan="4" class="empty-state">ยังไม่มีสินค้าที่ผูกกับซัพพลายเออร์รายนี้</td></tr>
          </tbody>
        </table>
        <div class="supplier-product-link"><div><strong>ผูกสินค้าเข้ากับ Supplier</strong><small>กำหนดแหล่งจัดซื้อให้แต่ละ SKU เพื่อใช้กับงานสั่งซื้อและ Reorder</small></div><div class="button-row"><select v-model="productToAssign" aria-label="เลือกสินค้าที่จะผูก"><option value="">เลือกสินค้า</option><option v-for="product in unassignedProducts" :key="product.sku" :value="product.sku">{{ product.sku }} · {{ product.name }}</option></select><button class="button secondary" :disabled="!productToAssign" @click="assignProduct"><SvgIcon name="plus" />ผูกสินค้า</button></div></div>
      </div>
    </section>
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <div class="modal">
        <div class="modal-heading">
          <h2>{{ editingSupplier ? 'แก้ไขข้อมูลซัพพลายเออร์' : 'เพิ่มซัพพลายเออร์' }}</h2>
          <button class="icon-button" @click="close">
            <SvgIcon name="close" />
          </button>
        </div>
        <label>ชื่อบริษัท<input v-model="form.name" required placeholder="กรอกชื่อบริษัท" /></label
        ><label>หมวดหมู่<input v-model="form.category" required placeholder="เช่น Solar Panels" /></label
        ><label>รายละเอียด<input v-model="form.description" placeholder="คำอธิบายและจุดเด่นของ Supplier" /></label
        ><label>ระยะเวลาจัดส่ง<input v-model="form.delivery" placeholder="เช่น 2-3 วัน" /></label>
        <div class="button-row end">
          <button class="button secondary" @click="close">ยกเลิก</button
          ><button class="button primary" @click="saveSupplier">บันทึก</button>
        </div>
      </div>
    </div></AppShell
  >
</template>

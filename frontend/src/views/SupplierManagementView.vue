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
</script>

<template>
  <AppShell placeholder="ค้นหาซัพพลายเออร์, SKU..."
    ><div class="page-title">
      <div>
        <h1>ศูนย์จัดการซัพพลายเออร์และสินค้า</h1>
        <p>Suppliers & Sourcing Hub</p>
      </div>
      <button class="button primary" @click="open">
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
          <button class="button secondary">
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
            <tr>
              <td class="mono">SP-JA-550M</td>
              <td>JA Solar 550W</td>
              <td>฿4,150</td>
              <td><span class="success-tag">พร้อมสั่งซื้อ</span></td>
            </tr>
            <tr>
              <td class="mono">INV-HW-10K3P</td>
              <td>Huawei SUN2000-10KTL</td>
              <td>฿58,900</td>
              <td><span class="success-tag">พร้อมสั่งซื้อ</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <div class="modal">
        <div class="modal-heading">
          <h2>เพิ่มซัพพลายเออร์</h2>
          <button class="icon-button" @click="close">
            <SvgIcon name="close" />
          </button>
        </div>
        <label>ชื่อบริษัท<input placeholder="กรอกชื่อบริษัท" /></label
        ><label>หมวดหมู่<input placeholder="กรอกหมวดหมู่" /></label>
        <div class="button-row end">
          <button class="button secondary" @click="close">ยกเลิก</button
          ><button class="button primary" @click="close">บันทึก</button>
        </div>
      </div>
    </div></AppShell
  >
</template>

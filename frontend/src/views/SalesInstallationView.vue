<script setup>
import { ref, computed } from "vue";
import AppShell from "@/components/AppShell.vue";
import SvgIcon from "@/components/SvgIcon.vue";
const catalog = [
  { name: "แผงโซลาร์ Longi 550W", price: 4150, qty: 18, unit: "แผง" },
  { name: "Inverter Huawei 10kW 3P", price: 58900, qty: 1, unit: "เครื่อง" },
  { name: "แบตเตอรี่ BYD 10.2kWh", price: 165000, qty: 1, unit: "ชุด" },
];
const bill = ref([]);
const total = computed(() =>
  bill.value.reduce((sum, item) => sum + item.price * item.qty, 0),
);
const addToBill = (product) => {
  const existing = bill.value.find((item) => item.name === product.name);
  if (existing) existing.qty += product.qty;
  else bill.value.push({ ...product });
};
const removeItem = (index) => bill.value.splice(index, 1);
const formatCurrency = (value) => new Intl.NumberFormat("th-TH").format(value);
</script>

<template>
  <AppShell placeholder="ค้นหา SKU, รหัสสินค้า, ชื่อลูกค้า..."
    ><div class="page-title">
      <div>
        <h1>ระบบขายสินค้า นัดหมายติดตั้ง และบริการหลังการขาย</h1>
        <p>Sales, Installation & After-sales Service</p>
      </div>
      <span class="online-status">ระบบออนไลน์ (ONLINE)</span>
    </div>
    <section class="master-detail sales-layout">
      <div class="list-column">
        <div class="panel compact">
          <h3><SvgIcon name="box" />แค็ตตาล็อกสินค้าพร้อมขาย</h3>
          <span class="muted">148 รายการ</span>
        </div>
        <article
          v-for="product in catalog"
          :key="product.name"
          class="product-card"
        >
          <div class="card-top">
            <b>{{ product.name }}</b
            ><strong>฿{{ formatCurrency(product.price) }}</strong>
          </div>
          <small>คงเหลือพร้อมขาย และรับประกันตามมาตรฐาน</small
          ><button class="button primary full" @click="addToBill(product)">
            <SvgIcon name="plus" />เพิ่ม {{ product.qty }}
            {{ product.unit }} ลงบิล
          </button>
        </article>
      </div>
      <div class="detail-card">
        <div class="detail-heading">
          <div>
            <span class="code-tag">CUST-2024-089</span
            ><span class="success-tag">Tier-A VIP</span>
            <h2>คุณสมศักดิ์ วัฒนากุล</h2>
            <p>
              สถานที่ติดตั้ง: หมู่บ้านมัณฑนา บางนา-วงแหวน อ.บางพลี จ.สมุทรปราการ
            </p>
          </div>
          <button class="button secondary">เปลี่ยนลูกค้า</button>
        </div>
        <h3>รายการสินค้าในใบเสนอราคา</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>รายการ</th>
              <th>จำนวน</th>
              <th>ราคา</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in bill" :key="item.name">
              <td>{{ item.name }}</td>
              <td>{{ item.qty }} {{ item.unit }}</td>
              <td>฿{{ formatCurrency(item.price * item.qty) }}</td>
              <td>
                <button class="icon-button" @click="removeItem(index)">
                  <SvgIcon name="close" />
                </button>
              </td>
            </tr>
            <tr v-if="!bill.length">
              <td colspan="4" class="empty-state">
                ยังไม่มีรายการสินค้า กรุณาเลือกสินค้าจากแค็ตตาล็อก
              </td>
            </tr>
          </tbody>
        </table>
        <div class="order-total">
          <span>ยอดรวมทั้งสิ้น</span
          ><strong>฿{{ formatCurrency(total) }}</strong>
        </div>
        <button
          class="button primary full"
          @click="window.alert('บันทึกคำสั่งขายและล็อกคิวนัดหมายสำเร็จ!')"
        >
          บันทึกคำสั่งขายและล็อกคิว
        </button>
      </div>
    </section></AppShell
  >
</template>

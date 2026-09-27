<script setup>
import { onMounted } from 'vue';
import AppShell from "@/components/AppShell.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import { useSalesController } from "@/controllers/useSalesController.js";

const { catalog, bill, total, reference, actor, loading, error, message,
  refresh, addToBill, removeItem, formatCurrency, saveOrder } = useSalesController();
onMounted(refresh);
</script>

<template>
  <AppShell placeholder="ค้นหา SKU, รหัสสินค้า, ชื่อลูกค้า..."
    ><div class="page-title">
      <div>
        <h1>แค็ตตาล็อกและจ่ายสินค้าเพื่อการขาย</h1>
        <p>สินค้าในหน้านี้ใช้ข้อมูลเดียวกับคลัง</p>
      </div>
      <button class="button secondary" :disabled="loading" @click="refresh">รีเฟรชข้อมูล</button>
    </div>
    <p v-if="error" class="workflow-alert error" role="alert">{{ error }}</p>
    <p v-if="message" class="workflow-alert success-message" role="status">{{ message }}</p>
    <p v-if="loading" class="muted" role="status">กำลังโหลด...</p>
    <section class="master-detail sales-layout">
      <div class="list-column">
        <div class="panel compact">
          <h3><SvgIcon name="box" />แค็ตตาล็อกสินค้าพร้อมขาย</h3>
          <span class="muted">{{ catalog.length }} รายการ</span>
        </div>
        <article
          v-for="product in catalog"
          :key="product.sku"
          class="product-card"
        >
          <div class="card-top">
            <b>{{ product.name }}</b
            ><strong>฿{{ formatCurrency(product.price) }}</strong>
          </div>
          <small>SKU {{ product.sku }} · คงเหลือ {{ product.stock }} {{ product.unit }}</small
          ><button class="button primary full" :disabled="loading || product.stock <= 0" @click="addToBill(product)">
            <SvgIcon name="plus" />เพิ่ม 1
            {{ product.unit }} ลงบิล
          </button>
        </article>
      </div>
      <div class="detail-card">
        <div class="detail-heading"><div><h2>รายการจ่ายสินค้า</h2><p>บันทึกเลขอ้างอิงของงานขายก่อนตัดสต็อก</p></div></div>
        <div class="workflow-form">
          <label>เลขอ้างอิง<input v-model.trim="reference" maxlength="120" placeholder="เช่น SALE-2026-001" /></label>
          <label>ผู้ดำเนินการ<input v-model.trim="actor" maxlength="120" /></label>
        </div>
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
            <tr v-for="(item, index) in bill" :key="item.sku">
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
          <span>ยอดตามราคาขาย</span
          ><strong>฿{{ formatCurrency(total) }}</strong>
        </div>
        <button
          class="button primary full"
          :disabled="loading || !bill.length" @click="saveOrder"
        >
          บันทึกการจ่ายสินค้าและตัดสต็อก
        </button>
      </div>
    </section></AppShell
  >
</template>

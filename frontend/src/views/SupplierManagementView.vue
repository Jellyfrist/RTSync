<script setup>
import { onMounted } from 'vue';
import AppShell from '@/components/AppShell.vue';
import { useProcurementController } from '@/controllers/useProcurementController.js';

const workflow = useProcurementController();
const {
  suppliers, products, orders, selectedId, selectedOrder, history, actor,
  supplierForm, linkForm, orderForm, lineForm, receiptReference, receiptQuantities,
  loading, error, message, refresh, selectOrder, addLine, removeLine,
  createSupplier, linkProduct, createOrder, approve, receive,
} = workflow;
onMounted(refresh);
</script>

<template>
  <AppShell placeholder="ค้นหาซัพพลายเออร์, SKU...">
    <div class="page-title">
      <div><h1>จัดซื้อและรับสินค้า</h1><p>Purchase orders, approval, goods receipt and stock history</p></div>
      <button class="button secondary" :disabled="loading" @click="refresh">รีเฟรชข้อมูล</button>
    </div>
    <p v-if="error" class="workflow-alert error" role="alert">{{ error }}</p>
    <p v-if="message" class="workflow-alert success-message" role="status">{{ message }}</p>
    <p v-if="loading" class="muted" role="status">กำลังโหลด...</p>

    <section class="panel workflow-section">
      <h2>ข้อมูลหลัก</h2>
      <p class="muted">สร้างสินค้าในหน้าคลังก่อนทำใบสั่งซื้อ</p>
      <form class="workflow-form" @submit.prevent="createSupplier">
        <label>ชื่อซัพพลายเออร์<input v-model.trim="supplierForm.name" required maxlength="255" /></label>
        <label>หมวดหมู่<input v-model.trim="supplierForm.category" required maxlength="120" /></label>
        <label>ระยะเวลาจัดส่ง<input v-model.trim="supplierForm.delivery" required maxlength="64" placeholder="เช่น 2 วัน" /></label>
        <button class="button secondary" type="submit" :disabled="loading">บันทึกซัพพลายเออร์</button>
      </form>
      <form class="workflow-form" @submit.prevent="linkProduct">
        <label>ซัพพลายเออร์<select v-model="linkForm.supplier_id" required><option value="">เลือกซัพพลายเออร์</option><option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">{{ supplier.name }}</option></select></label>
        <label>สินค้าที่จำหน่าย<select v-model="linkForm.product_sku" required><option value="">เลือกสินค้า</option><option v-for="product in products" :key="product.sku" :value="product.sku">{{ product.sku }} — {{ product.name }}</option></select></label>
        <button class="button secondary" type="submit" :disabled="loading">ผูกซัพพลายเออร์กับสินค้า</button>
      </form>
    </section>

    <section class="panel workflow-section">
      <h2>สร้างใบสั่งซื้อ</h2>
      <div class="workflow-form">
        <label>ชื่อผู้ดำเนินการ<input v-model.trim="actor" maxlength="120" placeholder="ชื่อที่ใช้บันทึกประวัติ" /></label>
        <label>ซัพพลายเออร์
          <select v-model="orderForm.supplier_id"><option value="">เลือกซัพพลายเออร์</option><option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">{{ supplier.name }}</option></select>
        </label>
      </div>
      <div class="workflow-form">
        <label>สินค้า
          <select v-model="lineForm.product_sku"><option value="">เลือกสินค้า</option><option v-for="product in products" :key="product.sku" :value="product.sku">{{ product.sku }} — {{ product.name }}</option></select>
        </label>
        <label>จำนวนที่สั่ง<input v-model.number="lineForm.quantity" type="number" min="1" step="1" /></label>
        <button class="button secondary" type="button" @click="addLine">เพิ่มรายการ</button>
      </div>
      <table v-if="orderForm.lines.length" class="data-table">
        <thead><tr><th>SKU</th><th>จำนวน</th><th></th></tr></thead>
        <tbody><tr v-for="line in orderForm.lines" :key="line.product_sku"><td>{{ line.product_sku }}</td><td>{{ line.quantity }}</td><td><button class="button secondary" type="button" @click="removeLine(line.product_sku)">ลบ</button></td></tr></tbody>
      </table>
      <button class="button primary" type="button" :disabled="loading" @click="createOrder">สร้างใบสั่งซื้อ (ฉบับร่าง)</button>
    </section>

    <section class="master-detail workflow-section">
      <div class="list-column">
        <h2>ใบสั่งซื้อ</h2>
        <p v-if="!orders.length" class="muted">ยังไม่มีใบสั่งซื้อ</p>
        <button v-for="order in orders" :key="order.id" class="customer-card" :class="{ selected: order.id === selectedId }" @click="selectOrder(order.id)">
          <strong>{{ order.id.slice(0, 8) }} · {{ suppliers.find(item => item.id === order.supplier_id)?.name || order.supplier_id }}</strong>
          <small>สถานะ: {{ order.status }} · {{ order.lines.length }} รายการ</small>
        </button>
      </div>
      <div v-if="selectedOrder" class="detail-card">
        <div class="detail-heading"><div><span class="code-tag">{{ selectedOrder.id }}</span><h2>ใบสั่งซื้อ</h2><p>สถานะ: {{ selectedOrder.status }} · สร้างโดย {{ selectedOrder.created_by }}</p></div></div>
        <table class="data-table">
          <thead><tr><th>SKU</th><th>สั่ง</th><th>รับแล้ว</th><th>คงเหลือ</th></tr></thead>
          <tbody><tr v-for="line in selectedOrder.lines" :key="line.id"><td>{{ line.product_sku }}</td><td>{{ line.ordered_quantity }}</td><td>{{ line.received_quantity }}</td><td>{{ line.ordered_quantity - line.received_quantity }}</td></tr></tbody>
        </table>
        <button v-if="selectedOrder.status === 'draft'" class="button primary" :disabled="loading" @click="approve">อนุมัติใบสั่งซื้อ</button>
        <div v-if="['approved', 'partially_received'].includes(selectedOrder.status)" class="workflow-receipt">
          <h3>รับสินค้า</h3>
          <label>เลขอ้างอิงใบรับสินค้า<input v-model.trim="receiptReference" maxlength="120" placeholder="เช่น GR-2026-001" /></label>
          <div v-for="line in selectedOrder.lines.filter(item => item.received_quantity < item.ordered_quantity)" :key="line.id" class="workflow-form">
            <span>{{ line.product_sku }} (รับได้อีก {{ line.ordered_quantity - line.received_quantity }})</span>
            <label>จำนวนที่รับ<input v-model.number="receiptQuantities[line.id]" type="number" min="0" :max="line.ordered_quantity - line.received_quantity" step="1" /></label>
          </div>
          <button class="button primary" :disabled="loading" @click="receive">บันทึกการรับและเพิ่ม stock</button>
        </div>
        <h3>ประวัติ</h3>
        <table class="data-table"><thead><tr><th>เวลา</th><th>เหตุการณ์</th><th>ผู้ดำเนินการ</th></tr></thead>
          <tbody><tr v-for="(event, index) in history.events" :key="index"><td>{{ new Date(event.created_at).toLocaleString('th-TH') }}</td><td>{{ event.event }}</td><td>{{ event.actor }}</td></tr></tbody>
        </table>
        <h3>ใบรับสินค้า</h3>
        <p v-if="!history.receipts.length" class="muted">ยังไม่มีการรับสินค้า</p>
        <div v-for="receipt in history.receipts" :key="receipt.id" class="workflow-history">
          <strong>{{ receipt.reference }}</strong> · {{ receipt.received_by }} · {{ new Date(receipt.received_at).toLocaleString('th-TH') }}
          <small v-for="line in receipt.lines" :key="line.order_line_id">{{ line.product_sku }} +{{ line.quantity }}</small>
        </div>
      </div>
    </section>
  </AppShell>
</template>

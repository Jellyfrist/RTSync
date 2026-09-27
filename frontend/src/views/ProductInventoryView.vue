<script setup>
import { onMounted } from 'vue';
import AppShell from '@/components/AppShell.vue';
import SvgIcon from '@/components/SvgIcon.vue';
import { useProductController } from '@/controllers/useProductController.js';
import { formatCurrency } from '@/utils/formatCurrency.js';

const { products, movements, loading, error, message, productForm, query, category,
  categories, filteredProducts, totalStock, totalValue, refresh, createProduct } = useProductController();
onMounted(refresh);
</script>
<template>
  <AppShell placeholder="ค้นหา SKU, รหัสสินค้า, ชื่อสินค้า...">
    <div class="page-title"><div><h1>สินค้าและคลังอุปกรณ์</h1><p>Product Inventory Management</p></div><button class="button secondary" :disabled="loading" @click="refresh">รีเฟรชข้อมูล</button></div>
    <p v-if="error" class="workflow-alert error" role="alert">{{ error }}</p>
    <p v-if="message" class="workflow-alert success-message" role="status">{{ message }}</p>
    <p v-if="loading" class="muted" role="status">กำลังโหลด...</p>
    <section class="kpi-grid">
      <article class="kpi-card"><div><span>สินค้าทั้งหมด</span><strong>{{ products.length }} <small>รายการ</small></strong><em>คงเหลือรวม {{ totalStock }} ชิ้น</em></div><SvgIcon name="box" size="26" /></article>
      <article class="kpi-card"><div><span>มูลค่าสต็อกตามราคาขาย</span><strong>฿{{ formatCurrency(totalValue) }}</strong><em>ยังไม่ใช่มูลค่าทุน</em></div><SvgIcon name="wallet" size="26" /></article>
    </section>
    <section class="panel workflow-section"><h2>เพิ่มสินค้า</h2>
      <form class="workflow-form" @submit.prevent="createProduct">
        <label>SKU<input v-model.trim="productForm.sku" required maxlength="64" /></label>
        <label>ชื่อสินค้า<input v-model.trim="productForm.name" required maxlength="255" /></label>
        <label>หมวดหมู่<input v-model.trim="productForm.category" required maxlength="120" /></label>
        <label>หน่วย<input v-model.trim="productForm.unit" required maxlength="32" /></label>
        <label>จุดสั่งซื้อ<input v-model.number="productForm.reorder_point" type="number" min="0" step="1" required /></label>
        <label>ราคา<input v-model.number="productForm.price" type="number" min="0" step="0.01" required /></label>
        <button class="button primary" type="submit" :disabled="loading">บันทึกสินค้า</button>
      </form><p class="muted">สินค้าใหม่เริ่มต้นที่ 0 ชิ้น และเพิ่มจำนวนผ่านการรับสินค้าในหน้าจัดซื้อ</p>
    </section>
    <section class="panel workflow-section"><div class="panel-toolbar"><h2>สินค้าในคลัง</h2><div class="search-inline"><SvgIcon name="search" /><input v-model="query" placeholder="ค้นหาในตาราง" /></div></div>
      <div class="filter-tabs"><button v-for="item in categories" :key="item" :class="{ selected: category === item }" @click="category = item">{{ item }}</button></div>
      <table class="data-table"><thead><tr><th>SKU</th><th>สินค้า</th><th>หมวดหมู่</th><th>คงเหลือ</th><th>จุดสั่งซื้อ</th><th>ราคา</th></tr></thead>
        <tbody><tr v-for="product in filteredProducts" :key="product.sku"><td class="mono">{{ product.sku }}</td><td><strong>{{ product.name }}</strong></td><td>{{ product.category }}</td><td><span :class="product.stock <= product.reorder_point ? 'warning-tag' : 'success-tag'">{{ product.stock }} {{ product.unit }}</span></td><td>{{ product.reorder_point }}</td><td>฿{{ formatCurrency(product.price) }}</td></tr>
          <tr v-if="!filteredProducts.length"><td colspan="6" class="empty-state">ยังไม่มีสินค้าตามเงื่อนไข</td></tr></tbody></table>
    </section>
    <section class="panel workflow-section"><h2>ประวัติการเคลื่อนไหวสต็อก</h2>
      <table class="data-table"><thead><tr><th>เวลา</th><th>SKU</th><th>จำนวนเปลี่ยน</th><th>ประเภท</th></tr></thead>
        <tbody><tr v-for="movement in movements" :key="movement.id"><td>{{ new Date(movement.created_at).toLocaleString('th-TH') }}</td><td>{{ movement.product_sku }}</td><td>{{ movement.quantity_change > 0 ? '+' : '' }}{{ movement.quantity_change }}</td><td>{{ movement.movement_type === 'issue' ? 'จ่ายออก' : 'รับเข้า' }}</td></tr>
          <tr v-if="!movements.length"><td colspan="4" class="empty-state">ยังไม่มีการเคลื่อนไหวสต็อก</td></tr></tbody></table>
    </section>
  </AppShell>
</template>

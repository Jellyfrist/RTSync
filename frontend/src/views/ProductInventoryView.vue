<script setup>
import { ref, computed } from "vue";
import AppShell from "@/components/AppShell.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import { useSearch } from "@/composables/useSearch";
const products = ref([
  {
    sku: "SP-JA-550M",
    name: "แผงโซลาร์ JA Solar 550W",
    category: "แผงโซลาร์",
    stock: 140,
    price: "฿4,150",
  },
  {
    sku: "INV-HW-5K1P",
    name: "Huawei SUN2000-5KTL",
    category: "อินเวอร์เตอร์",
    stock: 12,
    price: "฿42,900",
  },
  {
    sku: "INV-HW-10K3P",
    name: "Huawei SUN2000-10KTL-M1",
    category: "อินเวอร์เตอร์",
    stock: 6,
    price: "฿58,900",
  },
  {
    sku: "SP-LN-585X",
    name: "Longi Hi-MO 6 585W",
    category: "แผงโซลาร์",
    stock: 84,
    price: "฿4,350",
  },
  {
    sku: "SEN-HW-DTSU",
    name: "Huawei Smart Power Sensor",
    category: "อุปกรณ์วัด",
    stock: 24,
    price: "฿5,200",
  },
]);
const { query, filteredItems } = useSearch(products, [
  "sku",
  "name",
  "category",
]);
const category = ref("ทั้งหมด");
const filteredProducts = computed(() =>
  category.value === "ทั้งหมด"
    ? filteredItems.value
    : filteredItems.value.filter((item) => item.category === category.value),
);
</script>
<template>
  <AppShell placeholder="ค้นหา SKU, รหัสสินค้า, ชื่อสินค้า..."
    ><div class="page-title">
      <div>
        <h1>สินค้าและคลังอุปกรณ์</h1>
        <p>Product Inventory Management</p>
      </div>
      <button class="button primary"><SvgIcon name="plus" />เพิ่มสินค้า</button>
    </div>
    <section class="kpi-grid">
      <article class="kpi-card">
        <div>
          <span>สินค้าทั้งหมด</span><strong>148 <small>รายการ</small></strong
          ><em>พร้อมจำหน่าย 142 รายการ</em>
        </div>
        <SvgIcon name="box" size="26" />
      </article>
      <article class="kpi-card">
        <div>
          <span>มูลค่าสินค้าคงคลัง</span><strong>฿2.84M</strong
          ><em>อัปเดตล่าสุดวันนี้</em>
        </div>
        <SvgIcon name="wallet" size="26" />
      </article>
    </section>
    <section class="panel">
      <div class="panel-toolbar">
        <div class="filter-tabs">
          <button
            v-for="item in [
              'ทั้งหมด',
              'แผงโซลาร์',
              'อินเวอร์เตอร์',
              'อุปกรณ์วัด',
            ]"
            :key="item"
            :class="{ selected: category === item }"
            @click="category = item"
          >
            {{ item }}
          </button>
        </div>
        <div class="search-inline">
          <SvgIcon name="search" /><input
            v-model="query"
            placeholder="ค้นหาในตาราง"
          />
        </div>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>SKU</th>
            <th>สินค้า</th>
            <th>หมวดหมู่</th>
            <th>คงเหลือ</th>
            <th>ราคา</th>
            <th>จัดการ</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in filteredProducts" :key="product.sku">
            <td class="mono">{{ product.sku }}</td>
            <td>
              <strong>{{ product.name }}</strong>
            </td>
            <td>{{ product.category }}</td>
            <td>
              <span :class="product.stock < 10 ? 'warning-tag' : 'success-tag'"
                >{{ product.stock }} รายการ</span
              >
            </td>
            <td class="mono">{{ product.price }}</td>
            <td>
              <button class="icon-button" title="แก้ไข">
                <SvgIcon name="edit" />
              </button>
            </td>
          </tr>
        </tbody>
      </table></section
  ></AppShell>
</template>

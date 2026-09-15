// ไฟล์นี้เป็นตัวกลางเรียก API ของสินค้าและคลังสินค้า
import { request } from "./httpClient";

// ปรับชื่อข้อมูลจาก backend ให้ตรงกับรูปแบบที่คอมโพเนนต์ใช้
const normalizeProduct = (product) => ({
  ...product,
  reorderPoint: product.reorderPoint ?? product.reorder_point,
});

export const inventoryApi = {
  // ดึงรายการสินค้า
  getProducts: async () =>
    (await request("/inventory/products")).map(normalizeProduct),
  // ดึงข้อมูลสรุปคลัง
  getSummary: () => request("/inventory/summary"),
  // เพิ่มสินค้าใหม่
  createProduct: async (product) =>
    normalizeProduct(
      await request("/inventory/products", {
        method: "POST",
        body: JSON.stringify(product),
      }),
    ),
  // แก้ไขข้อมูลสินค้า
  updateProduct: async (sku, product) =>
    normalizeProduct(
      await request(`/inventory/products/${encodeURIComponent(sku)}`, {
        method: "PUT",
        body: JSON.stringify(product),
      }),
    ),
  // บันทึกการเติม Stock
  receiveStock: async (sku, quantity) =>
    normalizeProduct(
      await request(`/inventory/products/${encodeURIComponent(sku)}/receive`, {
        method: "POST",
        body: JSON.stringify({ quantity }),
      }),
    ),
};

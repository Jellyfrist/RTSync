// ไฟล์นี้เป็นตัวกลางเรียก API ของสินค้าและคลังสินค้า
import { isMockEnabled, request } from "./httpClient";
import { mockDb } from "./mockDb";
import { appendCostLot } from "./pricingPolicy";

// ปรับชื่อข้อมูลจาก backend ให้ตรงกับรูปแบบที่คอมโพเนนต์ใช้
const normalizeProduct = (product) => {
  const stock = Number(product.stock ?? 0);
  const reorderPoint = Number(
    product.reorderPoint ?? product.reorder_point ?? 0,
  );
  return {
    ...product,
    stock,
    reorderPoint,
    costPrice: product.costPrice ?? product.cost_price,
    salePrice: product.salePrice ?? product.sale_price,
    status: stock <= reorderPoint ? "ต้องสั่งเพิ่ม" : "พร้อมขาย",
  };
};

export const inventoryApi = {
  // ดึงหมวดหมู่สินค้าจากฐานข้อมูล
  getCategories: async () => {
    try {
      return await request("/inventory/categories");
    } catch (error) {
      if (!isMockEnabled()) throw error;
      return mockDb.get("categories");
    }
  },
  // เพิ่มหมวดหมู่สินค้าใหม่
  createCategory: async (name) => {
    try {
      return await request("/inventory/categories", {
        method: "POST",
        body: JSON.stringify({ name }),
      });
    } catch (error) {
      if (!isMockEnabled()) throw error;
      const category = {
        category_id: `CAT-${String(mockDb.get("categories").length + 1).padStart(3, "0")}`,
        name,
      };
      mockDb.insert("categories", category);
      return category;
    }
  },
  // ดึงรายการสินค้า
  getProducts: async () => {
    try {
      return (await request("/inventory/products")).map(normalizeProduct);
    } catch (error) {
      if (!isMockEnabled()) throw error;
      return mockDb.get("products").map(normalizeProduct);
    }
  },
  // ดึงข้อมูลสรุปคลัง
  getSummary: async () => {
    try {
      return await request("/inventory/summary");
    } catch (error) {
      if (!isMockEnabled()) throw error;
      return {
        total_products: mockDb.get("products").length,
        total_stock: mockDb
          .get("products")
          .reduce((sum, product) => sum + product.stock, 0),
        low_stock: mockDb
          .get("products")
          .filter((product) => product.stock <= product.reorderPoint).length,
      };
    }
  },
  // เพิ่มสินค้าใหม่
  createProduct: async (product) => {
    try {
      return normalizeProduct(
        await request("/inventory/products", {
          method: "POST",
          body: JSON.stringify(product),
        }),
      );
    } catch (error) {
      if (!isMockEnabled()) throw error;
      const record = normalizeProduct({
        ...product,
        status:
          product.stock <= product.reorderPoint ? "ต้องสั่งเพิ่ม" : "พร้อมขาย",
      });
      mockDb.insert("products", record);
      return record;
    }
  },
  // แก้ไขข้อมูลสินค้า
  updateProduct: async (sku, product) => {
    try {
      return normalizeProduct(
        await request(`/inventory/products/${encodeURIComponent(sku)}`, {
          method: "PUT",
          body: JSON.stringify(product),
        }),
      );
    } catch (error) {
      if (!isMockEnabled()) throw error;
      const record = normalizeProduct({
        ...product,
        sku,
        status:
          product.stock <= product.reorderPoint ? "ต้องสั่งเพิ่ม" : "พร้อมขาย",
      });
      mockDb.update("products", (item) => item.sku === sku, record);
      return record;
    }
  },
  // บันทึกการเติม Stock
  receiveStock: async (sku, quantity, unitCost) => {
    try {
      return normalizeProduct(
        await request(
          `/inventory/products/${encodeURIComponent(sku)}/receive`,
          {
            method: "POST",
            body: JSON.stringify({ quantity, unit_cost: unitCost }),
          },
        ),
      );
    } catch (error) {
      // In production, never fake a successful stock receipt if the API failed.
      // Only the intentionally enabled offline demo may update mock records.
      if (!isMockEnabled()) throw error;
      const product = mockDb.get("products").find((item) => item.sku === sku);
      const record = appendCostLot(
        {
          ...product,
          stock: Number(product?.stock || 0) + Number(quantity || 0),
        },
        quantity,
        Number(unitCost ?? product?.costPrice ?? product?.price ?? 0),
      );
      record.status =
        record.stock <= record.reorderPoint ? "ต้องสั่งเพิ่ม" : "พร้อมขาย";
      mockDb.update("products", (item) => item.sku === sku, record);
      return normalizeProduct(record);
    }
  },
};

// ไฟล์นี้รวม API ของงานขาย นัดหมายติดตั้ง และบริการหลังการขาย
import { isMockEnabled, request } from "./httpClient";
import { mockDb } from "./mockDb";
import { inventoryApi } from "./inventoryApi";

const withFallback = (path, fallback) => async () => {
  try {
    return await request(path);
  } catch (error) {
    if (!isMockEnabled()) throw error;
    return fallback.map((item) => ({ ...item }));
  }
};

export const operationsApi = {
  // ดึงสินค้าแนะนำสำหรับใบเสนอราคา
  getCatalog: async () => {
    try {
      // Use the real product catalog rather than the unrelated operations collection.
      // This keeps quotation product options aligned with Inventory/Supabase.
      return (await inventoryApi.getProducts()).map((product) => ({
        ...product,
        price: Number(product.salePrice ?? product.price ?? 0),
      }));
    } catch (error) {
      if (!isMockEnabled()) throw error;
      return mockDb.get("catalog");
    }
  },
  // ดึงนัดหมายติดตั้ง
  getAppointments: async () => {
    try {
      return await request("/operations/appointments");
    } catch (error) {
      if (!isMockEnabled()) throw error;
      return mockDb.get("appointments");
    }
  },
  // ดึงใบงานบริการ
  getServiceTickets: async () => {
    try {
      return await request("/operations/service-tickets");
    } catch (error) {
      if (!isMockEnabled()) throw error;
      return mockDb.get("serviceTickets");
    }
  },
  getSales: () => withFallback("/operations/sales", mockDb.get("sales"))(),
  getQuotations: () => withFallback("/operations/quotations", mockDb.get("quotations"))(),
  getPurchaseOrders: () => withFallback("/operations/purchaseOrders", mockDb.get("purchaseOrders"))(),
  getFuelClaims: () => withFallback("/operations/fuelClaims", mockDb.get("fuelClaims"))(),
  create: (collection, payload) => request(`/operations/${collection}`, { method: "POST", body: JSON.stringify(payload) }),
  update: (collection, id, payload) => request(`/operations/${collection}/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(payload) }),
};

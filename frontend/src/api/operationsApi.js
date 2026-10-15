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
      // Keep the cost basis in price and expose the offer price separately.
      // Replacing price with the sale price makes margin previews use the
      // offer itself as its cost basis.
      return (await inventoryApi.getProducts()).map((product) => {
        const costPrice = Number(
          product.costPrice ?? product.cost_price ?? product.price ?? 0,
        );
        const salePrice = Number(
          product.salePrice ?? product.sale_price ?? product.price ?? 0,
        );
        return { ...product, costPrice, salePrice };
      });
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
      return await request("/operations/serviceTickets");
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

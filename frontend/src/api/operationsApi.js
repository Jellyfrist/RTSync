// ไฟล์นี้รวม API ของงานขาย นัดหมายติดตั้ง และบริการหลังการขาย
import { isMockEnabled, request } from "./httpClient";
import { mockDb } from "./mockDb";

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
      return await request("/operations/catalog");
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
  getPurchaseOrders: () => withFallback("/operations/purchaseOrders", mockDb.get("purchaseOrders"))(),
  getFuelClaims: () => withFallback("/operations/fuelClaims", mockDb.get("fuelClaims"))(),
  create: (collection, payload) => request(`/operations/${collection}`, { method: "POST", body: JSON.stringify(payload) }),
  update: (collection, id, payload) => request(`/operations/${collection}/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(payload) }),
};

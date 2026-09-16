// ไฟล์นี้รวม API ของงานขาย นัดหมายติดตั้ง และบริการหลังการขาย
import { request } from "./httpClient";
import { mockDb } from "./mockDb";

const withFallback = (path, fallback) => async () => {
  try {
    return await request(path);
  } catch {
    return fallback.map((item) => ({ ...item }));
  }
};

export const operationsApi = {
  // ดึงสินค้าแนะนำสำหรับใบเสนอราคา
  getCatalog: async () => {
    try { return await request("/operations/catalog"); } catch { return mockDb.get("catalog"); }
  },
  // ดึงนัดหมายติดตั้ง
  getAppointments: async () => {
    try { return await request("/operations/appointments"); } catch { return mockDb.get("appointments"); }
  },
  // ดึงใบงานบริการ
  getServiceTickets: async () => {
    try { return await request("/operations/service-tickets"); } catch { return mockDb.get("serviceTickets"); }
  },
  getSales: () => Promise.resolve(mockDb.get("sales")),
  getPurchaseOrders: () => Promise.resolve(mockDb.get("purchaseOrders")),
  getFuelClaims: () => Promise.resolve(mockDb.get("fuelClaims")),
};

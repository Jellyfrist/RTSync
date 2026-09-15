// ไฟล์นี้รวม API ของงานขาย นัดหมายติดตั้ง และบริการหลังการขาย
import { request } from "./httpClient";

export const operationsApi = {
  // ดึงสินค้าแนะนำสำหรับใบเสนอราคา
  getCatalog: () => request("/operations/catalog"),
  // ดึงนัดหมายติดตั้ง
  getAppointments: () => request("/operations/appointments"),
  // ดึงใบงานบริการ
  getServiceTickets: () => request("/operations/service-tickets"),
};

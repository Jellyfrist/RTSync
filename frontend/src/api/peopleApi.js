// ไฟล์นี้รวม API ของลูกค้า ซัพพลายเออร์ และพนักงาน
import { request } from "./httpClient";

export const peopleApi = {
  // ดึงรายชื่อลูกค้า
  getCustomers: () => request("/customers"),
  // ดึงรายชื่อซัพพลายเออร์
  getSuppliers: () => request("/suppliers"),
  // ดึงพนักงานและปรับชื่อฟิลด์ให้ตรงกับหน้าค่าจ้าง
  getEmployees: async () =>
    (await request("/employees")).map((employee) => ({
      ...employee,
      initials: employee.initials || employee.name.slice(0, 2),
      otHours: employee.overtime_hours,
      otRate: employee.overtime_rate,
    })),
};

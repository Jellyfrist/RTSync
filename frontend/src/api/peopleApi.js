// ไฟล์นี้รวม API ของลูกค้า ซัพพลายเออร์ และพนักงาน
import { request } from "./httpClient";
import { mockDb } from "./mockDb";

// ข้อมูลตัวอย่างสำหรับ preview UI กรณีเปิดเฉพาะ frontend โดยยังไม่ได้รัน API
const normalizeEmployee = (employee) => ({
  ...employee,
  initials: employee.initials || employee.name.slice(0, 2),
  otHours: employee.otHours ?? employee.overtime_hours,
  otRate: employee.otRate ?? employee.overtime_rate,
});
const normalizeSupplier = (supplier) => ({
  ...supplier,
  contactName: supplier.contactName ?? supplier.contact_name ?? "",
  contactPhone: supplier.contactPhone ?? supplier.contact_phone ?? "",
  contactEmail: supplier.contactEmail ?? supplier.contact_email ?? "",
  paymentTerms: supplier.paymentTerms ?? supplier.payment_terms ?? "ยังไม่ระบุ",
});

export const peopleApi = {
  // ดึงรายชื่อลูกค้า
  getCustomers: async () => {
    try {
      return await request("/customers");
    } catch {
      return mockDb.get("customers");
    }
  },
  // ดึงรายชื่อซัพพลายเออร์
  getSuppliers: async () => {
    try {
      return (await request("/suppliers")).map(normalizeSupplier);
    } catch {
      return mockDb.get("suppliers").map(normalizeSupplier);
    }
  },
  // ดึงหมวดหมู่ซัพพลายเออร์จากฐานข้อมูล
  getSupplierCategories: async () => {
    try {
      return await request("/suppliers/categories");
    } catch {
      return mockDb.get("supplierCategories");
    }
  },
  // เพิ่มหมวดหมู่ซัพพลายเออร์ใหม่ลงฐานข้อมูล
  createSupplierCategory: async (name) => {
    try {
      return await request("/suppliers/categories", {
        method: "POST",
        body: JSON.stringify({ name }),
      });
    } catch {
      const category = {
        category_id: `SCAT-${String(mockDb.get("supplierCategories").length + 1).padStart(3, "0")}`,
        name,
      };
      mockDb.insert("supplierCategories", category);
      return category;
    }
  },
  // เพิ่มซัพพลายเออร์ใหม่ลงฐานข้อมูล
  createSupplier: async (supplier) => {
    try {
      return await request("/suppliers", {
        method: "POST",
        body: JSON.stringify(supplier),
      });
    } catch {
      const record = normalizeSupplier({
        ...supplier,
        id: `SUP-TH-${String(mockDb.get("suppliers").length + 1).padStart(3, "0")}`,
        sku_count: 0,
      });
      mockDb.insert("suppliers", record);
      return record;
    }
  },
  // ดึงพนักงานและปรับชื่อฟิลด์ให้ตรงกับหน้าค่าจ้าง
  getEmployees: async () => {
    try {
      return (await request("/employees")).map(normalizeEmployee);
    } catch {
      return mockDb.get("employees").map(normalizeEmployee);
    }
  },
};

// ไฟล์นี้รวม API ของลูกค้า ซัพพลายเออร์ และพนักงาน
import { isMockEnabled, request } from "./httpClient";
import { mockDb } from "./mockDb";

// ข้อมูลตัวอย่างสำหรับ preview UI กรณีเปิดเฉพาะ frontend โดยยังไม่ได้รัน API
const normalizeEmployee = (employee) => ({
  ...employee,
  initials: employee.initials || employee.name.slice(0, 2),
  otHours: employee.otHours ?? employee.overtime_hours,
  otRate: employee.otRate ?? employee.overtime_rate,
  startDate: employee.startDate ?? employee.start_date,
  allowance: Number(employee.allowance ?? 0),
  deduction: Number(employee.deduction ?? 0),
});
const normalizeCustomer = (customer) => ({
  ...customer,
  type: customer.type ?? customer.customer_type,
  email: customer.email ?? "",
  taxId: customer.taxId ?? customer.tax_id ?? "",
  contactName: customer.contactName ?? customer.contact_name ?? "",
  address: customer.address || {},
});
const normalizeSupplier = (supplier) => ({
  ...supplier,
  contactName: supplier.contactName ?? supplier.contact_name ?? "",
  contactPhone: supplier.contactPhone ?? supplier.contact_phone ?? "",
  contactEmail: supplier.contactEmail ?? supplier.contact_email ?? "",
  paymentTerms: supplier.paymentTerms ?? supplier.payment_terms ?? "ยังไม่ระบุ",
});

const supplierPayload = (supplier) => ({
  ...supplier,
  contact_name: supplier.contact_name ?? supplier.contactName ?? "",
  contact_phone: supplier.contact_phone ?? supplier.contactPhone ?? "",
  contact_email: supplier.contact_email ?? supplier.contactEmail ?? "",
  payment_terms: supplier.payment_terms ?? supplier.paymentTerms ?? "",
});

const employeePayload = (employee) => ({
  ...employee,
  overtime_hours: employee.overtime_hours ?? employee.otHours ?? 0,
  overtime_rate: employee.overtime_rate ?? employee.otRate ?? 0,
  start_date: employee.start_date ?? employee.startDate ?? null,
});

export const peopleApi = {
  // ดึงรายชื่อลูกค้า
  getCustomers: async () => {
    try {
      return (await request("/customers")).map(normalizeCustomer);
    } catch (error) {
      if (!isMockEnabled()) throw error;
      return mockDb.get("customers").map(normalizeCustomer);
    }
  },
  // ดึงรายชื่อซัพพลายเออร์
  getSuppliers: async () => {
    try {
      return (await request("/suppliers")).map(normalizeSupplier);
    } catch (error) {
      if (!isMockEnabled()) throw error;
      return mockDb.get("suppliers").map(normalizeSupplier);
    }
  },
  // ดึงหมวดหมู่ซัพพลายเออร์จากฐานข้อมูล
  getSupplierCategories: async () => {
    try {
      return await request("/suppliers/categories");
    } catch (error) {
      if (!isMockEnabled()) throw error;
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
    } catch (error) {
      if (!isMockEnabled()) throw error;
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
        body: JSON.stringify(supplierPayload(supplier)),
      });
    } catch (error) {
      if (!isMockEnabled()) throw error;
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
    } catch (error) {
      if (!isMockEnabled()) throw error;
      return mockDb.get("employees").map(normalizeEmployee);
    }
  },
  createCustomer: (customer) =>
    request("/customers", { method: "POST", body: JSON.stringify({ ...customer, customer_type: customer.customer_type ?? customer.type }) }),
  updateCustomer: (id, customer) =>
    request(`/customers/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify({ ...customer, customer_type: customer.customer_type ?? customer.type }) }),
  updateSupplier: (id, supplier) =>
    request(`/suppliers/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(supplierPayload(supplier)) }),
  linkProduct: (supplierId, sku) =>
    request(`/suppliers/${encodeURIComponent(supplierId)}/products/${encodeURIComponent(sku)}`, { method: "POST" }),
  unlinkProduct: (supplierId, sku) =>
    request(`/suppliers/${encodeURIComponent(supplierId)}/products/${encodeURIComponent(sku)}`, { method: "DELETE" }),
  createEmployee: (employee) =>
    request("/employees", { method: "POST", body: JSON.stringify(employeePayload(employee)) }),
  updateEmployee: (id, employee) =>
    request(`/employees/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(employeePayload(employee)) }),
};

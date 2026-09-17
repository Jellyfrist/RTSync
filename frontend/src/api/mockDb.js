// Mock database กลางของโหมด demo: ทุกหน้าจออ่าน/เขียนข้อมูลชุดเดียวกันผ่านไฟล์นี้
import {
  MOCK_APPOINTMENTS,
  MOCK_CATALOG,
  MOCK_CATEGORIES,
  MOCK_CUSTOMERS,
  MOCK_CUSTOMER_TYPES,
  MOCK_EMPLOYEES,
  MOCK_FUEL_CLAIMS,
  MOCK_PURCHASE_ORDERS,
  MOCK_SALES,
  MOCK_SERVICE_TICKETS,
  MOCK_SUPPLIER_CATEGORIES,
  MOCK_SUPPLIERS,
  MOCK_PRODUCTS,
} from "./mockData";

const DB_KEY = "rtsync.mockDb.v1";
const seed = {
  categories: MOCK_CATEGORIES,
  supplierCategories: MOCK_SUPPLIER_CATEGORIES,
  suppliers: MOCK_SUPPLIERS,
  products: MOCK_PRODUCTS,
  customers: MOCK_CUSTOMERS,
  customerTypes: MOCK_CUSTOMER_TYPES,
  employees: MOCK_EMPLOYEES,
  employeeRoles: [
    ...new Set(MOCK_EMPLOYEES.map((employee) => employee.role).filter(Boolean)),
  ],
  inventoryStatuses: ["ทั้งหมด", "พร้อมขาย", "ต้องสั่งเพิ่ม"],
  customerStatuses: ["ทั้งหมด", "ชำระครบถ้วน", "รอนัดตรวจเช็ก", "รอเปิดบัญชี"],
  claimStatuses: [
    "ทั้งหมด",
    "รอตรวจสอบ",
    "อนุมัติแล้ว",
    "รอเอกสาร",
    "ไม่อนุมัติ",
  ],
  paymentStatuses: [
    "ทั้งหมด",
    "ชำระเรียบร้อย",
    "ชำระมัดจำ",
    "รอชำระมัดจำ",
    "รอชำระส่วนที่เหลือ",
  ],
  orderStatuses: [
    "รอการยืนยัน",
    "ยืนยันคำสั่งซื้อ",
    "กำลังเตรียมสินค้า",
    "จัดส่งแล้ว",
    "ปิดการขาย",
    "ปฏิเสธการสั่งซื้อ",
  ],
  purchaseOrderStatuses: [
    "รอดำเนินการ",
    "กำลังจัดซื้อ",
    "สั่งซื้อแล้ว",
    "รอของมาส่ง",
    "รับของเรียบร้อยแล้ว",
    "สำเร็จ",
  ],
  appointmentTimes: ["09:00–12:00", "13:00–16:00", "09:00–15:00", "กำหนดเอง"],
  appointmentStatuses: [
    "ทั้งหมด",
    "รอยืนยัน",
    "ยืนยันแล้ว",
    "เตรียมอุปกรณ์",
    "กำลังติดตั้ง",
    "เสร็จสิ้น",
  ],
  serviceStatuses: [
    "ทั้งหมด",
    "รอเปิดงาน",
    "รอมอบหมาย",
    "นัดหมายแล้ว",
    "ยืนยันแล้ว",
    "กำลังเข้าบริการ",
    "เสร็จสิ้น",
  ],
  servicePriorities: ["ปกติ", "สูง", "เร่งด่วน"],
  serviceTypes: [
    { value: "installation", label: "ค่าติดตั้งระบบ", defaultPrice: 8500 },
    { value: "after-sales", label: "ค่าบริการหลังการขาย", defaultPrice: 1500 },
    { value: "transport", label: "ค่าขนส่งและจัดส่ง", defaultPrice: 1200 },
  ],
  catalog: MOCK_CATALOG,
  sales: MOCK_SALES,
  quotations: [],
  purchaseOrders: MOCK_PURCHASE_ORDERS,
  appointments: MOCK_APPOINTMENTS,
  serviceTickets: MOCK_SERVICE_TICKETS,
  fuelClaims: MOCK_FUEL_CLAIMS,
  fuelSources: ["ติดตั้ง", "บริการหลังการขาย"],
};

const clone = (value) => JSON.parse(JSON.stringify(value));
let memoryDb = clone(seed);

function readDb() {
  if (typeof localStorage === "undefined") return memoryDb;
  try {
    const stored = JSON.parse(localStorage.getItem(DB_KEY) || "null");
    if (stored && typeof stored === "object") {
      memoryDb = { ...clone(seed), ...stored };
      // ฐาน demo รุ่นแรกอาจเคยบันทึกค่าว่างไว้ก่อนมี seed รายการสั่งซื้อ
      if (
        !Array.isArray(memoryDb.purchaseOrders) ||
        memoryDb.purchaseOrders.length === 0
      ) {
        memoryDb.purchaseOrders = clone(seed.purchaseOrders);
      }
      // catalog คือรายการสำหรับเสนอราคา จึงต้องเริ่มด้วยราคาขาย ไม่ใช่ราคาทุน
      if (Array.isArray(memoryDb.catalog)) {
        const seedCatalogBySku = new Map(
          seed.catalog.map((item) => [item.sku, item]),
        );
        memoryDb.catalog = memoryDb.catalog.map((item) => {
          const canonical = seedCatalogBySku.get(item.sku);
          if (!canonical) return item;
          return {
            ...item,
            costPrice: item.costPrice ?? canonical.costPrice,
            costLots: item.costLots ?? canonical.costLots,
            salePrice: item.salePrice ?? canonical.salePrice,
            price: canonical.salePrice ?? item.salePrice ?? item.price,
          };
        });
        writeDb(memoryDb);
      }
      // เติมฟิลด์ติดต่อและเงื่อนไขการชำระเงินให้ซัพพลายเออร์จากฐาน demo รุ่นเก่า
      if (Array.isArray(memoryDb.suppliers)) {
        const seedSupplierById = new Map(
          seed.suppliers.map((item) => [item.id, item]),
        );
        memoryDb.suppliers = memoryDb.suppliers.map((item) => {
          const canonical = seedSupplierById.get(item.id);
          if (!canonical) return item;
          return {
            ...canonical,
            ...item,
            contactName: item.contactName ?? canonical.contactName,
            contactPhone: item.contactPhone ?? canonical.contactPhone,
            contactEmail: item.contactEmail ?? canonical.contactEmail,
            paymentTerms: item.paymentTerms ?? canonical.paymentTerms,
          };
        });
        writeDb(memoryDb);
      }
      // เติมข้อมูลติดต่อและที่อยู่ลูกค้าจาก seed ให้ฐาน demo รุ่นเก่ามีโครงสร้างเดียวกัน
      if (Array.isArray(memoryDb.customers)) {
        const seedCustomerByCode = new Map(
          seed.customers.map((item) => [item.code, item]),
        );
        memoryDb.customers = memoryDb.customers.map((item) => {
          const canonical = seedCustomerByCode.get(item.code);
          return {
            ...(canonical || {}),
            ...item,
            contactName: item.contactName ?? canonical?.contactName ?? "",
            email: item.email ?? canonical?.email ?? "",
            taxId: item.taxId ?? canonical?.taxId ?? "",
            address: item.address ?? canonical?.address ?? {},
          };
        });
        writeDb(memoryDb);
      }
      // เติมชุดสาธิตนัดหมายของวันนี้ลงฐานเดิมที่เคยบันทึกไว้แล้ว
      // เพื่อให้หน้า calendar แสดงตัวอย่าง 5 งานในวันเดียวกันได้ทันที
      if (Array.isArray(memoryDb.appointments)) {
        const demoAppointments = seed.appointments.filter((item) =>
          item.id.startsWith("INS-DEMO-"),
        );
        const storedDemoIds = new Set(
          memoryDb.appointments
            .filter((item) => item.id?.startsWith("INS-DEMO-"))
            .map((item) => item.id),
        );
        const todayDemoIds = new Set(demoAppointments.map((item) => item.id));
        memoryDb.appointments = memoryDb.appointments.filter(
          (item) =>
            !item.id?.startsWith("INS-DEMO-") || todayDemoIds.has(item.id),
        );
        demoAppointments.forEach((item) => {
          if (!storedDemoIds.has(item.id))
            memoryDb.appointments.push(clone(item));
        });
        writeDb(memoryDb);
      }
    } else {
      const legacyKeys = {
        sales: "rtsync.sales",
        quotations: "rtsync.quotations",
        purchaseOrders: "rtsync.purchaseOrders",
      };
      const migrated = clone(seed);
      Object.entries(legacyKeys).forEach(([collection, key]) => {
        try {
          const legacyRecords = JSON.parse(localStorage.getItem(key) || "null");
          if (Array.isArray(legacyRecords) && legacyRecords.length)
            migrated[collection] = legacyRecords;
        } catch {
          // ข้ามข้อมูล legacy ที่อ่านไม่ได้ แล้วใช้ seed ที่ปลอดภัยแทน
        }
      });
      writeDb(migrated);
    }
  } catch {
    memoryDb = clone(seed);
  }
  return memoryDb;
}

function writeDb(db) {
  memoryDb = db;
  if (typeof localStorage !== "undefined") {
    localStorage.setItem(DB_KEY, JSON.stringify(db));
  }
}

export const mockDb = {
  get(collection) {
    const db = readDb();
    if (
      collection === "purchaseOrders" &&
      (!Array.isArray(db[collection]) || db[collection].length === 0)
    ) {
      db[collection] = clone(seed.purchaseOrders);
      writeDb(db);
    }
    return clone(db[collection] || []);
  },
  set(collection, records) {
    const db = readDb();
    db[collection] = clone(records);
    writeDb(db);
    return clone(db[collection]);
  },
  insert(collection, record) {
    const records = this.get(collection);
    records.unshift(clone(record));
    return this.set(collection, records);
  },
  update(collection, predicate, updates) {
    const records = this.get(collection);
    const record = records.find(predicate);
    if (record) Object.assign(record, updates);
    this.set(collection, records);
    return record ? clone(record) : null;
  },
  reset() {
    writeDb(clone(seed));
  },
};

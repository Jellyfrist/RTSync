// Mock database กลางของโหมด demo: ทุกหน้าจออ่าน/เขียนข้อมูลชุดเดียวกันผ่านไฟล์นี้
import {
  MOCK_APPOINTMENTS,
  MOCK_CATALOG,
  MOCK_CATEGORIES,
  MOCK_CUSTOMERS,
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
  employees: MOCK_EMPLOYEES,
  catalog: MOCK_CATALOG,
  sales: MOCK_SALES,
  quotations: [],
  purchaseOrders: MOCK_PURCHASE_ORDERS,
  appointments: MOCK_APPOINTMENTS,
  serviceTickets: MOCK_SERVICE_TICKETS,
  fuelClaims: MOCK_FUEL_CLAIMS,
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
      if (!Array.isArray(memoryDb.purchaseOrders) || memoryDb.purchaseOrders.length === 0) {
        memoryDb.purchaseOrders = clone(seed.purchaseOrders);
      }
    } else {
      const legacyKeys = { sales: "rtsync.sales", quotations: "rtsync.quotations", purchaseOrders: "rtsync.purchaseOrders" };
      const migrated = clone(seed);
      Object.entries(legacyKeys).forEach(([collection, key]) => {
        try {
          const legacyRecords = JSON.parse(localStorage.getItem(key) || "null");
          if (Array.isArray(legacyRecords) && legacyRecords.length) migrated[collection] = legacyRecords;
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
    if (collection === "purchaseOrders" && (!Array.isArray(db[collection]) || db[collection].length === 0)) {
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

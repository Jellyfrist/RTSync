// ไฟล์กำหนดเส้นทางและจับคู่ URL กับหน้า Vue ของระบบ
import { createRouter, createWebHistory } from "vue-router";
const CustomerView = () => import("@/views/CustomerView.vue");
const EmployeePayrollView = () => import("@/views/EmployeePayrollView.vue");
const ProductInventoryView = () => import("@/views/ProductInventoryView.vue");
const SalesInstallationView = () => import("@/views/SalesInstallationView.vue");
const SupplierManagementView = () => import("@/views/SupplierManagementView.vue");
const FuelClaimsView = () => import("@/views/FuelClaimsView.vue");

const routes = [
  { path: "/", redirect: "/customers" },
  { path: "/customers", name: "customers", component: CustomerView },
  { path: "/inventory", name: "inventory", component: ProductInventoryView },
  { path: "/suppliers", name: "suppliers", component: SupplierManagementView },
  { path: "/sales", name: "sales", component: SalesInstallationView, props: { initialTab: "sales" } },
  { path: "/installations", name: "installations", component: SalesInstallationView, props: { initialTab: "appointments" } },
  { path: "/service", name: "service", component: SalesInstallationView, props: { initialTab: "service" } },
  { path: "/fuel-claims", name: "fuel-claims", component: FuelClaimsView },
  { path: "/payroll", name: "payroll", component: EmployeePayrollView },
];

// Router กลางของ frontend สำหรับแทนที่ลิงก์ HTML เดิม
export default createRouter({
  history: createWebHistory(),
  routes,
});

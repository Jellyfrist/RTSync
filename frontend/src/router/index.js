// ไฟล์กำหนดเส้นทางและจับคู่ URL กับหน้า Vue ของระบบ
import { createRouter, createWebHistory } from "vue-router";
import { authEnabled, loadAuthStatus, loadCurrentUser } from "@/api/authSession";
const CustomerView = () => import("@/views/CustomerView.vue");
const LoginView = () => import("@/views/LoginView.vue");
const EmployeePayrollView = () => import("@/views/EmployeePayrollView.vue");
const ProductInventoryView = () => import("@/views/ProductInventoryView.vue");
const SalesInstallationView = () => import("@/views/SalesInstallationView.vue");
const SupplierManagementView = () =>
  import("@/views/SupplierManagementView.vue");
const FuelClaimsView = () => import("@/views/FuelClaimsView.vue");

const routes = [
  { path: "/", name: "home-login", component: LoginView },
  { path: "/login", name: "login", component: LoginView },
  { path: "/customers", name: "customers", component: CustomerView },
  { path: "/inventory", name: "inventory", component: ProductInventoryView },
  { path: "/suppliers", name: "suppliers", component: SupplierManagementView },
  {
    path: "/sales",
    name: "sales",
    component: SalesInstallationView,
    props: { initialTab: "sales" },
  },
  {
    path: "/installations",
    name: "installations",
    component: SalesInstallationView,
    props: { initialTab: "appointments" },
  },
  {
    path: "/service",
    name: "service",
    component: SalesInstallationView,
    props: { initialTab: "service" },
  },
  { path: "/fuel-claims", name: "fuel-claims", component: FuelClaimsView },
  { path: "/payroll", name: "payroll", component: EmployeePayrollView },
];

// Router กลางของ frontend สำหรับแทนที่ลิงก์ HTML เดิม
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    if (to.hash) return { el: to.hash, behavior: "smooth" };
    return { top: 0 };
  },
});


// Role gating applies to existing screens only; this adds no business Use Case.
// Business APIs independently validate the verified account session + role.
router.beforeEach(async (to) => {
  const enabled = await loadAuthStatus();
  if (!enabled) return to.path === "/login" ? "/" : true;

  if (to.path === "/" || to.path === "/login") {
    const user = await loadCurrentUser();
    return user ? "/customers" : true;
  }

  const user = await loadCurrentUser();
  if (!user) return { path: "/", query: { returnTo: to.fullPath } };

  if (user.role === "employee" && ["/payroll", "/suppliers"].includes(to.path)) {
    // UC-03-08: from the inventory form Staff may use supplier registration
    // only, not the owner-only supplier management module.
    if (to.path === "/suppliers" && to.query.from === "inventory") return true;
    return { path: "/inventory", query: { forbidden: "1" } };
  }
  return true;
});

export default router;

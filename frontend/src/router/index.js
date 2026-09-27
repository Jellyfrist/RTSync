import { createRouter, createWebHistory } from 'vue-router'
import CustomerView from '@/views/CustomerView.vue'
import EmployeePayrollView from '@/views/EmployeePayrollView.vue'
import ProductInventoryView from '@/views/ProductInventoryView.vue'
import SalesInstallationView from '@/views/SalesInstallationView.vue'
import SupplierManagementView from '@/views/SupplierManagementView.vue'

const routes = [
  { path: '/', redirect: '/customers' },
  { path: '/customers', name: 'customers', component: CustomerView },
  { path: '/inventory', name: 'inventory', component: ProductInventoryView },
  { path: '/suppliers', name: 'suppliers', component: SupplierManagementView },
  { path: '/installations', name: 'installations', component: SalesInstallationView },
  { path: '/payroll', name: 'payroll', component: EmployeePayrollView }
]

// Shared frontend router for replacing the old HTML links.
export default createRouter({
  history: createWebHistory(),
  routes
})

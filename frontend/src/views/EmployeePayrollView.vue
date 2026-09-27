<script setup>
import AppShell from "@/components/AppShell.vue";
import SvgIcon from "@/components/SvgIcon.vue";
import { useEmployeeController } from "@/controllers/useEmployeeController.js";

const { activeId, collapsed, search, visibleEmployees, activeEmployee } = useEmployeeController();
</script>

<template>
  <AppShell placeholder="ค้นหาพนักงาน, รหัสพนักงาน..."
    ><div class="page-title">
      <div>
        <h1>ค่าตอบแทนและ OT พนักงาน</h1>
        <p>Employee Payroll & Overtime Management</p>
      </div>
      <button class="button primary">
        <SvgIcon name="plus" />เพิ่มพนักงาน
      </button>
    </div>
    <section class="kpi-grid four">
      <article class="kpi-card">
        <div>
          <span>พนักงานทั้งหมด</span><strong>24 <small>คน</small></strong>
        </div>
        <SvgIcon name="user" />
      </article>
      <article class="kpi-card">
        <div>
          <span>ชั่วโมง OT รวม</span><strong>186 <small>ชม.</small></strong>
        </div>
        <SvgIcon name="settings" />
      </article>
      <article class="kpi-card warning">
        <div><span>ยอดค่า OT รวม</span><strong>฿84,350</strong></div>
        <SvgIcon name="wallet" />
      </article>
      <article class="kpi-card">
        <div><span>เงินเดือนสุทธิ</span><strong>฿612,450</strong></div>
        <SvgIcon name="wallet" />
      </article>
    </section>
    <section class="payroll-workbench">
      <div class="employee-list" :class="{ collapsed }">
        <div class="panel-toolbar">
          <strong>รายชื่อพนักงาน</strong
          ><button class="icon-button" @click="collapsed = !collapsed">
            <SvgIcon name="grid" />
          </button>
        </div>
        <div class="search-inline" v-if="!collapsed">
          <SvgIcon name="search" /><input
            v-model="search"
            placeholder="ค้นหาพนักงาน"
          />
        </div>
        <button
          v-for="employee in visibleEmployees"
          :key="employee.id"
          class="employee-card"
          :class="{ selected: activeId === employee.id }"
          @click="activeId = employee.id"
        >
          <span class="employee-avatar">{{ employee.initials }}</span
          ><span v-if="!collapsed"
            ><strong>{{ employee.name }}</strong
            ><small>{{ employee.role }}</small
            ><em>OT {{ employee.ot }}</em></span
          >
        </button>
      </div>
      <div class="detail-card" v-if="activeEmployee">
        <div class="detail-heading">
          <div>
            <span class="code-tag">{{ activeEmployee.id }}</span>
            <h2>{{ activeEmployee.name }}</h2>
            <p>{{ activeEmployee.role }}</p>
          </div>
          <button class="button primary">คำนวณเงินเดือน</button>
        </div>
        <div class="info-grid">
          <div>
            <small>เงินเดือนพื้นฐาน</small
            ><strong>{{ activeEmployee.salary }}</strong>
          </div>
          <div>
            <small>ชั่วโมง OT เดือนนี้</small
            ><strong>{{ activeEmployee.ot }}</strong>
          </div>
          <div>
            <small>สถานะรอบเงินเดือน</small
            ><strong class="text-success">รอตรวจสอบ</strong>
          </div>
        </div>
        <h3>รายการค่าตอบแทนประจำเดือน</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>รายการ</th>
              <th>จำนวน</th>
              <th>ยอดเงิน</th>
              <th>สถานะ</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>เงินเดือนพื้นฐาน</td>
              <td>1 งวด</td>
              <td>{{ activeEmployee.salary }}</td>
              <td><span class="success-tag">พร้อมจ่าย</span></td>
            </tr>
            <tr>
              <td>ค่าล่วงเวลา</td>
              <td>{{ activeEmployee.ot }}</td>
              <td>฿3,500.00</td>
              <td><span class="warning-tag">รอตรวจสอบ</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section></AppShell
  >
</template>

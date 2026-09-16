<script setup>
import { computed, ref } from "vue";
import SvgIcon from "@/components/SvgIcon.vue";

const props = defineProps({
  items: { type: Array, default: () => [] },
  mode: { type: String, default: "installation" },
});

const toLocalISO = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};
const todayISO = toLocalISO(new Date());
const initialDate = new Date(`${todayISO}T00:00:00`);
const viewYear = ref(initialDate.getFullYear());
const viewMonth = ref(initialDate.getMonth());
const selectedDate = ref(todayISO);
const weekdayLabels = ["อาทิตย์", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์"];
const monthOptions = Array.from({ length: 12 }, (_, month) => ({
  value: month,
  label: new Intl.DateTimeFormat("th-TH-u-ca-gregory", { month: "long" }).format(
    new Date(2025, month, 1),
  ),
}));
const yearOptions = computed(() => {
  const years = new Set([initialDate.getFullYear(), new Date().getFullYear()]);
  props.items.forEach((item) => {
    if (item.date) years.add(new Date(`${item.date}T00:00:00`).getFullYear());
  });
  return [...years].sort((a, b) => a - b);
});
const monthLabel = computed(() =>
  new Intl.DateTimeFormat("th-TH-u-ca-gregory", { month: "long", year: "numeric" }).format(
    new Date(viewYear.value, viewMonth.value, 1),
  ),
);
const calendarDays = computed(() => {
  const start = new Date(viewYear.value, viewMonth.value, 1).getDay();
  const daysInMonth = new Date(viewYear.value, viewMonth.value + 1, 0).getDate();
  return Array.from({ length: 42 }, (_, index) => {
    const day = index - start + 1;
    if (day < 1 || day > daysInMonth) return { key: `empty-${index}`, empty: true };
    const date = `${viewYear.value}-${String(viewMonth.value + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    return { key: date, date, day };
  });
});
const itemsForDate = computed(() =>
  props.items.filter((item) => item.date === selectedDate.value),
);
const selectedDateLabel = computed(() => {
  return new Intl.DateTimeFormat("th-TH-u-ca-gregory", {
    weekday: "long",
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${selectedDate.value}T00:00:00`));
});
const isInstallation = computed(() => props.mode === "installation");
const itemLabel = computed(() => (isInstallation.value ? "งานติดตั้ง" : "งานบริการ"));
const statusLegend = computed(() =>
  isInstallation.value
    ? [
        { tone: "success", label: "ยืนยันแล้ว / เสร็จสิ้น" },
        { tone: "info", label: "เตรียมอุปกรณ์" },
        { tone: "warning", label: "รอยืนยัน" },
      ]
    : [
        { tone: "success", label: "ยืนยันแล้ว / เสร็จสิ้น" },
        { tone: "info", label: "นัดหมายแล้ว" },
        { tone: "warning", label: "รอมอบหมาย / รอยืนยัน" },
        { tone: "neutral", label: "รอเปิดงาน" },
      ],
);
const dateItems = (date) => props.items.filter((item) => item.date === date);
const selectDate = (date) => {
  if (!date) return;
  selectedDate.value = date;
};
const selectDateInView = () => {
  const prefix = `${viewYear.value}-${String(viewMonth.value + 1).padStart(2, "0")}`;
  const nextDate = props.items.find((item) => item.date?.startsWith(prefix))?.date;
  selectedDate.value = nextDate || `${prefix}-01`;
};
const changeMonth = (offset) => {
  const next = new Date(viewYear.value, viewMonth.value + offset, 1);
  viewYear.value = next.getFullYear();
  viewMonth.value = next.getMonth();
  selectDateInView();
};
const resetMonth = () => {
  viewYear.value = initialDate.getFullYear();
  viewMonth.value = initialDate.getMonth();
  selectedDate.value = todayISO;
};
const statusClass = (status) => {
  if (["เสร็จสิ้น", "ยืนยันแล้ว"].includes(status)) return "success-tag";
  if (["รอยืนยัน", "รอมอบหมาย"].includes(status)) return "warning-tag";
  return "code-tag";
};
const calendarStatusClass = (status) => {
  if (["เสร็จสิ้น", "ยืนยันแล้ว"].includes(status)) return "calendar-status-success";
  if (["รอยืนยัน", "รอมอบหมาย"].includes(status)) return "calendar-status-warning";
  if (["เตรียมอุปกรณ์", "นัดหมายแล้ว"].includes(status)) return "calendar-status-info";
  return "calendar-status-neutral";
};
</script>

<template>
  <div class="operations-calendar">
    <section class="calendar-board" aria-label="ปฏิทินนัดหมายรายเดือน">
      <div class="calendar-toolbar">
        <div>
          <span class="eyebrow">MONTHLY SCHEDULE</span>
          <div class="calendar-month-picker">
            <button class="calendar-nav-button" aria-label="เดือนก่อนหน้า" @click="changeMonth(-1)">
              <SvgIcon name="chevron-left" size="18" />
            </button>
            <select v-model.number="viewMonth" aria-label="เลือกเดือน" @change="selectDateInView">
              <option v-for="month in monthOptions" :key="month.value" :value="month.value">{{ month.label }}</option>
            </select>
            <select v-model.number="viewYear" aria-label="เลือกปี" @change="selectDateInView">
              <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
            </select>
            <button class="calendar-nav-button" aria-label="เดือนถัดไป" @click="changeMonth(1)">
              <SvgIcon name="chevron-right" size="18" />
            </button>
          </div>
          <h3 class="calendar-month-label">{{ monthLabel }}</h3>
        </div>
        <div class="calendar-toolbar-actions">
          <button class="button secondary calendar-reset-button" @click="resetMonth">กลับเดือนเริ่มต้น</button>
          <span class="calendar-count">{{ items.length }} {{ itemLabel }}</span>
        </div>
      </div>
      <div class="calendar-grid calendar-weekdays">
        <span v-for="weekday in weekdayLabels" :key="weekday">{{ weekday }}</span>
      </div>
      <div class="calendar-grid calendar-dates">
        <button
          v-for="cell in calendarDays"
          :key="cell.key"
          class="calendar-day"
          :class="{
            empty: cell.empty,
            selected: cell.date === selectedDate,
            'has-events': cell.date && dateItems(cell.date).length,
          }"
          :disabled="cell.empty"
          :aria-label="cell.date ? `วันที่ ${cell.day} มี ${dateItems(cell.date).length} ${itemLabel}` : undefined"
          @click="selectDate(cell.date)"
        >
          <span v-if="!cell.empty" class="calendar-day-number">{{ cell.day }}</span>
          <span v-if="cell.date && dateItems(cell.date).length" class="calendar-events">
            <i
              v-for="item in dateItems(cell.date).slice(0, 3)"
              :key="item.id"
              :class="calendarStatusClass(item.status)"
              :title="item.status"
            ></i>
          </span>
          <small v-if="cell.date && dateItems(cell.date).length" class="calendar-event-count">
            {{ dateItems(cell.date).length }} งาน
          </small>
        </button>
      </div>
      <div class="calendar-legend">
        <span v-for="legend in statusLegend" :key="legend.tone">
          <i :class="['legend-dot', `calendar-status-${legend.tone}`]"></i>
          {{ legend.label }}
        </span>
      </div>
    </section>

    <aside class="calendar-detail" aria-live="polite">
      <div class="calendar-detail-heading">
        <div>
          <span class="eyebrow">DAY DETAILS</span>
          <h3>{{ selectedDateLabel }}</h3>
        </div>
        <span class="calendar-detail-total">{{ itemsForDate.length }}</span>
      </div>
      <div v-if="itemsForDate.length" class="calendar-event-list">
        <article v-for="item in itemsForDate" :key="item.id" class="calendar-event-card">
          <div class="calendar-event-card-top">
            <span class="sku-code">{{ item.id }}</span>
            <span :class="statusClass(item.status)">{{ item.status }}</span>
          </div>
          <strong>{{ item.customer }}</strong>
          <p>{{ item.subject || item.type }}</p>
          <dl>
            <div><dt>เวลา</dt><dd>{{ item.time }}</dd></div>
            <div><dt>สถานที่</dt><dd>{{ item.site }}</dd></div>
            <div><dt>พนักงานที่ส่งไป</dt><dd>{{ item.employees?.join(" · ") || item.crew || item.owner }}</dd></div>
          </dl>
        </article>
      </div>
      <div v-else class="calendar-empty-detail">
        <SvgIcon name="calendar" size="28" />
        <strong>วันนี้ยังไม่มีนัดหมาย</strong>
        <p>เลือกวันที่มีจุดสีบนปฏิทินเพื่อดูรายละเอียดงาน</p>
      </div>
      <div v-if="$slots['detail-actions']" class="calendar-detail-actions">
        <slot name="detail-actions" />
      </div>
    </aside>
  </div>
</template>

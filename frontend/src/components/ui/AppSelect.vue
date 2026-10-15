<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import SvgIcon from "@/components/SvgIcon.vue";

const props = defineProps({
  modelValue: { type: [String, Number], default: "" },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: "เลือกข้อมูล" },
  searchPlaceholder: { type: String, default: "ค้นหา..." },
  ariaLabel: { type: String, default: "เลือกข้อมูล" },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  searchable: { type: Boolean, default: true },
  buttonClass: { type: String, default: "" },
});
const emit = defineEmits(["update:modelValue", "change"]);
const root = ref(null);
const menu = ref(null);
const open = ref(false);
const query = ref("");
const menuStyle = ref({});
let trackingMenuPosition = false;
const normalizedOptions = computed(() =>
  props.options.map((option) =>
    typeof option === "object" ? option : { value: option, label: option },
  ),
);
const selectedOption = computed(() =>
  normalizedOptions.value.find(
    (option) => String(option.value) === String(props.modelValue),
  ),
);
const visibleOptions = computed(() => {
  const search = query.value.trim().toLocaleLowerCase("th-TH");
  if (!search) return normalizedOptions.value;
  return normalizedOptions.value.filter((option) =>
    String(option.label).toLocaleLowerCase("th-TH").includes(search),
  );
});
function toggle() {
  if (props.disabled) return;
  if (open.value) {
    closeMenu();
    return;
  }

  open.value = true;
  query.value = "";
  startTrackingMenuPosition();
  nextTick(updateMenuPosition);
}
function choose(option) {
  emit("update:modelValue", option.value);
  emit("change", option.value);
  closeMenu();
}
function closeMenu() {
  open.value = false;
  query.value = "";
  stopTrackingMenuPosition();
}
function closeOnOutside(event) {
  if (root.value?.contains(event.target) || menu.value?.contains(event.target)) {
    return;
  }
  closeMenu();
}
function updateMenuPosition() {
  if (!open.value || !root.value) return;

  const trigger = root.value.querySelector(".app-select-trigger");
  if (!trigger) return;

  const rect = trigger.getBoundingClientRect();
  const viewportWidth = document.documentElement.clientWidth;
  const viewportHeight = window.innerHeight;
  const edge = 8;
  const gap = 8;
  const below = Math.max(0, viewportHeight - rect.bottom - gap - edge);
  const above = Math.max(0, rect.top - gap - edge);
  const openAbove = below < 220 && above > below;
  const availableHeight = openAbove ? above : below;
  const width = Math.min(rect.width, Math.max(0, viewportWidth - edge * 2));
  const left = Math.min(
    Math.max(edge, rect.left),
    Math.max(edge, viewportWidth - edge - width),
  );

  menuStyle.value = {
    left: `${left}px`,
    width: `${width}px`,
    maxHeight: `${Math.max(80, Math.min(320, availableHeight))}px`,
    ...(openAbove
      ? { bottom: `${viewportHeight - rect.top + gap}px` }
      : { top: `${rect.bottom + gap}px` }),
  };
}
function startTrackingMenuPosition() {
  if (trackingMenuPosition) return;
  trackingMenuPosition = true;
  window.addEventListener("resize", updateMenuPosition);
  window.addEventListener("scroll", updateMenuPosition, true);
  window.visualViewport?.addEventListener("resize", updateMenuPosition);
  window.visualViewport?.addEventListener("scroll", updateMenuPosition);
}
function stopTrackingMenuPosition() {
  if (!trackingMenuPosition) return;
  trackingMenuPosition = false;
  window.removeEventListener("resize", updateMenuPosition);
  window.removeEventListener("scroll", updateMenuPosition, true);
  window.visualViewport?.removeEventListener("resize", updateMenuPosition);
  window.visualViewport?.removeEventListener("scroll", updateMenuPosition);
}
onMounted(() => document.addEventListener("click", closeOnOutside));
onBeforeUnmount(() => {
  document.removeEventListener("click", closeOnOutside);
  stopTrackingMenuPosition();
});
</script>

<template>
  <div
    ref="root"
    class="app-select"
    :class="{ 'is-open': open, 'is-disabled': disabled }"
  >
    <button
      type="button"
      class="app-select-trigger"
      :class="buttonClass"
      :aria-label="ariaLabel"
      :aria-expanded="open"
      :disabled="disabled"
      @click.stop="toggle"
    >
      <span :class="{ placeholder: !selectedOption }">{{
        selectedOption?.label || placeholder
      }}</span>
      <SvgIcon name="chevron-right" size="16" />
    </button>
    <Teleport to="body">
      <div
        v-if="open"
        ref="menu"
        class="app-select-menu"
        role="listbox"
        :style="menuStyle"
      >
        <div v-if="searchable" class="app-select-search">
          <SvgIcon name="search" size="17" />
          <input
            v-model="query"
            type="search"
            :placeholder="searchPlaceholder"
            :aria-label="searchPlaceholder"
            @click.stop
          />
        </div>
        <button
          v-for="option in visibleOptions"
          :key="String(option.value)"
          type="button"
          class="app-select-option"
          :class="{ selected: String(option.value) === String(modelValue) }"
          role="option"
          :aria-selected="String(option.value) === String(modelValue)"
          @click="choose(option)"
        >
          {{ option.label }}
        </button>
        <p v-if="!visibleOptions.length" class="app-select-empty">
          ไม่พบข้อมูลที่ค้นหา
        </p>
        <div v-if="$slots['menu-footer']" class="app-select-menu-footer">
          <slot name="menu-footer" :close="closeMenu" />
        </div>
      </div>
    </Teleport>
    <input
      v-if="required"
      class="app-select-required"
      tabindex="-1"
      :value="modelValue"
      required
      aria-hidden="true"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
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
const open = ref(false);
const query = ref("");
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
  open.value = !open.value;
  if (open.value) query.value = "";
}
function choose(option) {
  emit("update:modelValue", option.value);
  emit("change", option.value);
  closeMenu();
}
function closeMenu() {
  open.value = false;
  query.value = "";
}
function closeOnOutside(event) {
  if (root.value && !root.value.contains(event.target)) open.value = false;
}
onMounted(() => document.addEventListener("click", closeOnOutside));
onBeforeUnmount(() => document.removeEventListener("click", closeOnOutside));
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
    <div v-if="open" class="app-select-menu" role="listbox">
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

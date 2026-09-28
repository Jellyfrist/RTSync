<!-- Search control shared by page filters, searchable pickers, and the app header. -->
<script setup>
import SvgIcon from "@/components/SvgIcon.vue";

const model = defineModel({ type: String, default: "" });

defineProps({
  placeholder: { type: String, default: "ค้นหา" },
  label: { type: String, default: "ค้นหา" },
  className: { type: [String, Array, Object], default: "" },
});
</script>

<template>
  <div class="control-field control-field--search" :class="className">
    <SvgIcon name="search" aria-hidden="true" />
    <input
      v-model="model"
      type="search"
      :placeholder="placeholder"
      :aria-label="label"
    />
  </div>
</template>

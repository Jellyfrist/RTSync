<script setup>
import SvgIcon from "@/components/SvgIcon.vue";

defineProps({
  eyebrow: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, default: "" },
  modalClass: { type: String, default: "" },
});

defineEmits(["close", "submit"]);
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <form
      class="modal inventory-form-modal"
      :class="modalClass"
      @submit.prevent="$emit('submit')"
    >
      <div class="modal-heading">
        <div>
          <span class="eyebrow">{{ eyebrow }}</span>
          <h2>{{ title }}</h2>
        </div>
        <button
          type="button"
          class="icon-button"
          title="ปิด"
          @click="$emit('close')"
        >
          <SvgIcon name="close" />
        </button>
      </div>
      <p v-if="description" class="form-helper inventory-form-description">
        {{ description }}
      </p>
      <slot />
      <footer class="inventory-form-footer">
        <slot name="footer-pagination" />
        <div class="inventory-form-actions">
          <div class="button-row end">
            <slot name="actions" />
          </div>
        </div>
      </footer>
    </form>
  </div>
</template>

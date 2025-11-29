<template>
  <label :for="forId" class="app-lable">
    <slot />
    <span v-if="required" class="required">*</span>
  </label>
</template>

<script setup>
defineProps({
  forId: { type: String, default: '' },
  required: { type: Boolean, default: false },
});
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/label';
</style>
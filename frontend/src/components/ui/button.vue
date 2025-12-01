<template>
  <button class="app-button" :class="[variant, { loading, disabled }]" :disabled="disabled || loading"
    @click="handleClick">
    <Loading v-if="loading" />

    <template v-else>
      <template v-if="variant === 'primary'">
        <slot />
      </template>

      <template v-else-if="variant === 'upload'">
        <UploadIcon class="btn-icon" />
        <span>Загрузить</span>
      </template>
    </template>
  </button>
</template>

<script setup>
import Loading from '../../assets/icons/main/Loading.vue';
import UploadIcon from '../../assets/icons/main/Download.vue';

const props = defineProps({
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  variant: { type: String, default: 'primary' },
});

const emit = defineEmits(['click']);
const handleClick = (event) => {
  if (!props.loading && !props.disabled) {
    emit('click', event);
  }
};
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/button';
</style>
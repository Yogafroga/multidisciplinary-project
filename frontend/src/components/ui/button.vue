<template>
  <button
      class="app-button"
      :class="[variant, { loading, disabled }]"
      :disabled="disabled || loading"
      @click="handleClick"
  >
        <span v-if="!loading">
            <slot />
        </span>
    <Loading v-else />
  </button>
</template>

<script setup>
import Loading from '../../assets/icons/main/Loading.vue';

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
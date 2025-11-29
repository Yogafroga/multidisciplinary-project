<template>
  <div class="app-input" :class="[variant, { error: !!error }]">
    <div class="input-wrapper">
      <input
          :id="id"
          :type="type === 'password' ? (isVisible ? 'text' : 'password') : type"
          :placeholder="placeholder"
          :value="modelValue"
          @input="updateValue($event.target.value)"
      />

      <span class="eye" v-if="type === 'password'" @click="toggleVisibility">
                <Eye v-if="!isVisible" />
                <Eye_Close v-else />
            </span>
    </div>
    <span v-if="error" class="error-message">{{ error }}</span>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Eye from '../../assets/icons/main/Eye.vue';
import Eye_Close from '../../assets/icons/main/Eye_Close.vue';

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  error: { type: String, default: '' },
  variant: { type: String, default: 'primary' },
  id: { type: String, default: '' },
});

const emit = defineEmits(['update:modelValue']);

const isVisible = ref(false);
const toggleVisibility = () => (isVisible.value = !isVisible.value);
const updateValue = (value) => emit('update:modelValue', value);
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/input';
</style>
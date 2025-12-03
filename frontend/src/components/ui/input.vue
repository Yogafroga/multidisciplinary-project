<template>
  <div class="app-input" :class="[variant, { error }]">
    <div class="input-wrapper">
      <!-- --- Обычные типы --- -->
      <input v-if="type !== 'daterange'" :id="id" :type="inputType" :placeholder="placeholder" v-model="internalValue"
        class="text-input" />

      <!-- --- Диапазон дат (единый инпут) --- -->
      <input v-else type="text" :id="id" :placeholder="placeholder" :value="formattedDateRange"
        @click="showDatePicker = true" readonly class="daterange-input" />

      <!-- Иконка календаря для диапазона дат -->
      <span class="calendar-icon" v-if="type === 'daterange'" :class="{ active: showDatePicker }"
        @click.stop="toggleDatePicker">
        <Calendar />
      </span>

      <!-- Иконка глаза -->
      <span class="eye" v-if="type === 'password'" @click="toggleVisibility">
        <Eye v-if="!isVisible" />
        <Eye_Close v-else />
      </span>
    </div>

    <!-- Компонент выбора даты -->
    <DatePicker v-if="showDatePicker && type === 'daterange'" v-model="dateRange" is-range
      :model-config="{ type: 'string', mask: 'YYYY-MM-DD' }" @update:modelValue="onDateRangeChange"
      @close="showDatePicker = false" class="date-picker-popup" />

    <span v-if="error" class="error-message">{{ error }}</span>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { DatePicker } from 'v-calendar'
import 'v-calendar/style.css'
import dayjs from 'dayjs'
import Eye from '../../assets/icons/main/Eye.vue'
import Eye_Close from '../../assets/icons/main/Eye_Close.vue'
import Calendar from '../../assets/icons/main/Calendar1.vue'

const props = defineProps({
  modelValue: { type: [String, Array], default: '' },
  type: { type: String, default: 'text' },
  placeholder: String,
  error: String,
  variant: String,
  id: String,
  dateFormat: { type: String, default: 'DD.MM.YYYY' }
})

const emit = defineEmits(["update:modelValue"])

// --- PASSWORD TYPE ---
const isVisible = ref(false)
const toggleVisibility = () => (isVisible.value = !isVisible.value)

const inputType = computed(() =>
  props.type === "password" ? (isVisible.value ? "text" : "password") : props.type
)

// --- NORMAL INPUT ---
const internalValue = ref(props.modelValue)
watch(internalValue, val => emit("update:modelValue", val))
watch(() => props.modelValue, val => internalValue.value = val)

// --- DATE RANGE ---
const showDatePicker = ref(false)
const dateRange = ref({
  start: Array.isArray(props.modelValue) ? props.modelValue[0] : null,
  end: Array.isArray(props.modelValue) ? props.modelValue[1] : null
})

// Форматирование даты
const formatDate = (dateString) => dateString ? dayjs(dateString).format(props.dateFormat) : ''

// Форматированный диапазон для отображения в инпуте
const formattedDateRange = computed(() => {
  const { start, end } = dateRange.value
  if (!start && !end) return ''
  return `${formatDate(start)} – ${formatDate(end)}`
})

// Синхронизация dateRange и v-model
const onDateRangeChange = (value) => {
  emit("update:modelValue", [value.start, value.end])
  if (value.start && value.end) showDatePicker.value = false
}

// Переключение открытия календаря
const toggleDatePicker = () => {
  showDatePicker.value = !showDatePicker.value
}

// Обновляем локальный dateRange при внешнем изменении modelValue
watch(() => props.modelValue, (newValue) => {
  if (Array.isArray(newValue) && newValue.length === 2) {
    dateRange.value = { start: newValue[0], end: newValue[1] }
  }
}, { immediate: true })
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/input';
</style>

<!-- --- Пример использования --- -->

<!-- <Input
  id="date1"
  type="daterange"
  v-model="dateRange"
  placeholder="Выберите период"
  variant="calendar-green" без этого будет простой вариант календарь
/> -->

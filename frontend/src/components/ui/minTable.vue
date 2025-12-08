<template>
  <div class="data-table__wrapper">
    <table class="data-table head" :class="[variant]">
      <thead>
      <tr class="data-table__head-tr" :class="{ 'data-table__row_loading': loading }">
        <th v-for="field in currentHeaders" :key="field.key">
          {{ field.title }}
        </th>
      </tr>
      </thead>
    </table>
  </div>
  <div class="data-table__scroll">
    <table class="data-table body" :class="[variant]">
      <tbody>
      <tr v-for="item in displayedItems" :key="item.id">
        <td v-for="field in currentHeaders" :key="field.key">
          <div class="cell-content">
                            <span class="cell-text">
                                {{ field.display ? field.display(item[field.key]) : item[field.key] }}
                            </span>
            <component v-if="field.icon" :is="field.icon" class="cell-icon" />
          </div>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useCowsStore } from '../../stores/cows.js';

const props = defineProps({
  variant: String,
  type: String,
});

const cowsStore = useCowsStore();
const loading = ref(false);

/* Настройки колонок */
const currentHeaders = computed(() => {
  switch (props.type) {
    case 'cows':
      return [
        {
          title: 'Кон-во коров',
          align: 'start',
          key: 'count',
          display: (value) => value ?? "—"
        },
        {
          title: 'Средний вес/кг',
          align: 'start',
          key: 'averageWeight',
          display: (value) => value ?? "—"
        },
        {
          title: 'Общий вес/кг',
          align: 'start',
          key: 'totalWeight',
          display: (value) => value ?? "—"
        }
      ];
    default:
      return [
        {
          title: 'Файл',
          align: 'end',
          key: 'file-id',
        },
        {
          title: 'ID',
          align: 'start',
          key: 'animal_id',
          display: (value) => value ?? "ID",
        },
        {
          title: 'Дата',
          align: 'start',
          key: 'date',
          icon: 'Calendar1',
          display: (value) => value ?? "Дата"
        },
        {
          title: 'Время',
          align: 'start',
          key: 'time',
          icon: 'Time',
          display: (value) => value ?? "Время"
        },
        {
          title: 'Вес/кг',
          align: 'start',
          key: 'weight',
          display: (value) => value ?? "—"
        }
      ];
  }
});

// Преобразуем данные из history в формат MinTable
const displayedItems = computed(() => {
  if (props.type === 'cows') {
    const data = cowsStore.history.data;
    const count = data.length;
    const totalWeight = data.reduce((sum, item) => sum + (item.weight || 0), 0);
    const averageWeight = count ? (totalWeight / count).toFixed(1) : 0;

    return [{
      id: 'summary',
      count,
      averageWeight,
      totalWeight: totalWeight.toFixed(1)
    }];
  }

  return cowsStore.history.data.map(item => ({
    'file-id': item.image_url?.split('/').pop() || 'photo.jpg',
    animal_id: item.animal_id,
    date: formatDate(item.created_at),
    time: formatTime(item.created_at),
    weight: item.weight,
  }));
});

const formatDate = (iso) => {
  const d = new Date(iso);
  return d.toLocaleDateString('ru-RU');
};

const formatTime = (iso) => {
  const d = new Date(iso);
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
};

// Загрузка данных при монтировании
onMounted(async () => {
  loading.value = true;
  try {
    await cowsStore.fetchHistory({ limit: 10 });
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/minTable';
</style>
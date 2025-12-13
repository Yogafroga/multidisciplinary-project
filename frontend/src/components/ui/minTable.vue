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
            <template v-if="field.key === 'animal_id' && props.mode === 'one'">
              <input v-model="item.animal_id" @input="onIdInput($event.target.value, item.id)" class="table-input"
                placeholder="Введите ID" type="text" />
            </template>
            <template v-else>
              <div class="cell-content">
                <span class="cell-text">
                  {{ field.display ? field.display(item[field.key]) : item[field.key] }}
                </span>
                <component v-if="field.icon" :is="field.icon" class="cell-icon" />
              </div>
            </template>

          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useCowsStore } from '../../stores/cows.js';

const props = defineProps({
  variant: String,
  type: String,
  mode: String,
  items: {
    type: Array,
    default: () => []
  }
});

const cowsStore = useCowsStore();
const loading = ref(false);

const emit = defineEmits(['id-changed']);

const onIdInput = (value, itemId) => {
  emit('id-changed', { id: itemId, animal_id: value });
};

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

const displayedItems = computed(() => {
  const items = props.items || [];

  // Для режима "one" или "group" до расчёта/после
  if (props.mode === 'one' || props.mode === 'group') {
    return items.map(item => ({
      id: item.id,
      'file-id': item.name || 'file.jpg',
      animal_id: item.animal_id || '',
      // Дата и время из uploadTime (клиентское) или из result.created_at (серверное)
      date: item.uploadTime ? formatDate(item.uploadTime) : 
            (item.result?.created_at ? formatDate(item.result.created_at) : '—'),
      time: item.uploadTime ? formatTime(item.uploadTime) : 
            (item.result?.created_at ? formatTime(item.result.created_at) : '—'),
      weight: item.weight ?? item.result?.weight ?? '—',
    }));
  }

  // Для сводной таблицы по группе (cows)
  if (props.type === 'cows') {
    const cows = cowsStore.calculatedGroup || {};
    return [{
      id: 'summary',
      count: cows.count ?? '—',
      averageWeight: cows.averageWeight ?? '—',
      totalWeight: cows.totalWeight ?? '—',
    }];
  }

  return [];
});


const localItems = ref(props.items || []);
watch(() => props.items, (newItems) => {
  localItems.value = newItems || [];
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
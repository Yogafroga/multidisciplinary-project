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
                <tr v-for="item in pageItems" :key="item.id">
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
import { getPosts } from '../../services/api'
import { computed, onMounted, ref } from 'vue'
import Calendar1 from '../../assets/icons/main/Calendar1.vue'
import Time from '../../assets/icons/main/Time.vue'
import { convertApiResponceToDataTableOptions } from '../../stores/table'

import { testTableData } from '../../helpers/minTableDate'

const props = defineProps({
    variant: String,
    type: String,
})
const pageItems = ref([])
const loading = ref(true)

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
            ]

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
                    key: 'id',
                    display: (value) => value ?? "ID",
                },
                {
                    title: 'Дата',
                    align: 'start',
                    key: 'date-id',
                    icon: Calendar1,
                    display: (value) => value ?? "Дата"
                },
                {
                    title: 'Время',
                    align: 'start',
                    key: 'time-id',
                    icon: Time,
                    display: (value) => value ?? "Вемя"
                },
                {
                    title: 'Вес/кг',
                    align: 'start',
                    key: 'weight-id',
                    display: (value) => value ?? "—"
                }
            ]
    }
})


// Загрузка данных сервера
// async function loadData() {
//     loading.value = true

//     const data = convertApiResponceToDataTableOptions(getPosts())
//     pageItems.value = data.items

//     loading.value = false
// }

// Загрузка тестовых данных
async function loadData() {
    loading.value = true

    if (props.type === 'cows') {
        pageItems.value = [
            {
                id: 1,
                count: 7,
                averageWeight: 500,
                totalWeight: 2700
            }
        ]
    } else {
        pageItems.value = testTableData
    }

    loading.value = false
}


onMounted(loadData)
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/minTable';
</style>
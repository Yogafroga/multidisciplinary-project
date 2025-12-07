<!-- BigTable.vue -->
<template>
    <div class="table-wrapper">
        <table class="data-table">
            <thead>
                <tr>
                    <th class="checkbox-th">
                        <div class="th-block">
                            Выбрать
                            <div class="custom-checkbox" @click="toggleSelectAll">
                                <CheckboxChecked v-if="allPageSelected" />
                                <CheckboxUnchecked v-else />
                            </div>
                        </div>
                    </th>

                    <th>Фото</th>

                    <th v-for="field in head" :key="field.key" class="sortable"
                        :class="{ 'sorted': sort.key === field.key }" @click="field.sortable && toggleSort(field.key)">
                        <div class="th-block">
                            {{ field.title }}
                            <SortIcon v-if="field.sortable" class="sort-icon" :class="{
                                'active-asc': sort.key === field.key && sort.order === 'asc',
                                'active-desc': sort.key === field.key && sort.order === 'desc'
                            }" />
                        </div>
                    </th>

                    <th>Действия</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="item in displayedItems" :key="item.id"
                    :class="{ 'selected-row': selectedItems.includes(item.id) }">
                    <td class="checkbox-td">
                        <div class="custom-checkbox" @click="toggleRow(item.id)">
                            <CheckboxChecked v-if="selectedItems.includes(item.id)" />
                            <CheckboxUnchecked v-else />
                        </div>
                    </td>
                    <td>{{ item.photo }}</td>
                    <td>{{ item.id }}</td>
                    <td>{{ item.date }}</td>
                    <td>{{ item.time }}</td>
                    <td>{{ item.weight }}</td>
                    <td class="actions-td">
                        <button class="action-btn info" title="Скачать PDF" @click="downloadPDF">
                            <Pdf_M />
                        </button>
                        <button class="action-btn delete" title="Скачать Excel" @click="downloadExcel">
                            <File_M />
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>

        <div class="pagination">
            <button class="icon-btn" :disabled="currentPage === 1" @click="prevPage(item)">
                <previousIcon />
            </button>
            <span>{{ currentPage }} / {{ pagesCount }}</span>
            <button class="icon-btn" :disabled="currentPage >= pagesCount" @click="nextPage(item)">
                <nextIcon />
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { jsPDF } from "jspdf"
import * as XLSX from "xlsx"

// Иконки
import previousIcon from '../../assets/icons/main/Left.vue'
import nextIcon from '../../assets/icons/main/Right.vue'
import CheckboxUnchecked from '../../assets/icons/main/Check_Box_Blank.vue'
import CheckboxChecked from '../../assets/icons/main/Check_Box.vue'
import SortIcon from '../../assets/icons/main/Chevron_Both.vue'
import File_M from '../../assets/icons/files/X_M.vue'
import Pdf_M from '../../assets/icons/files/Pdf_M.vue'

// --- ДАННЫЕ ---
const rawItems = ref([
    { id: 18, date: '25.11.25', photo: '18_25.11.25_12:01.png', time: '12:01', weight: 648 },
    { id: 19, date: '26.11.25', photo: '19_26.11.25_09:30.png', time: '09:30', weight: 712 },
    ...Array.from({ length: 120 }, (_, i) => ({
        photo: 'photo.p ng',
        id: 20 + i,
        date: ['25.11.25', '26.11.25', '27.11.25'][Math.floor(Math.random() * 3)],
        time: `${String(Math.floor(Math.random() * 24)).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
        weight: 500 + Math.floor(Math.random() * 300)
    }))
]) // удалить

const head = [
    {
        title: 'ID',
        align: 'end',
        key: 'id',
        sortable: true,
    },
    {
        title: 'Дата',
        align: 'end',
        key: 'date',
        sortable: true,
    },
    {
        title: 'Время',
        align: 'end',
        key: 'time',
        sortable: true,
    },
    {
        title: 'Вес/кг',
        align: 'end',
        key: 'weight',
        sortable: true,
    },
]

const selectedItems = ref([])

// --- ПАГИНАЦИЯ ---
const pagination = reactive({
    page: 1,
    perPage: 10
})

const currentPage = computed({
    get: () => pagination.page,
    set: (v) => pagination.page = v
})

const pagesCount = computed(() =>
    Math.ceil(rawItems.value.length / pagination.perPage)
)

// --- СОРТИРОВКА ---
const sort = reactive({
    key: null,
    order: 'asc' // 'asc' | 'desc'
})

const toggleSort = (key) => {
    if (sort.key === key) {
        if (sort.order === 'asc') {
            sort.order = 'desc'
        } else {
            sort.order = 'asc'
        }
    } else {
        sort.key = key
        sort.order = 'asc'
    }
    pagination.page = 1
}

// Отсортированные + отпагинированные элементы
const displayedItems = computed(() => {
    let items = [...rawItems.value]

    if (sort.key) {
        items.sort((a, b) => {
            let aVal = a[sort.key]
            let bVal = b[sort.key]

            // Обработка даты
            if (sort.key === 'date') {
                const parse = (s) => {
                    if (!s) return 0
                    const [d, m, y] = s.split('.').map(Number)
                    return new Date(2000 + y, m - 1, d).getTime()
                }
                aVal = parse(aVal)
                bVal = parse(bVal)
            }

            // Время
            if (sort.key === 'time') {
                const toMinutes = (t) => {
                    if (!t) return 0
                    const [h, m] = t.split(':').map(Number)
                    return h * 60 + m
                }
                aVal = toMinutes(aVal)
                bVal = toMinutes(bVal)
            }

            // Нулевые значения
            if (aVal == null) aVal = ''
            if (bVal == null) bVal = ''

            if (aVal < bVal) return sort.order === 'asc' ? -1 : 1
            if (aVal > bVal) return sort.order === 'asc' ? 1 : -1
            return 0
        })
    }

    // Пагинация
    const start = (pagination.page - 1) * pagination.perPage
    const end = start + pagination.perPage
    return items.slice(start, end)
})


// --- ВЫДЕЛЕНИЕ ---
const allPageSelected = computed(() =>
    displayedItems.value.length > 0 &&
    displayedItems.value.every(i => selectedItems.value.includes(i.id))
)

const toggleRow = (id) => {
    const idx = selectedItems.value.indexOf(id)
    if (idx > -1) selectedItems.value.splice(idx, 1)
    else selectedItems.value.push(id)
}

const toggleSelectAll = () => {
    if (allPageSelected.value) {
        selectedItems.value = []
    } else {
        selectedItems.value = rawItems.value.map(i => i.id)
    }
}


// --- ПАГИНАЦИЯ ---
const nextPage = () => {
    if (currentPage.value < pagesCount.value) {
        pagination.page++
    }
}

const prevPage = () => {
    if (currentPage.value > 1) pagination.page--
}

// --- Пример реализации скачивания ---
const downloadPDF = (item) => {
    const doc = new jsPDF()
    doc.text("Данные строки", 10, 10)

    let y = 20
    Object.keys(item).forEach(key => {
        doc.text(`${key}: ${item[key]}`, 10, y)
        y += 10
    })

    doc.save(`row-${item.id}.pdf`)
}

const downloadExcel = (item) => {
    const worksheet = XLSX.utils.json_to_sheet([item])
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, "Row")

    XLSX.writeFile(workbook, `row-${item.id}.xlsx`)
}
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/bigTable';
</style>
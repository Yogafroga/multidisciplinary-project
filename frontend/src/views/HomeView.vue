<template>
    <div class="home">
        <div class="home__content">
            <div class="home__header">
                <Header class="home__header-component" :email="userEmail" :active-tab="currentTab"
                    @change-tab="currentTab = $event" @logout="handleLogout" />
            </div>

            <!-- Реализация плавного перехода между вкладками -->
            <Transition name="fade" mode="out-in">
                <!-- Вкладка для загрузки данных -->
                <div v-if="currentTab === 'upload'" class="home__loading">
                    <div class="home__upload">
                        <TabBar variant="animals" @update:selectedTab="selectedAnimalTab = $event" />

                        <div v-if="selectedAnimalTab === 'one'">
                            <DragDropUpload class="home__upload-image-drop" variant="image" />
                        </div>

                        <div v-else-if="selectedAnimalTab === 'group'">
                            <DragDropUpload class="home__upload-archive-drop" variant="archive" />
                        </div>

                        <div class="home__files">
                            <FileItem :file="{ name: 'report.pdf', loaded: 2_500_000, total: 5_000_000 }" />
                            <FileItem :file="{ name: 'photo.jpg', loaded: 5_000_000, total: 5_000_000 }" />
                            <FileItem :file="{ name: 'data.raw', loaded: 1_000_000, total: 5_000_000 }" />
                        </div>
                    </div>

                    <div class="home__data">
                        <div class="home__controls">
                            <div class="home__controls-one" v-if="selectedAnimalTab === 'one'">
                                <MinTable type="default" variant="green" />
                            </div>

                            <div class="home__controls-group" v-else="selectedAnimalTab === 'group'">
                                <div>
                                    <MinTable type="cows" variant="green" />
                                </div>
                                <div>
                                    <MinTable type="default" variant="green" />
                                </div>
                            </div>

                            <Button class="home__controls-btn" :disabled="!isDataReady || isCalculating"
                                @click="handlCalculate">Рассчитать</Button>
                        </div>

                        <div class="home__export">
                            <TabBar class="home__export-tabbar" variant="export"
                                v-model:selectedTab="selectedExportTab" />
                            <Button class="home__export-btn" :disabled="!isDataReady || isCalculating"
                                @click="handleExport">Скачать</Button>
                        </div>
                    </div>
                </div>

                <!-- Вкладка для просмотра историй -->
                <div v-else class="home__history">
                    <div class="home__actions">
                        <div class="home__action-left">
                            <TabBar variant="small" />
                            <div class="home__filter">
                                <div class="home-filter-content">
                                    <Lable class="home__filter-lable" for-id="id">Номер бирки:</Lable>
                                    <Input class="home__filter-input" id="id" type="text" placeholder="ID" />
                                </div>
                                <div class="home-filter-content">
                                    <Lable class="home__filter-lable" for-id="date">Выбор периода:</Lable>
                                    <Input class="home__filter-input" id="date" type="daterange" placeholder="Период" variant="calendar-green" v-model="dateRange"/>
                                </div>
                            </div>
                            <div class="export">
                                <TabBar variant="export-small" />
                                <Button variant="download" ></Button>
                            </div>
                        </div>
                    </div>
                    <BigTable type="operation" />
                </div>
            </Transition>
        </div>
    </div>
</template>



<script setup>
import { ref } from 'vue'

import Header from '../components/ui/head.vue'
import TabBar from '../components/ui/tabBar.vue'
import DragDropUpload from '../components/ui/DragDropUpload.vue'
import FileItem from '../components/ui/fileItem.vue'
import MinTable from '../components/ui/minTable.vue'
import Button from '../components/ui/button.vue'
import Lable from '../components/ui/label.vue'
import Input from '../components/ui/input.vue'
import BigTable from '../components/ui/bigTable.vue'

const userEmail = ref('user@example.com')
const currentTab = ref('upload')
const selectedAnimalTab = ref('one')
const isDataReady = ref(false) // данные для расчёта готовы
const isCalculating = ref(false) // сейчас идёт расчёт

const handleLogout = () => {
    // логика выхода
}

// Логика клика на конопку расчета
async function handlCalculate() {

}

// Логика клика на конопку скачивания
async function handleExport() {
    if (!isDataReady.value || isCalculating.value) return

    if (selectedExportTab.value === 'pdf') {
        downloadPDF() // Функция скачивания (заглушки для API)
    } else if (selectedExportTab.value === 'excel') {
        downloadExcel() // Функция скачивания (заглушки для API)
    }
}
</script>

<style scoped lang="scss">
@use '../assets/styles/components/HomeView';
</style>
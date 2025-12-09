<template>
    <div class="header-bar">
        <div class="left-section">
            <div class="logo">
                <LogoBig />
            </div>
        </div>

        <nav class="center-section" aria-label="Основная навигация">
            <ul class="nav-list">
                <li>
                    <a href="#" class="nav-link download-block" :class="{ active: activeTab === 'upload' }"
                        @click.prevent="$emit('change-tab', 'upload')" aria-current="upload">
                        <DownloadIcon class="head-icon" />
                        <span class="text">Загрузка фотографий</span>
                    </a>
                </li>
                <li>
                    <a href="#" class="nav-link history-block" :class="{ active: activeTab === 'history' }"
                        @click.prevent="$emit('change-tab', 'history')" aria-current="history">
                        <HistoryIcon class="head-icon" />
                        <span class="text">История взвешиваний</span>
                    </a>
                </li>
            </ul>
        </nav>
        <div class="right-section">
            <span class="email">{{ email }}</span>
            <button class="logout-btn" @click="$emit('logout')" aria-label="Выйти">
                <Logout class="head-icon" />
            </button>
        </div>
    </div>
</template>

<script setup>
import LogoBig from '../../assets/icons/logo/Logo-big.vue';
import DownloadIcon from '../../assets/icons/main/Download.vue';
import HistoryIcon from '../../assets/icons/main/History.vue';
import Logout from '../../assets/icons/main/Logout.vue';

const props = defineProps({
    email: String,
    activeTab: {
        type: String,
        required: true,
        validator: v => ['upload', 'history'].includes(v)
    }
})

defineEmits(['change-tab', 'logout'])
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/head';
</style>
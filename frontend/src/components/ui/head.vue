<template>
    <div class="header-bar">
        <div class="left-section">
            <div class="logo">
                <LogoBig />
            </div>
        </div>
        <div class="center-section">
            <button class="download-block">
                <DownloadIcon class="head-icon" />
                <span class="text text-h3">Загрузка фотографий</span>
            </button>
            <button class="history-block">
                <HistoryIcon class="head-icon" />
                <span class="text text-h3">История взвешиваний</span>
            </button>
        </div>
        <div class="right-section">
            <span class="email text-h4">{{ email }}</span>
            <button>
                <Logout class="head-icon" />
            </button>
        </div>   
    </div>
</template>

<script>
import LogoBig from '../../assets/icons/logo/Logo-big.vue';
import DownloadIcon from '../../assets/icons/main/Download.vue';
import HistoryIcon from '../../assets/icons/main/History.vue';
import Logout from '../../assets/icons/main/Logout.vue';

export default {
    name: 'Head',

    props: {
        email: {
            type: String,
            required: true
        }
    },

    components: {
        LogoBig,
        DownloadIcon,
        HistoryIcon,
        Logout
    }
}
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/head';
</style>
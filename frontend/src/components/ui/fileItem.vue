<template>
    <div class="file-item">
        <div class="file-icon">
            <component :is="fileIcon" />
        </div>

        <div class="file-info">
            <div class="file-name text-h4">{{ file.name }}</div>
            <div class="file-info-botton text-h5">
                <div class="file-progress">
                    <span class="text-h5">{{ formattedLoaded }}</span>
                    <span> / </span>
                    <span class="text-h5">{{ formattedTotal }}</span>
                </div>


                <Point />

                <!-- Вариан "Загрузка" -->
                <template v-if="isLoading">
                    <LoadingIcon class="loading-spinner" />
                    <span>Загрузка...</span>
                </template>

                <!-- Вариант "Завершено" -->
                <template v-if="isDone">
                    <DoneIcon class="done-icon" />
                    <span>Завершено</span>
                </template>
            </div>
        </div>
        <div class="btn">
            <template v-if="isLoading">
                <button class="delete-btn" @click="$emit('delete')">
                    <CloseIcon />
                </button>
            </template>

            <template v-if="isDone">
                <button class="delete-btn" @click="$emit('delete')">
                    <DeleteIcon />
                </button>
            </template>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';

import LoadingIcon from '../../assets/icons/main/Loading.vue';
import Point from '../../assets/icons/main/Point.vue';
import DoneIcon from '../../assets/icons/main/Check.vue';
import CloseIcon from '../../assets/icons/main/Close.vue';
import DeleteIcon from '../../assets/icons/main/Trash.vue';

import Jpg_L from '../../assets/icons/files/Jpg_L.vue'
import Pdf_L from '../../assets/icons/files/Pdf_L.vue'
import Png_L from '../../assets/icons/files/Png_L.vue'
import Raw_L from '../../assets/icons/files/Raw_L.vue'
import TIFF_L from '../../assets/icons/files/TIFF_L.vue'
import File_L from '../../assets/icons/files/X_L.vue'

const props = defineProps({
    file: {
        type: Object,
        required: true
    }
});

function getIcon(name) {
    const ext = name.split('.').pop().toLowerCase();
    switch (ext) {
        case 'png':
            return Png_L;
        case 'jpg':
            return Jpg_L;
        case 'pdf':
            return Pdf_L;
        case 'raw':
            return Raw_L;
        case 'tiff':
            return TIFF_L;
        default:
            return File_L;
    }
}

const fileIcon = computed(() => {
    return getIcon(props.file.name);
});

function formatMb(bytes) {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB'; //Если данные будут приходить в байтах
};

const formattedLoaded = computed(() => formatMb(props.file.loaded))
const formattedTotal = computed(() => formatMb(props.file.total))

const isDone = computed(() => props.file.loaded >= props.file.total)
const isLoading = computed(() => !isDone.value)
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/fileItem';
</style>
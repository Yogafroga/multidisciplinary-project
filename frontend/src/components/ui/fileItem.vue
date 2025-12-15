<template>
    <div class="file-item" :class="{ 'file-item--error': isError, 'file-item--partial': isPartial }">
        <div class="file-data-content">
            <div class="file-icon">
                <component :is="fileIcon" />
            </div>

            <div class="file-info">
                <div class="file-name text-h4">{{ file.name }}</div>
                <div class="file-info-botton text-h5">
                    <div class="file-progress">
                        <span>{{ formattedProgress }}</span>
                        <span class="text-muted"> / {{ formattedTotal }}</span>
                    </div>


                    <Point />
                    <div class="file-status">
                        <!-- Вариан "Загрузка" -->
                        <template v-if="isUploading">
                            <LoadingIcon class="loading-spinner" />
                            <span>Загрузка{{ progressPercent ? ' ' + progressPercent + '%' : '' }}...</span>
                        </template>

                        <!-- Вариант "Завершено" -->
                        <template v-if="isSuccess">
                            <DoneIcon class="done-icon" />
                            <span>Завершено</span>
                        </template>

                        <template v-if="isPartial">
                            <span class="text-warning">
                                {{ file.result.processed_images }}/{{ file.result.total_images }} обработано
                            </span>
                        </template>

                        <template v-if="isError">
                            <span class="text-error">Ошибка</span>
                        </template>

                        <template v-if="isPending">
                            <span class="text-error"> Ожидание...</span>
                        </template>
                    </div>
                </div>
            </div>
        </div>

        <button v-if="canRemove" class="delete-btn" @click="$emit('remove', file.id)" :disabled="isUploading"
            :title="isUploading ? 'Нельзя удалить во время загрузки' : 'Удалить файл'">
            <CloseIcon v-if="isUploading" />
            <DeleteIcon v-else />
        </button>

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

defineEmits(['remove'])

// Иконка по расширению
const fileIcon = computed(() => {
    const ext = props.file.name.split('.').pop().toLowerCase()
    const map = {
        jpg: Jpg_L,
        png: Png_L,
        zip: File_L,
        default: File_L,
    }
    return map[ext] || map.default
})

// Формотирование размеров
const formatBytes = (bytes) => {
    if (!bytes) return '0 MB'
    const mb = bytes / 1024 / 1024
    return mb < 10 ? mb.toFixed(2) + ' MB ' : mb.toFixed(1) + ' MB'
}

const formattedTotal = computed(() => formatBytes(props.file.size || props.file.total))
const formattedLoaded = computed(() => formatBytes(props.file.loaded || 0))

const progressPercent = computed(() => {
    if (!props.file.size) return 0
    return Math.min(100, Math.round((props.file.loaded / props.file.size) * 100))
})

const formattedProgress = computed(() => {
    if (progressPercent.value === 0) return '0'
    return `${formattedLoaded.value} (${progressPercent.value}%)`
})

const canRemove = computed(() => {
    return !props.file.fromArchive
})

// Статусы
const isUploading = computed(() => props.file.status === 'uploading')
const isSuccess = computed(() => props.file.status === 'success')
const isPartial = computed(() => props.file.status === 'partial')
const isError = computed(() => props.file.status === 'error')
const isPending = computed(() => props.file.status === 'pending')

</script>

<style scoped lang="scss">
@use '../../assets/styles/components/fileItem';
</style>
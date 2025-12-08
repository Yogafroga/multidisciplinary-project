<template>
  <div
      class="drag-drop-zone"
      :class="{ 'drag-over': isDragOver }"
      @dragenter="onDragEnter"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
  >
  
    <div class="drag-drop-content">
      <AppButton variant="upload" @click="selectFile">
        {{ buttonText }}
      </AppButton>
      <div class="text">
        <p class="text-h4">{{ title }}</p>
        <p class="text-h5 hint">{{ hint }}</p>
      </div>
      <input
          ref="fileInput"
          type="file"
          :accept="accept"
          :multiple="multiple"
          @change="onFileChange"
          class="file-input"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useCowsStore } from '../../stores/cows.js';
import AppButton from '../../components/ui/button.vue';

const cowsStore = useCowsStore();
const fileInput = ref(null);
const isDragOver = ref(false);

// === Props ===
const props = defineProps({
  variant: {
    type: String,
    default: 'image', // 'image' или 'archive'
  },
});

// === Конфигурация по варианту ===
const config = {
  image: {
    accept: 'image/jpeg, image/png',
    multiple: true,
    title: 'Перетащите фото или нажмите для выбора',
    hint: 'Поддерживаемые форматы: JPG, PNG',
    buttonText: 'Загрузить фото',
  },
  archive: {
    accept: '.zip',
    multiple: false,
    title: 'Перетащите ZIP-архив или нажмите для выбора',
    hint: 'Поддерживаемый формат: ZIP',
    buttonText: 'Загрузить архив',
  },
};

const { accept, multiple, title, hint, buttonText } = config[props.variant];

// === События перетаскивания ===
const onDragEnter = (e) => {
  e.preventDefault();
  isDragOver.value = true;
};

const onDragOver = (e) => {
  e.preventDefault();
  isDragOver.value = true;
};

const onDragLeave = () => {
  isDragOver.value = false;
};

const onDrop = (e) => {
  e.preventDefault();
  isDragOver.value = false;
  const files = Array.from(e.dataTransfer.files);
  handleFiles(files);
};

// === Открытие диалога выбора файла ===
const selectFile = () => {
  fileInput.value?.click();
};

const onFileChange = (e) => {
  const files = Array.from(e.target.files);
  handleFiles(files);
};

// === Обработка файлов ===
const handleFiles = async (files) => {
  if (!files.length) return;

  if (props.variant === 'image') {
    const validFiles = files.filter(f => ['image/jpeg', 'image/png', 'image/jpg'].includes(f.type));
    if (validFiles.length !== files.length) {
      alert('Недопустимый формат. Разрешены только JPG и PNG.');
      return;
    }

    for (const file of validFiles) {
      const result = await cowsStore.uploadImage(file, 'auto');
      if (result.success) {
        console.log('[✅] Фото успешно загружено:', result.data);
      } else {
        alert(`Ошибка загрузки фото ${file.name}: ${result.error}`);
      }
    }
  }

  if (props.variant === 'archive') {
    const file = files[0];
    if (!file.name.toLowerCase().endsWith('.zip')) {
      alert('Разрешён только ZIP-архив');
      return;
    }

    const result = await cowsStore.uploadArchive(file);
    if (result.success) {
      console.log('[✅] Архив успешно загружен:', result.data);
      alert(`Архив "${file.name}" загружен: ${result.data.processed_images} файлов обработано`);
    } else {
      alert(`Ошибка загрузки архива: ${result.error}`);
    }
  }

  // Сброс input
  fileInput.value.value = '';
};
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/dragDrop';
</style>
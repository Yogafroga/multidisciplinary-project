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
      <!-- ✅ Добавлен @click -->
      <AppButton variant="upload" @click="selectFile">
        {{ buttonText }}
      </AppButton>
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
    title: 'Перетащите файлы или нажмите для выбора',
    hint: 'Доступные форматы: JPG, PNG',
    buttonText: 'Загрузить фото',
  },
  archive: {
    accept: '.zip',
    multiple: false,
    title: 'Перетащите архив или нажмите для выбора',
    hint: 'Доступные форматы: ZIP',
    buttonText: 'Загрузить архив',
  },
};

const current = config[props.variant];

const accept = current.accept;
const multiple = current.multiple;
const title = current.title;
const hint = current.hint;
const buttonText = current.buttonText;

// === События ===
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

// ✅ Вызов через кнопку
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

  const file = files[0]; // архив — один файл

  if (props.variant === 'image') {
    const imageFiles = files.filter((f) =>
        ['image/jpeg', 'image/jpg', 'image/png'].includes(f.type)
    );

    if (imageFiles.length !== files.length) {
      alert('Разрешены только JPG и PNG файлы');
      return;
    }

    for (const f of imageFiles) {
      console.log('[DRAGDROP] Загрузка фото:', f.name);
      const result = await cowsStore.uploadImage(f, 'auto');
      if (result.success) {
        console.log('[✅] Фото загружено:', result.data);
      } else {
        console.error('[❌] Ошибка загрузки фото:', result.error);
      }
    }
  }

  if (props.variant === 'archive') {
    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'zip') {
      alert('Разрешён только ZIP-архив');
      return;
    }

    console.log('[DRAGDROP] Загрузка архива:', file.name);
    const result = await cowsStore.uploadArchive(file, 'cow');
    if (result.success) {
      console.log('[✅] Архив обработан:', result.data);
      // Можно добавить уведомление
    } else {
      console.error('[❌] Ошибка загрузки архива:', result.error);
    }
  }

  fileInput.value.value = '';
};
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/dragDrop';
</style>
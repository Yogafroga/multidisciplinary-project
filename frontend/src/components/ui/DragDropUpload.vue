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
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
        />
      </svg>
      <div class="text">
        <p class="text-h4">Перетащите файлы или нажмите для выбора</p>
        <p class="text-h5 hint">Доступные форматы: JPG, PNG</p>
      </div>
      <input
          ref="fileInput"
          type="file"
          :accept="accept"
          multiple
          @change="onFileChange"
          class="file-input"
      />
      <AppButton variant="upload" @click="selectFile">Загрузить</AppButton>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
//import { useCowsStore } from 'frontend/src/stores/cows.js';
//import AppButton from 'frontend/src/components/ui/button.vue';
import { useCowsStore} from "../../stores/cows.js";
import AppButton from "../../components/ui/button.vue";

const cowsStore = useCowsStore();
const fileInput = ref(null);
const isDragOver = ref(false);

const accept = 'image/jpeg, image/png';

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

const selectFile = () => {
  fileInput.value?.click();
};

const onFileChange = (e) => {
  const files = Array.from(e.target.files);
  handleFiles(files);
};
/*
const handleFiles = async (files) => {
  if (!files.length) return;

  const imageFiles = files.filter((file) =>
      ['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)
  );

  if (imageFiles.length !== files.length) {
    alert('Разрешены только JPG и PNG файлы');
    return;
  }

  for (const file of imageFiles) {
    await cowsStore.uploadImage(file, 'auto');
  }

  fileInput.value.value = '';
};
*/
const handleFiles = async (files) => {
  if (!files.length) return;

  const imageFiles = files.filter((file) =>
      ['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)
  );

  if (imageFiles.length !== files.length) {
    alert('Разрешены только JPG и PNG файлы');
    return;
  }

  // 🔥 Каждый файл отправляется в стор
  for (const file of imageFiles) {
    console.log('[TEST] Передаём файл в стор:', file.name);
    const result = await cowsStore.uploadImage(file, 'auto');
    if (result.success) {
      console.log('[✅ SUCCESS] Файл добавлен в стор:', result.data);
    } else {
      console.error('[❌ ERROR] Ошибка загрузки:', result.error);
    }
  }

  fileInput.value.value = '';
};
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/dragDrop';
</style>
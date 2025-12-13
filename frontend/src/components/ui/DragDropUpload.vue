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
import { ref, computed  } from 'vue';
import AppButton from '../../components/ui/button.vue';

// Эмит событий в родитель
const emit = defineEmits(['file-added']);

const props = defineProps({
  variant: {
    type: String,
    default: 'image' // 'image' или 'archive'
  }
});

const fileInput = ref(null);
const isDragOver = ref(false);

const config = {
  image: {
    accept: 'image/jpeg, image/png',
    multiple: true,
    title: 'Перетащите фото или нажмите для выбора',
    hint: 'Поддерживаемые форматы: JPG, PNG',
    buttonText: 'Загрузить фото'
  },
  archive: {
    accept: '.zip',
    multiple: false,
    title: 'Перетащите ZIP-архив или нажмите для выбора',
    hint: 'Поддерживаемый формат: ZIP',
    buttonText: 'Загрузить архив'
  }
};

// реактивные вычисляемые значения для шаблона
const variantConfig = computed(() => config[props.variant] || config.image);
const accept = computed(() => variantConfig.value.accept);
const multiple = computed(() => variantConfig.value.multiple);
const title = computed(() => variantConfig.value.title);
const hint = computed(() => variantConfig.value.hint);
const buttonText = computed(() => variantConfig.value.buttonText);

// drag events
const onDragEnter = (e) => { e.preventDefault(); isDragOver.value = true; };
const onDragOver = (e) => { e.preventDefault(); isDragOver.value = true; };
const onDragLeave = () => { isDragOver.value = false; };
const onDrop = (e) => {
  e.preventDefault();
  isDragOver.value = false;
  const files = Array.from(e.dataTransfer?.files || []);
  handleFiles(files);
};

// === Открытие диалога выбора файла ===
const selectFile = () => {
  fileInput.value?.click();
};

const onFileChange = (e) => {
  const files = Array.from(e.target?.files || []);
  handleFiles(files);
};

// просто эмитим файлы вверх, родитель сам делает загрузку
const handleFiles = (files) => {
  if (!files?.length) return;

  const now = new Date();

  const formatDateShort = (d) => {
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = String(d.getFullYear()).slice(2);
    return `${day}.${month}.${year}`;
  };

  const formatTimeShort = (d) => {
    return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  };

  const enrichedFiles = files.map(file => ({
    id: crypto.randomUUID(),
    name: file.name,
    size: file.size,
    variant: props.variant,
    status: 'pending',
    progress: 0,
    date: formatDateShort(now),
    time: formatTimeShort(now),
    created_at: now.toISOString(),
  }));

  // Эмиттим: метаданные + сами File-ы отдельно
  emit('file-added', enrichedFiles, Array.from(files), props.variant);

  // Сброс input
  if (fileInput.value) fileInput.value.value = '';
};
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/dragDrop';
</style>
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
                        <TabBar variant="animals" @update:selectedTab="onAnimalTabChange" />

                        <div v-if="selectedAnimalTab === 'one'">
                            <DragDropUpload class="home__upload-image-drop" variant="image" @file-added="onFileAdded" />
                        </div>

                        <div v-else-if="selectedAnimalTab === 'group'">
                            <DragDropUpload class="home__upload-archive-drop" variant="archive"
                                @file-added="onFileAdded" />
                        </div>

                        <div class="home__files">
                            <FileItem v-for="f in fileItems" :key="f.id" :file="f" @remove="removeFile" />
                        </div>
                    </div>

                    <div class="home__data">
                        <div class="home__controls">
                            <Transition name="fade" mode="out-in">
                                <div class="home__controls-one" v-if="selectedAnimalTab === 'one'">
                                    <MinTable type="default" variant="green" :mode="selectedAnimalTab"
                                        :items="fileItems" @id-changed="checkIfReady" />
                                </div>

                                <div class="home__controls-group" v-else="selectedAnimalTab === 'group'">
                                    <div>
                                        <MinTable type="cows" variant="green" :mode="selectedAnimalTab" />
                                    </div>
                                    <div>
                                        <MinTable type="default" variant="green" :mode="selectedAnimalTab"
                                            :items="fileItems" />
                                    </div>
                                </div>
                            </Transition>


                            <Button class="home__controls-btn" :disabled="!canCalculate || isCalculating"
                                :loading="isCalculating" @click="handlCalculate">Рассчитать</Button>
                        </div>

                        <div class="home__export">
                            <TabBar class="home__export-tabbar" variant="export"
                                v-model:selectedTab="selectedExportTab" />
                            <Button class="home__export-btn" :disabled="!isExportDataReady   || isCalculating"
                                @click="handleExport">Скачать</Button>
                        </div>
                    </div>
                </div>

                <!-- Вкладка для просмотра историй -->
                <div v-else class="home__history">
                    <div class="home__actions">
                        <div class="home__action-left">
                            <TabBar variant="small" @update:selectedTab="selectedJournal = $event" />
                            <div class="home__filter">
                                <div class="home-filter-content">
                                    <Lable class="home__filter-lable" for-id="id">Номер бирки:</Lable>
                                    <Input class="home__filter-input-id small" id="id" type="text" placeholder="ID"
                                        v-model="filterId" />
                                </div>
                                <div class="home-filter-content">
                                    <Lable class="home__filter-lable" for-id="date">Выбор периода:</Lable>
                                    <Input class="home__filter-input" id="date" type="daterange" placeholder="Период"
                                        variant="calendar-green" v-model="dateRange" />
                                </div>
                                <Button v-if="hasActiveFilters" class="reset-filters-btn" @click="resetFilters"
                                    title="Сбросить все фильтры" variant="reset">
                                </Button>

                            </div>
                        </div>
                        <div class="home__action-export">
                            <TabBar variant="export-small" v-model:selectedTab="selectedExportTab" />
                            <Button variant="download" @click="exportSelected"></Button>
                        </div>
                    </div>
                    <div class="home__table">
                        <Transition name="fade" mode="out-in">
                            <div v-if="selectedJournal === 'log'">
                              <BigTable
                               ref="weighingsTable"
                                  type="weighings"
                                  :filter-id="filterId"
                                  :filter-date-range="dateRange"
                                  @update:selectedItems="selectedItems = $event"
                              />
                            </div>
                            <div v-else-if="selectedJournal === 'history'">
                              <BigTable
                              ref="operationTable"
                                  type="operation"
                                  :filter-id="filterId"
                                  :filter-date-range="dateRange"
                                  @update:selectedItems="selectedItems = $event"
                              />
                            </div>
                        </Transition>
                    </div>
                </div>
            </Transition>
        </div>
    </div>
</template>



<script setup>
import { ref, computed, nextTick } from 'vue'
import { useCowsStore } from '../stores/cows'
import { useReportsStore } from '../stores/reports'
const reportsStore = useReportsStore();
import JSZip from 'jszip';

import Header from '../components/ui/head.vue'
import TabBar from '../components/ui/tabBar.vue'
import DragDropUpload from '../components/ui/DragDropUpload.vue'
import FileItem from '../components/ui/fileItem.vue'
import MinTable from '../components/ui/minTable.vue'
import Button from '../components/ui/button.vue'
import Lable from '../components/ui/label.vue'
import Input from '../components/ui/input.vue'
import BigTable from '../components/ui/bigTable.vue'
const selectedItems = ref([]);
const userEmail = ref('user@example.com')
const currentTab = ref('upload')
const selectedAnimalTab = ref('one')
const selectedJournal = ref('log')
const selectedAnimalId = ref('')
const isCalculating = ref(false) // при расчёте
const selectedExportTab = ref('excel')
const fileItems = ref([])
const uploadedImageINfo = ref(null) // ответ сервера после uploadImage
const uploadedArchiveInfo = ref(null) // ответ сервера после uploadArchive
const filterId = ref('')
const dateRange = ref({ start: null, end: null });
const weighingsTable = ref(null)
const operationTable = ref(null)

const hasActiveFilters = computed(() => {
    return filterId.value.trim() !== '' ||
        dateRange.value.start !== null ||
        dateRange.value.end !== null;
});

const cowSore = useCowsStore()

// Функция сброса
const resetFilters = () => {
    filterId.value = '';
    dateRange.value = { start: null, end: null };
};

// когда все данные есть
const isDataReady = computed(() => {
    if (selectedAnimalTab === 'one') {
        return !!selectedAnimalId.value && !!uploadedImageINfo.value
    } else {
        return !!uploadedArchiveInfo.value
    }
})

// готовность данных таблицы
const isExportDataReady = computed(() => {
  return fileItems.value.some(item => item.status === 'success')
})


// Смена варианта таблиц и отчизение старых данных
const onAnimalTabChange = (tab) => {
    selectedAnimalTab.value = tab
    fileItems.value = []
    cowSore.clearCalculatedGroup?.();
}

// Если сервер не дает id при загрузке архива
function extractIdFromFilename(filename) {
    if (!filename) return '';
    // Получаем имя файла без пути и расширения
    const name = filename.split('/').pop().split('.')[0]; // cow_001
    const parts = name.split(/[_-]/); // разделяем по _ или -
    const last = parts[parts.length - 1];
    // Если последняя часть — числа, возвращаем её
    if (/^\d+$/.test(last)) return last;
    // иначе возвращаем всё имя без расширения как fallback
    return name;
}

// функция для извлечения файлов из ZIP — возвращаем blob + objectURL
async function extractArchiveFiles(zipFile) {
    const reader = new FileReader();

    return new Promise((resolve, reject) => {
        reader.onload = async (e) => {
            try {
                const zip = await JSZip.loadAsync(e.target.result);
                const extractedFiles = [];
                const promises = [];

                zip.forEach((relativePath, file) => {
                    if (file.dir) return;

                    promises.push(
                        file.async('blob').then(blob => {
                            const url = URL.createObjectURL(blob); // object URL для быстрого превью
                            extractedFiles.push({
                                name: relativePath,
                                size: blob.size,
                                type: blob.type || guessTypeByName(relativePath),
                                blob,
                                url,
                                addedTime: new Date()
                            });
                        })
                    );
                });

                await Promise.all(promises);
                resolve(extractedFiles);
            } catch (err) {
                reject(err);
            }
        };

        reader.onerror = reject;
        reader.readAsArrayBuffer(zipFile);
    });
}

function guessTypeByName(name) {
    const ext = (name.split('.').pop() || '').toLowerCase();
    if (['jpg', 'jpeg'].includes(ext)) return 'image/jpeg';
    if (['png'].includes(ext)) return 'image/png';
    return 'application/octet-stream';
}


// Получение данных файла
const onFileAdded = (metaItems, rawFiles, variant) => {
    if (!rawFiles.length) return;

    rawFiles.forEach(async (file, i) => {
        const meta = metaItems[i];

        // Если это изображение
        if (variant === 'image') {
            fileItems.value.push({
                id: crypto.randomUUID(),
                name: file.name,
                size: file.size,
                file,
                loaded: 0,
                progress: 0,
                status: 'pending',
                result: null,
                animal_id: meta.animal_id || '',
                uploadTime: null,
                variant: 'image',
            });
        }

        // Если это архив — добавляем ОДИН элемент с типом 'archive' и сохраняем извлечённые файлы для превью
        if (variant === 'archive') {
            try {
                const extractedFiles = await extractArchiveFiles(file); // JSZip извлечение для превью

                if (extractedFiles.length === 0) {
                    console.warn('Архив пустой или не содержит изображений');
                    return;
                }

                fileItems.value.push({
                    id: crypto.randomUUID(),
                    name: file.name,
                    size: file.size,
                    file: file,
                    loaded: 0,
                    progress: 0,
                    status: 'pending',
                    result: null,
                    animal_id: '',
                    uploadTime: null,
                    variant: 'archive',
                    extractedFiles: extractedFiles
                });
            } catch (err) {
                console.error('Ошибка извлечения архива:', err);
            }
        }
    });
};

// ОТправлени данных для расчета на сервер
async function handlCalculate() {
    if (!canCalculate.value || isCalculating.value) return;

    isCalculating.value = true;

    try {
        const itemsCopy = [...fileItems.value];

        for (let idx = 0; idx < itemsCopy.length; idx++) {
            const item = itemsCopy[idx];
            const currentItem = fileItems.value.find(f => f.id === item.id);

            if (!currentItem) continue;

            // --- ОДИНОЧНОЕ ИЗОБРАЖЕНИЕ ---
            if (item.variant === 'image') {
                if (!item.animal_id || !item.animal_id.trim()) {
                    currentItem.status = 'error';
                    currentItem.errorMessage = 'Нет ID животного';
                    continue;
                }

                currentItem.status = 'uploading';
                currentItem.loaded = 0
                currentItem.progress = 0
                currentItem.size = item.file.size

                const result = await cowSore.uploadImage(
                    item.file,
                    item.animal_id,
                    (loaded, total) => {
                        currentItem.loaded = loaded
                        currentItem.progress = Math.round((loaded / total) * 100)
                    }
                )

                if (!result.success) {
                    currentItem.status = 'error';
                    currentItem.errorMessage = result.error || 'Ошибка обработки';
                    continue;
                }

                currentItem.status = 'processing'

                const fileResult = result.data.files?.[0] || result.data;

                // Обновляем текущий элемент
                currentItem.result = fileResult;
                currentItem.weight = Math.round(fileResult.weight) ?? null;
                currentItem.animal_id = item.animal_id;
                currentItem.status = 'success';
                currentItem.progress = 100

                currentItem.uploadTime = fileResult.created_at
                    ? new Date(fileResult.created_at)
                    : new Date();

                continue;
            }

            // --- ZIP-АРХИВ ---
            if (item.variant === 'archive') {
                currentItem.loaded = 0
                currentItem.progress = 0
                currentItem.status = 'uploading';

                const result = await cowSore.uploadArchive(item.file); // один запрос — весь архив

                if (!result.success) {
                    currentItem.status = 'error';
                    currentItem.errorMessage = result.error || 'Ошибка загрузки архива';
                    continue;
                }

                currentItem.loaded = currentItem.size
                currentItem.progress= 100
                currentItem.status = 'processing'

                const details = result.data.details || [];
                const summary = result.data?.summary;

                if (summary) {
                    cowSore.setCalculatedGroup({
                        count: summary.animal_count,
                        averageWeight: summary.average_weight,
                        totalWeight: summary.total_weight
                    });
                }

                if (!details.length) {
                    currentItem.status = 'error';
                    currentItem.errorMessage = 'В архиве нет поддерживаемых изображений';
                    continue;
                }

                // Создаём новые элементы для каждого файла из ответа сервера
                const newItems = details.map((detail) => {
                    const extracted = item.extractedFiles.find(ef => {
                        if (!ef?.name) return false;
                        return ef.name.split('/').pop() === detail.filename;
                    }) || {};


                    return {
                        id: crypto.randomUUID(),
                        variant: 'image',
                        fromArchive: true,
                        name: detail.filename || 'unknown.jpg',
                        size: extracted.size ?? detail.size ?? 0,
                        file: extracted.blob || null, // для превью
                        loaded: extracted.size ?? detail.size ?? 0,
                        progress: 100,
                        status: detail.status === 'success' ? 'success' : 'error',
                        result: detail,
                        weight: Math.round(detail.weight) ?? null,
                        animal_id: detail.animal_id ?? extractIdFromFilename(detail.filename),
                        uploadTime: detail.created_at ? new Date(detail.created_at) : new Date(),
                        errorMessage: detail.status === 'error' ? detail.error : undefined
                    };
                });

                // Заменяем элемент архива на список обработанных файлов
                const currentIdx = fileItems.value.findIndex(f => f.id === item.id);
                if (currentIdx !== -1) {
                    fileItems.value.splice(currentIdx, 1, ...newItems);
                }

                // Пропускаем добавленные элементы в цикле
                idx += newItems.length - 1;
                continue;
            }
            console.log('ARCHIVE RESPONSE:', result.data);
        }
    } catch (e) {
        console.error('Ошибка в handlCalculate:', e);
    } finally {
        isCalculating.value = false;
    }
}

const checkIfReady = ({ id, animal_id }) => {
    const file = fileItems.value.find(f => f.id === id);
    if (file) {
        file.animal_id = animal_id?.trim() || '';
    }
};

const canCalculate = computed(() => {
    return fileItems.value.length > 0 &&
        fileItems.value.every(item => {
            if (item.variant === 'image') {
                return item.animal_id && item.animal_id.trim() !== '';
            }
            if (item.variant === 'archive') {
                return true;
            }
            return false;
        });
});

// удаление загруженнго файла
const removeFile = (fileId) => {
    const index = fileItems.value.findIndex(item => item.id === fileId)
    if (index !== -1) {
        const fileToRemove = fileItems.value[index]
        if (fileToRemove.abortController) {
            fileToRemove.abortController.abort()
        }
        fileItems.value.splice(index, 1)
    }
}


// === Генерация и скачивание отчёта ===
async function handleExport() {
  if (isCalculating.value || !isExportDataReady.value) return;

  let payload = {
    format: selectedExportTab.value === 'pdf' ? 'pdf' : 'excel',
    report_type: 'summary',
    include_images: false,
  };

  // 🔹 Если выбрана вкладка "История взвешиваний"
  if (selectedJournal.value === 'log') {
    payload.include_weighs = selectedItems.value;
  }

  // 🔹 Если выбрана вкладка "Операции" (батчи)
  if (selectedJournal.value === 'history') {
    const allDetectionIds = [];

    for (const batchNumber of selectedItems.value) {
      const batch = cowSore.batchStats.items.find(b => b.batch_number === batchNumber);
      if (batch && Array.isArray(batch.detection_ids)) {
        allDetectionIds.push(...batch.detection_ids);
      }
    }

    if (allDetectionIds.length === 0) {
      alert('Нет данных для экспорта: выбранные батчи не содержат взвешиваний');
      return;
    }

    payload.include_weighs = allDetectionIds;
  }

  console.log('Формируем отчёт с payload:', payload);

  // Генерируем отчёт
  const res = await reportsStore.generateReport(payload);

  if (!res.success) {
    alert('Ошибка генерации: ' + res.error);
    return;
  }

  const reportId = res.data.report_id;
  console.log('Отчёт сгенерирован, ID:', reportId);

  // Ждём 10 секунд (лучше — polling, но пока так)
  await new Promise(resolve => setTimeout(resolve, 10000));

  // Скачиваем
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Токен не найден');
      return;
    }

    const url = `${import.meta.env.VITE_API_BASE_URL}/reports/${reportId}/download`;
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 200) {
      const blob = await response.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${reportId}.${payload.format === 'excel' ? 'xlsx' : 'pdf'}`;
      a.click();
      URL.revokeObjectURL(a.href);
    } else {
      alert(`Ошибка скачивания: ${response.status}`);
    }
  } catch (error) {
    console.error('Ошибка скачивания:', error);
    alert('Не удалось скачать файл');
  }
}

function exportSelected() {
  let activeTable = selectedJournal.value === 'log' ? weighingsTable.value : operationTable.value

  if (activeTable) {
    activeTable.downloadSelected(selectedExportTab.value)
  }
}

const handleLogout = () => {
    // логика выхода
}
</script>

<style scoped lang="scss">
@use '../assets/styles/components/HomeView';
</style>
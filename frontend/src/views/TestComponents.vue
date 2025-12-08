<template>
  <div class="component-test-view">
    <h1 class="text-h1">🧪 Тест компонентов</h1>

    <section>
      <h2 class="text-h2">1. HeaderBar — Шапка</h2>
      <HeaderBar email="user@farm.com" />
    </section>

    <section>
      <h2 class="text-h2">2. TabBar — Вкладки</h2>
      <div class="tab-examples">
        <TabBar variant="animals" />
        <TabBar variant="small" />
        <TabBar variant="export" />
        <TabBar variant="export-small" />
      </div>
    </section>

    <section>
      <h2 class="text-h2">3. AppInput — Поля ввода</h2>
      <div class="input-examples">
        <AppInput v-model="inputText" placeholder="Обычный инпут" />
        <AppInput v-model="inputPassword" type="password" placeholder="Пароль" />
        <AppInput
            v-model="dateRange"
            type="daterange"
            placeholder="Выберите период"
            variant="calendar-green"
        />
        <AppInput
            v-model="inputError"
            placeholder="С ошибкой"
            error="Поле обязательно"
        />
      </div>
    </section>

    <section>
      <h2 class="text-h2">4. AppButton — Кнопки</h2>
      <div class="button-examples">
        <AppButton>Обычная кнопка</AppButton>
        <AppButton variant="upload">Кнопка загрузки</AppButton>
        <AppButton loading>Загрузка...</AppButton>
        <AppButton disabled>Отключена</AppButton>
      </div>
    </section>

    <section>
      <h2 class="text-h2">5. AppLabel — Метки</h2>
      <div class="label-examples">
        <AppLabel forId="input1">Имя пользователя</AppLabel>
        <AppLabel forId="input2" required>Обязательное поле</AppLabel>
      </div>
    </section>

    <section>
      <h2 class="text-h2">6. FileItem — Файлы</h2>
      <div class="file-examples">
        <FileItem :file="{ name: 'report.pdf', loaded: 2_500_000, total: 5_000_000 }" />
        <FileItem :file="{ name: 'photo.jpg', loaded: 5_000_000, total: 5_000_000 }" />
        <FileItem :file="{ name: 'data.raw', loaded: 1_000_000, total: 5_000_000 }" />
      </div>
    </section>

    <!-- === DRAG & DROP: Загрузка фото === -->
    <section>
      <h2 class="text-h2">7. Загрузка изображения</h2>
      <DragAndDrop variant="image" />
    </section>

    <!-- === DRAG & DROP: Загрузка архива === -->
    <section>
      <h2 class="text-h2">8. Загрузка ZIP-архива</h2>
      <DragAndDrop variant="archive" />
    </section>

    <!-- === ТАБЛИЦА: Полная таблица === -->
    <section>
      <h2 class="text-h2">9. BigTable — Полная таблица</h2>
      <div v-if="cowsStore.history.loading" class="loading">Загрузка данных с сервера...</div>
      <div v-else-if="cowsStore.history.error" class="error">Ошибка: {{ cowsStore.history.error }}</div>
      <BigTable v-else />
    </section>

    <!-- === ТАБЛИЦА: Мини-таблица === -->
    <section>
      <h2 class="text-h2">10. MinTable — Упрощённая таблица</h2>
      <div class="min-table-wrapper">
        <h3 class="text-h4">Мини-таблица (по умолчанию)</h3>
        <MinTable type="default" />
      </div>
      <div class="min-table-wrapper">
        <h3 class="text-h4">Мини-таблица (коровы)</h3>
        <MinTable type="cows" />
      </div>
    </section>

    <!-- === СТАТУС: Данные из API === -->
    <section>
      <h2 class="text-h2">11. Статус загрузки данных</h2>
      <div class="store-preview">
        <p class="text-h5">Записей в истории: <strong>{{ cowsStore.history.data.length }}</strong></p>
        <p>Загружено со страницы {{ cowsStore.history.page }} (всего страниц: {{ cowsStore.history.total_pages }})</p>
        <p v-if="cowsStore.history.error" style="color: #d32f2f">❌ Ошибка: {{ cowsStore.history.error }}</p>
        <p v-else-if="!cowsStore.history.loading" style="color: #4caf50">✅ Данные успешно загружены</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import HeaderBar from '../components/ui/head.vue';
import TabBar from '../components/ui/tabBar.vue';
import AppInput from '../components/ui/input.vue';
import AppButton from '../components/ui/button.vue';
import AppLabel from '../components/ui/label.vue';
import FileItem from '../components/ui/fileItem.vue';
import DragAndDrop from '../components/ui/DragDropUpload.vue';
import BigTable from '../components/ui/bigTable.vue';
import MinTable from '../components/ui/minTable.vue';
import { useCowsStore } from '../stores/cows.js';
import { onMounted } from 'vue';

// Инициализация стора
const cowsStore = useCowsStore();

// Для теста инпутов
import { ref } from 'vue';
const inputText = ref('');
const inputPassword = ref('');
const dateRange = ref([]);
const inputError = ref('');

// Загружаем историю при открытии
onMounted(async () => {
  await cowsStore.fetchHistory({
    page: 1,
    limit: 20,
  });
});
</script>

<style scoped lang="scss">
.component-test-view {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
}

section {
  margin-bottom: 48px;
}

h2 {
  margin-bottom: 16px;
}

.tab-examples,
.input-examples,
.button-examples,
.label-examples,
.file-examples {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-examples {
  align-items: flex-start;
}

.min-table-wrapper {
  margin-bottom: 24px;
}

.store-preview {
  padding: 16px;
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 8px;
  font-size: 14px;
}

.loading {
  padding: 20px;
  text-align: center;
  color: #666;
  font-style: italic;
}

.error {
  padding: 20px;
  text-align: center;
  color: #d32f2f;
}
</style>
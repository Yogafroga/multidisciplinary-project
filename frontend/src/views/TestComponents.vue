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

    <!-- === DRAG & DROP: РЕЖИМ 1 — ФОТО === -->
    <section>
      <h2 class="text-h2">7. DragDropUpload — Загрузка фото</h2>
      <DragAndDrop variant="image" />
    </section>

    <!-- === DRAG & DROP: РЕЖИМ 2 — АРХИВ === -->
    <section>
      <h2 class="text-h2">8. DragDropUpload — Загрузка архива</h2>
      <DragAndDrop variant="archive" />
    </section>

    <!-- === ТЕСТ: ДАННЫЕ ИЗ СТОРА === -->
    <section>
      <h2 class="text-h2">9. Данные из стора `useCowsStore`</h2>
      <div class="store-preview">
        <p class="text-h5">Всего записей в истории: <strong>{{ cowsStore.history.data.length }}</strong></p>

        <div v-if="cowsStore.history.data.length === 0" class="empty">
          Пока нет загруженных изображений
        </div>
        <ul v-else class="history-list">
          <li v-for="item in cowsStore.history.data" :key="item.id" class="history-item">
            🐄 <strong>Корова {{ item.animal_id }}</strong> — {{ item.weight }} кг,
            {{ new Date(item.created_at).toLocaleString() }}
          </li>
        </ul>
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

// 🔹 Импорт стора
import { useCowsStore } from '../stores/cows.js';

const cowsStore = useCowsStore();

// Для теста инпутов
import { ref } from 'vue';
const inputText = ref('');
const inputPassword = ref('');
const dateRange = ref([]);
const inputError = ref('');
</script>

<style scoped lang="scss">
.component-test-view {
  padding: 32px;
  max-width: 1000px;
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

/* === Стили для просмотра стора === */
.store-preview {
  padding: 16px;
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 8px;
  font-size: 14px;
}

.history-list {
  list-style: none;
  padding: 0;
  margin-top: 10px;
}

.history-item {
  padding: 8px 12px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #271f12;
}

.empty {
  color: #999;
  font-style: italic;
  padding: 10px 0;
}
</style>
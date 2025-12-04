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
  </div>
</template>

<script setup>
import HeaderBar from '../components/ui/head.vue';
import TabBar from '../components/ui/tabBar.vue';
import AppInput from '../components/ui/input.vue';
import AppButton from '../components/ui/button.vue';
import AppLabel from '../components/ui/label.vue';
import FileItem from '../components/ui/fileItem.vue';

import { ref } from 'vue';

// Для теста инпутов
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
</style>
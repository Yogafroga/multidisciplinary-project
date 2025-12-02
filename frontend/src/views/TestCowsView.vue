<template>
  <div class="view">
    <h1>🐄 История взвешиваний</h1>

    <button @click="cows.fetchHistory()">Загрузить историю</button>
    <div v-if="cows.historyLoading">Загрузка...</div>
    <ul v-else-if="cows.history.data.length">
      <li v-for="item in cows.history.data" :key="item.id">
        <strong>Корова {{ item.animal_id }}</strong>
        — {{ item.weight }} кг,
        {{ new Date(item.created_at).toLocaleString() }}
        <button @click="deleteItem(item.id)">Удалить</button>
      </li>
    </ul>
    <div v-else class="empty">Нет данных</div>

    <hr />

    <h2>Загрузить изображение</h2>
    <input type="file" @change="onFileChange" accept="image/*" />
    <input v-model="animalId" placeholder="ID коровы" />
    <button @click="uploadImage">Загрузить</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useCowsStore } from '../stores/cows.js';

const cows = useCowsStore();
const animalId = ref('001');
const selectedFile = ref(null);

const onFileChange = (e) => {
  selectedFile.value = e.target.files[0];
};

const deleteItem = async (id) => {
  if (confirm('Удалить запись?')) {
    await cows.deleteRecord(id);
  }
};

const uploadImage = async () => {
  if (!selectedFile.value || !animalId.value) {
    alert('Выберите файл и укажите ID');
    return;
  }
  const result = await cows.uploadImage(selectedFile.value, animalId.value);
  if (result.success) {
    alert('Изображение загружено!');
  } else {
    alert('Ошибка: ' + result.error);
  }
  selectedFile.value = null;
};
</script>

<style scoped>
.view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

button {
  padding: 8px 16px;
  margin: 5px;
  background: #4361ee;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

input {
  padding: 8px;
  margin: 5px 0 10px;
  width: 300px;
  border: 1px solid #271f12;
  border-radius: 4px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 10px;
  border: 1px solid #ddd;
  margin-bottom: 8px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
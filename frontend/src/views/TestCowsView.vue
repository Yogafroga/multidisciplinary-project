<template>
  <div class="view">
    <h1>История взвешиваний</h1>

    <button @click="loadHistory">Загрузить историю</button>
    <div v-if="loading">Загрузка...</div>
    <ul v-else-if="history.length">
      <li v-for="item in history" :key="item.id">
        <strong>Корова {{ item.animal_id }}</strong>
        — {{ item.weight }} кг,
        {{ new Date(item.created_at).toLocaleString() }}
        <button @click="deleteItem(item.id)">Удалить</button>
      </li>
    </ul>
    <div v-else-if="!loading" class="empty">Нет данных</div>

    <hr />

    <h2>Загрузить изображение</h2>
    <input type="file" @change="onFileChange" accept="image/*" />
    <input v-model="animalId" placeholder="ID коровы" />
    <button @click="uploadImage">Загрузить</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const history = ref([]);
const loading = ref(false);
const animalId = ref('001');
const selectedFile = ref(null);

// Мок загрузки истории
const loadHistory = async () => {
  loading.value = true;
  // Имитация задержки
  await new Promise(resolve => setTimeout(resolve, 800));
  history.value = [
    {
      id: 1,
      animal_id: '001',
      weight: 450.5,
      confidence: 0.92,
      created_at: '2024-01-15T10:30:00Z',
    },
    {
      id: 2,
      animal_id: '002',
      weight: 460.1,
      confidence: 0.89,
      created_at: '2024-01-16T11:00:00Z',
    },
  ];
  loading.value = false;
};

// Удаление записи
const deleteItem = (id) => {
  if (confirm('Удалить запись?')) {
    history.value = history.value.filter(item => item.id !== id);
  }
};

// Выбор файла
const onFileChange = (e) => {
  selectedFile.value = e.target.files[0];
};

// Мок загрузки изображения
const uploadImage = () => {
  if (!selectedFile.value || !animalId.value) {
    alert('Выберите файл и укажите ID коровы');
    return;
  }
  const newEntry = {
    id: Date.now(),
    animal_id: animalId.value,
    weight: (450 + Math.random() * 30).toFixed(1),
    created_at: new Date().toISOString(),
  };
  history.value.unshift(newEntry);
  alert('Изображение загружено (мок)');
  selectedFile.value = null;
  animalId.value = '001';
};
</script>

<style scoped>
.view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1, h2 {
  color: #271f12;
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

button:hover {
  background: #3a0ca3;
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

.empty {
  color: #999;
  font-style: italic;
}

hr {
  margin: 30px 0;
  border: 1px solid #eee;
}
</style>
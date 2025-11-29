// frontend/src/main.js
import './assets/styles/main.scss'; // Импорт CSS-файла
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

// Импорт vue-good-table
import VueGoodTablePlugin from 'vue-good-table';
import 'vue-good-table/dist/vue-good-table.css';

// Импорт VueDatePicker
import { VueDatePicker } from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

const app = createApp(App);
const pinia = createPinia();

// Использование vue-good-table плагина
app.use(VueGoodTablePlugin);

// Регистрация VueDatePicker как глобального компонента
app.component('VueDatePicker', VueDatePicker);

app.use(pinia);
app.use(router);

app.mount('#app');
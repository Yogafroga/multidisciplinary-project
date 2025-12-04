import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore} from "../stores/auth.js";

import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import MainView from "../views/MainView.vue";
import TestCowsView from "../views/TestCowsView.vue";
import TestReportsView from "../views/TestReportsView.vue";
import TestComponents from "../views/TestComponents.vue";

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/cows', component: TestCowsView }, // TODO: удалить после тестов
    { path: '/reports', component: TestReportsView }, // TODO: удалить после тестов
    { path: '/test', component: TestComponents }, // TODO: удалить после тестов
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    {
        path: '/main',
        component: MainView,
        meta: { requiresAuth: true },
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Глобальный guard
router.beforeEach((to, from, next) => {
    const auth = useAuthStore();

    if (to.meta.requiresAuth && !auth.isAuthenticated()) {
        next('/login');
    } else if ((to.path === '/login' || to.path === '/register') && auth.isAuthenticated()) {
        next('/main');
    } else {
        next();
    }
});

export default router;

import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from "../stores/auth.js";

import AuthView from "../views/AuthView.vue";
import HomeView from "../views/HomeView.vue";

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: AuthView },
    { path: '/register', component: AuthView },
    {
        path: '/home',
        component: HomeView,
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
        next('/home');
    } else {
        next();
    }
});

export default router;

-- add_user.sql
-- Переопределите значения LOGIN / PLAINTEXT_PASSWORD / ROLE по необходимости.
-- Генерирует bcrypt-хеш в Postgres (pgcrypto) и вставляет роль + пользователя.
-- Не выполняет никаких изменений, если запись уже существует.

BEGIN;

-- 1) Убедиться, что расширение доступно (требует superuser)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2) Создать роль (если ещё нет)
INSERT INTO user_roles (role)
VALUES ('admin')
ON CONFLICT (role) DO NOTHING;

-- 3) Вставить пользователя с bcrypt-хешем (cost = 12)
INSERT INTO users (login, password_hash, role_id)
VALUES (
  'NEW_USER', -- <- замените на нужный логин
  crypt('NEW_USER_PASSWORD', gen_salt('bf', 12)), -- <- замените пароль
  (SELECT id FROM user_roles WHERE role = 'admin')
)
ON CONFLICT (login) DO NOTHING;

COMMIT;
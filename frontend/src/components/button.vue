<template>
    <button class="app-button" :class="[
        variant,
        { loading, disabled }
    ]" :disabled="disabled || loading" @click="handleClick">
        <span v-if="!loading">
            <slot />
        </span>

        <img v-else src="../assets/images/loading.svg" class="loader"></img>
    </button>
</template>

<script setup>
const props = defineProps({
    loading: {
        type: Boolean,
        default: false
    },
    disabled: {
        type: Boolean,
        default: false
    },
    variant: {
        type: String,
        default: "primary"
    }
})

const emit = defineEmits(["click"])

function handleClick(event) {
    if (!props.loading && !props.disabled) {
        emit("click", event)
    }
}
</script>

<style scoped lang="scss">
@use "../assets/styles/variables.scss" as *;
@use "../assets/styles/base/_typography.scss" as *;
@use "sass:color";

.app-button {
    display: flex;
    justify-content: center;
    align-items: center;

    width: 366px;
    height: 43px;
    padding: 16px 8px;
    border-radius: 12px;

    border: 1px solid #271F12;

    font-size: 16px;
    font-weight: $font-weight-regular;
    transition: 0.25s;
    user-select: none;
}

/* ВАРИАНТЫ КНОПКИ */
.app-button.primary {
    background-color: $color-headline;
}

.app-button.primary:hover:not(.disabled):not(.loading) {
    background-color: color.scale($color-headline, $alpha: -25%);
}

.app-button.primary:active:not(.disabled):not(.loading) {
    background-color: $color-background-2;
}

/* СОСТОЯНИЕ LOADING */
.app-button.loading {
    cursor: wait;
    opacity: 0.8;
}

/* Кружок загрузки */
.loader {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    animation: spin 1.5s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* DISABLED СОСТОЯНИЕ */
.app-button.disabled {
    background-color: $color-background-2;
    cursor: default;
}
</style>

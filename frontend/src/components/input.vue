<template>
    <div class="app-input" :class="[variant, {error: error}]">
        <div class="input-wrapper">
            <input 
            :id="id"
            :type="type === 'password' ? (isVisible ? 'text' : 'password') : type"
            :placeholder="placeholder" 
            :value="modelValue"
            @input="updateValue($event.target.value)" />

            <span 
            class="eye" 
            v-if="type === 'password'" 
            @click="toggleVisibility">
                <svg v-if="!isVisible" xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none"
                    viewBox="0 0 24 24">
                    <path stroke="#444" stroke-width="2" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" />
                    <circle cx="12" cy="12" r="3" stroke="#444" stroke-width="2" />
                </svg>

                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24">
                    <path stroke="#444" stroke-width="2"
                        d="M3 3l18 18M10.73 5.08C11.15 5.03 11.57 5 12 5c7 0 11 7 11 7a21.8 21.8 0 0 1-3.17 4.52M6.1 6.1A21.8 21.8 0 0 0 1 12s4 7 11 7c1.86 0 3.53-.44 5-.5" />
                </svg>
            </span>
        </div>
        <span v-if="error" class="error-message">{{ error }}</span>
    </div>
</template>

<script setup>
import { ref } from 'vue';

    const props = defineProps({
        modelValue: {
            type: [String, Number],
            default: ''
        },
        type: {
            type: String,
            default: 'text'
        },
        placeholder: {
            type: String,
            default: ''
        },
        error: {
            type: String,
            default: ''
        },
        variant: {
            type: String,
            default: 'primary'
        },
        id: {
            type: String,
            default: ''
        }
    })

    const emit = defineEmits(['update:modelValue'])

    const isVisible = ref(false)

    const toggleVisibility = () => {
        isVisible.value = !isVisible.value
    }

    const updateValue = (value) => {
        emit('update:modelValue', value)
    }
</script>

<style scoped lang="scss">
    @use "../assets/styles/variables.scss" as *;
    @use "../assets/styles/base/_typography.scss" as *;
    @use "sass:color";

    .app-input {
        display: flex;
        justify-content: flex-start;
        align-items: flex-start; 
        flex-direction: column;
    }

    input {
        width: 366px;
        height: 37px;
        padding: 16px 8px;
        border: 1px solid #271F12;
        border-radius: 12px;
        opacity: 1;

        font-size: 14px;
        font-family: $font-family-primary;
        font-weight: $font-weight-regular;
    }

    .input-wrapper {
        position: relative;
        width: 366px;
    }

    .eye {
        position: absolute;
        top: 50%;
        right: 10px;
        transform: translateY(-50%);
        cursor: pointer;
        display: flex;
        align-items: center;
    }

    .error-message {
        display: flex;
        justify-content: flex-start;
        align-items: center;

        width: 313px;
        height: 34px;
        padding: 10px;
        color: #CC4E4E;

        text-align: left;
        vertical-align: center;
        font-size: $font-size-h6;
    }

    .app-input.error input {
        border-color: #CC4E4E;
    }
</style>
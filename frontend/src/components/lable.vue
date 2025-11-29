<template>
    <label :for="forId" class="app-lable">
        <slot />
        <span v-if="required" class="required">*</span>
    </label>
</template>

<script setup>
    const props = defineProps({
        forId: {
            type: String,
            default: ''
        },
        required: {
            type: Boolean,
            default: false
        },
    });
</script>

<style scoped lang="scss">
    @use "../assets/styles/variables.scss" as *;
    @use "../assets/styles/base/_typography.scss" as *;

    .app-lable {
        display: block;

        font-family: $font-family-primary;
        font-size: 16px;
        font-weight: $font-weight-regular;
        color: $text-color-primary;
    }
</style>
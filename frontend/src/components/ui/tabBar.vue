<template>
    <div class="tab-bar" :class="{ small: isSmall }">
        <div v-for="tab in tabs" :key="tab.value" class="tab" :class="{ selected: selectedTab === tab.value }"
            @click="selectTab(tab.value)">
            {{ tab.label }}
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
    isSmall: { type: Boolean, default: false },
})

const selectedTab = ref(props.isSmall ? 'log' : 'one')

const tabs = computed(() => {
    if (props.isSmall) {
        return [
            { value: 'log', label: 'Журнал животных' },
            { value: 'history', label: 'История операций' }
        ]
    } else {
        return [
            { value: 'one', label: 'Одно животное' },
            { value: 'group', label: 'Группа животных' }
        ]
    }
})

function selectTab(tab) {
    selectedTab.value = tab
}
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/tabBar';
</style>

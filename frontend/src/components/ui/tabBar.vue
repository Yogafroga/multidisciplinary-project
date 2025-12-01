<template>
    <div class="tab-bar" :class="variantClass">
        <div v-for="tab in tabs" :key="tab.value" class="tab" :class="[
            { selected: selectedTab === tab.value },
            sizeClass
        ]" @click="selectTab(tab.value)">
            <component :is="tab.icon" class="tab-icon" />
            {{ tab.label }}
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Pdf_M from '../../assets/icons/files/Pdf_M.vue'
import Pdf_S from '../../assets/icons/files/Pdf_S.vue'
import X_M from '../../assets/icons/files/X_M.vue'
import X_S from '../../assets/icons/files/X_S.vue'

const props = defineProps({
    variant: {
        type: String,
        default: "animals"
        /*
            animals — большой таб: Одно / Группа  
            small — маленький таб: Журнал / История  
            export — большой Excel / PDF  
            export-small — маленький Excel / PDF
        */
    },
})

const selectedTab = ref(null)

const tabs = computed(() => {
    switch (props.variant) {
        case "animals":
            selectedTab.value ??= "one"
            return [
                { value: "one", label: "Одно животное" },
                { value: "group", label: "Группа животных" }
            ]

        case "small":
            selectedTab.value ??= "log"
            return [
                { value: "log", label: "Журнал животных" },
                { value: "history", label: "История операций" }
            ]

        case "export":
            selectedTab.value ??= "excel"
            return [
                { value: "excel", label: "Excel", icon: X_M },
                { value: "pdf", label: "PDF", icon: Pdf_M }
            ]

        case "export-small":
            selectedTab.value ??= "excel"
            return [
                { value: "excel", label: "Excel", icon: X_S },
                { value: "pdf", label: "PDF", icon: Pdf_S }
            ]
    }
})

const sizeClass = computed(() => {
    return props.variant.includes("small") ? "tab-small" : "tab-big"
})

const variantClass = computed(() => {
    return props.variant
})

function selectTab(tab) {
    selectedTab.value = tab
}
</script>

<style scoped lang="scss">
@use '../../assets/styles/components/tabBar';
</style>

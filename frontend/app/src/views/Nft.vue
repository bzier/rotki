<template>
  <v-container>
    <module-not-active :modules="modules" />
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api';
import ModuleNotActive from '@/components/defi/ModuleNotActive.vue';
import { setupModuleEnabled } from '@/composables/session';
import { Module } from '@/types/modules';

export default defineComponent({
  name: 'Nft',
  components: { ModuleNotActive },
  setup() {
    const module = Module.NFTS;
    const { isModuleEnabled } = setupModuleEnabled();
    return {
      isEnabled: isModuleEnabled(module),
      modules: [module]
    };
  }
});
</script>

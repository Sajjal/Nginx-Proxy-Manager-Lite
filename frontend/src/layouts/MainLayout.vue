<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container :style="isPC ? 'width: 60vw' : 'width:100vw'" class="fixed-center scrolling">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue';
import store from '../store/index';
import { useQuasar } from 'quasar';

export default defineComponent({
  name: 'MainLayout',
  components: {},
  setup() {
    const $q = useQuasar();
    let isPC = $q.platform.is.mobile ? false : true;
    return {
      store,
      isPC
    };
  }
});
</script>

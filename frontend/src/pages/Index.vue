<template>
  <q-page class="q-pa-md shadow-4 bg-black">
    <q-banner inline-actions rounded class="text-white bg-primary q-pa-md q-mb-md" style="overflow: hidden">
      <q-btn flat round dense icon="settings_input_antenna" class="q-mr-md" @click="goto_home" />
      <span class="text-h6" style="cursor: default" v-if="isPC"> Nginx Proxy Manager Lite </span>
      <span class="text-h6" style="cursor: default" v-else> NPM Lite </span>

      <template v-slot:action>
        <q-btn dense flat round icon="person" aria-label="Account" class="q-ml-md">
          <q-menu>
            <q-list style="min-width: 80px">
              <q-item clickable v-close-popup @click="change_password">
                <q-item-section>Change Password</q-item-section>
                <q-item-section avatar>
                  <q-icon color="primary" name="password" />
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup @click="logout_user">
                <q-item-section>Logout</q-item-section>
                <q-item-section avatar>
                  <q-icon color="primary" name="logout" />
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </template>
    </q-banner>
    <div v-if="store.state.display_list">
      <q-banner inline-actions rounded class="text-black bg-grey-1 q-mb-lg" style="overflow: hidden">
        <span class="text-h6" style="cursor: default" v-if="isPC"> Available Hosts </span>
        <div style="width: 250px" v-if="!isPC">
          <q-select dense outlined v-model="filter" :options="filter_option" label="Filter" class="q-mr-xl" @update:model-value="filter_list()" />
        </div>
        <template v-slot:action>
          <div style="width: 250px" v-if="isPC">
            <q-select dense outlined v-model="filter" :options="filter_option" label="Filter" class="q-mr-xl" @update:model-value="filter_list()" />
          </div>
          <q-btn round color="primary" icon="add" dense @click="goto_add" />
        </template>
      </q-banner>

      <q-scroll-area dark v-if="list_hosts" :thumb-style="thumbStyle" class="text-white rounded-borders" :style="isPC ? 'height: 60vh' : 'height:55vh;'">
        <div v-for="domain in temp_domain_list" :key="domain.id">
          <q-item dark>
            <q-item-section avatar>
              <q-icon name="lock" v-if="domain.enableSSL" class="text-secondary" />
              <q-icon name="no_encryption" v-else class="text-grey" />
            </q-item-section>

            <q-item-section>
              <q-item-label class="text-subtitle2">{{ domain.domain }}</q-item-label>
              <q-item-label caption v-if="domain.type == 'static'"> {{ domain.static_path }} </q-item-label>
              <q-item-label caption v-if="domain.type == 'redirect'"> {{ domain.redirect_url }} </q-item-label>
              <q-item-label caption v-if="domain.type == 'reverse_proxy'"> {{ domain.ips[0].ip }} </q-item-label>
            </q-item-section>
            <q-item-section> </q-item-section>
            <q-item-section side>
              <q-toggle color="blue" v-model="activeStatus[domain.domain]" true-value="0" false-value="1" @click="enableDisable(domain.domain)" />
            </q-item-section>
            <q-item-section side>
              <q-btn flat dense round icon="edit" aria-label="Edit" @click="edit_host(domain.domain)" />
            </q-item-section>
            <q-item-section side>
              <q-btn flat dense round icon="delete" aria-label="Delete" class="text-negative" @click="delete_host(domain.domain)" />
            </q-item-section>
          </q-item>
          <q-separator dark />
        </div>
      </q-scroll-area>

      <q-scroll-area dark v-if="list_ssl" :thumb-style="thumbStyle" class="text-white rounded-borders" :style="isPC ? 'height: 60vh' : 'height:55vh;'">
        <div v-for="ssl in store.state.ssl_list" :key="ssl.id">
          <q-item dark>
            <q-item-section avatar>
              <q-icon name="lock" class="text-secondary" />
            </q-item-section>

            <q-item-section>
              <q-item-label class="text-subtitle2">{{ ssl.domain }}</q-item-label>
              <q-item-label caption> {{ ssl.cert_info.ssl_active_from }} to {{ ssl.cert_info.ssl_expiry }}</q-item-label>
            </q-item-section>
            <q-item-section> </q-item-section>
            <q-item-section side>
              <q-item-label class="text-subtitle2"></q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-item-label class="text-subtitle2">{{ ssl.cert_info.ssl_issuer }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-separator dark />
        </div>
      </q-scroll-area>
      <div class="bg-grey-1 q-mt-md q-pa-sm" style="overflow: hidden" v-if="error">
        <span class="text-subtitle2 text-red" style="cursor: default"> {{ error }} </span>
      </div>
      <div rounded class="text-black bg-grey-1 text-center q-pa-xs q-mt-md" style="overflow: hidden">
        <span style="cursor: default"> S & D Nginx Proxy Manager Lite | github: @Sajjal </span>
      </div>
    </div>
    <div class="q-mt-sm shadow-4 bg-black" v-if="store.state.display_add_form">
      <add_host />
    </div>
    <q-dialog v-model="askToConfirmDelete" persistent>
      <q-card style="min-width: 300px">
        <q-linear-progress :value="1" color="red" />
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="negative" text-color="white" />
          <span class="q-ml-sm"> </span>
          <div>
            <div class="q-ml-sm">
              Are you sure to delete <span class="text-weight-bold"> {{ selected_domain_to_delete }} </span> ?
            </div>
            <div class="q-ml-sm text-grey">You will loose all config and SSL certs related to {{ selected_domain_to_delete }} !</div>
          </div>
        </q-card-section>
        <q-card-section>
          <q-input outlined v-model="confirmDeleteDomainName" label="Enter domain name to confirm!" class="p-pa-sm" />
        </q-card-section>

        <q-card-section v-if="error">
          <div class="text-red text-subtitle2 q-px-md">{{ error }}</div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Delete" color="red" @click="confirm_delete_host" />
          <q-btn flat label="Cancel" color="primary" @click="cancel_delete_host" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { defineComponent, ref, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import store from '../store/index';
import add_host from '../components/add_host.vue';
import getServerData from '../utils/getServerData';

export default defineComponent({
  name: 'PageIndex',
  components: { add_host },
  setup() {
    const router = useRouter();
    const $q = useQuasar();
    let isPC = $q.platform.is.mobile ? false : true;
    const { error, listHosts, enableHost, disableHost, deleteHost, listSSLCerts, logout } = getServerData();

    const list_hosts = ref(true);
    const list_ssl = ref(false);

    let temp_domain_list = ref([]);

    const filter = ref(null);
    const filter_option = ref([
      { label: 'All Hosts', value: 'all_hosts' },
      { label: 'Static Hosts', value: 'static' },
      { label: 'Reverse Proxy Hosts', value: 'reverse_proxy' },
      { label: 'Redirect Hosts', value: 'redirect' },
      { label: 'SSL Certificates', value: 'ssl_certs' }
    ]);
    const activeStatus = ref({});
    const askToConfirmDelete = ref(false);
    const selected_domain_to_delete = ref(null);
    const confirmDeleteDomainName = ref(null);

    async function list_all_hosts() {
      await listHosts();
      await listSSLCerts();
      temp_domain_list.value = store.state.domain_list;
      updateActiveStatus();
    }
    list_all_hosts();

    watch(
      () => store.state.domain_list,
      () => {
        updateActiveStatus();
      },
      {
        deep: true
      }
    );

    async function filter_list() {
      list_hosts.value = true;
      list_ssl.value = false;
      temp_domain_list.value = store.state.domain_list;
      if (filter.value.value == 'all_hosts') return temp_domain_list.value;
      if (filter.value.value == 'ssl_certs') {
        list_hosts.value = false;
        list_ssl.value = true;
        await listSSLCerts();
      } else temp_domain_list.value = store.state.domain_list.filter((item) => item.type == filter.value.value);
    }

    //Update active status (toggle) of projects
    function updateActiveStatus() {
      for (let i in store.state.domain_list) {
        activeStatus.value[store.state.domain_list[i].domain] = store.state.domain_list[i].is_disabled.toString();
      }
      temp_domain_list.value = store.state.domain_list;
    }
    async function enableDisable(domain) {
      if (activeStatus.value[domain] == '0') {
        await enableHost({ domain });
        if (error.value) activeStatus.value[domain] = '1';
      } else if (activeStatus.value[domain] == '1') {
        await disableHost({ domain });
        if (error.value) activeStatus.value[domain] = '0';
      }
    }

    function edit_host(domain) {
      store.dispatch('update_edit_domain', domain);
      store.dispatch('update_display', 'add');
    }

    function delete_host(domain) {
      selected_domain_to_delete.value = domain;
      askToConfirmDelete.value = true;
    }
    async function confirm_delete_host() {
      if (confirmDeleteDomainName.value == selected_domain_to_delete.value) {
        await deleteHost({ domain: confirmDeleteDomainName.value });
        temp_domain_list.value = store.state.domain_list;
        askToConfirmDelete.value = null;
        selected_domain_to_delete.value = null;
        confirmDeleteDomainName.value = null;
        error.value = null;
      } else {
        error.value = 'Error: Invalid Domain Name!';
      }
    }
    function cancel_delete_host() {
      askToConfirmDelete.value = null;
      selected_domain_to_delete.value = null;
      confirmDeleteDomainName.value = null;
      error.value = null;
    }

    function goto_home() {
      store.dispatch('update_edit_domain', null);
      store.dispatch('update_display', 'list');
    }
    function goto_add() {
      store.dispatch('update_display', 'add');
    }

    function change_password() {
      store.dispatch('update_change_password', { change: true, afterLogin: true });
      router.push({ name: 'Login' });
    }

    async function logout_user() {
      await logout();
    }

    return {
      isPC,
      thumbStyle: { width: '0px' },
      store,
      temp_domain_list,
      list_hosts,
      edit_host,
      delete_host,
      list_ssl,
      filter_list,
      goto_home,
      goto_add,
      change_password,
      logout_user,
      askToConfirmDelete,
      selected_domain_to_delete,
      confirmDeleteDomainName,
      activeStatus,
      enableDisable,
      confirm_delete_host,
      cancel_delete_host,
      filter,
      filter_option,
      error
    };
  }
});
</script>

<template>
  <q-banner rounded class="text-black bg-grey-1 q-mb-md" style="overflow: hidden">
    <span class="text-h6" style="cursor: default"> {{ pageTitle }} </span>
  </q-banner>
  <div>
    <q-input dark dense outlined v-model="domain" label="Domain" />
    <q-scroll-area dark :thumb-style="thumbStyle" class="text-white" :style="isPC ? 'height: 55vh' : 'height:42vh;'">
      <div class="q-pt-md text-white">
        <q-radio dark v-model="type" val="static" label="Static" />
        <q-radio dark v-model="type" val="reverse_proxy" label="Reverse Proxy" color="secondary" class="q-pl-md" />
        <q-radio dark v-model="type" val="redirect" label="Redirect 301" color="purple" class="q-pl-md" />
      </div>
      <q-input v-if="type == 'static'" dark dense outlined v-model="static_path" label="Static Path /" class="q-mt-md" />
      <q-input v-if="type == 'redirect'" dark dense outlined v-model="redirect_url" label="Redirect Url" class="q-mt-md" />
      <div v-if="type == 'reverse_proxy'">
        <div v-for="(ip, index) in ips" :key="`ip-${index}`" :class="isPC ? 'row' : ''">
          <q-input dark dense outlined v-model="ip.ip" label="Forward ip/hostname" class="q-mt-md" :style="isPC && ips.length <= 1 ? 'width: 82%' : isPC && ips.length > 1 ? 'width: 77%' : ''" />
          <q-input dark dense outlined v-model="ip.port" label="Port" :class="isPC ? 'q-mt-md q-ml-sm' : 'q-mt-md'" :style="isPC ? 'width: 12%' : ''" />
          <q-btn v-if="isPC" color="primary" icon="add" dense class="q-mt-md q-ml-sm" size="md" @click="add_ip_and_port(ip)" />
          <q-btn v-else color="primary" icon="add" dense class="q-mt-md" size="md" label="Add Another Forward ip " @click="add_ip_and_port(ip)" />
          <q-btn v-if="isPC" color="negative" icon="remove" dense class="q-mt-md q-ml-sm" size="md" @click="remove_ip_and_port(index)" v-show="ips.length > 1" />
          <q-btn v-else color="negative" icon="remove" dense class="q-mt-md" size="md" label="Remove Forward ip " @click="remove_ip_and_port(index)" v-show="ips.length > 1" />
        </div>
      </div>

      <div class="q-pt-md text-white">
        <q-checkbox dark v-model="block_exploit" label="Block Common Exploits" color="teal" />
        <q-separator v-if="!isPC" />
        <q-checkbox dark v-if="type != 'redirect'" v-model="websocket" label="Websocket Support" color="orange" :class="isPC ? 'q-pl-md' : ''" />
        <q-separator v-if="!isPC" />
        <q-checkbox dark v-if="type != 'redirect'" v-model="enableSSL" label="Enable SSL" :class="isPC ? 'q-pl-md' : ''" />
      </div>
      <div v-if="enableSSL && type != 'redirect'" class="text-white">
        <q-select dark dense outlined v-model="selected_option" :options="sslList" label="Select SSL Certificate" class="q-mt-md" @update:model-value="select_ssl_option()" />
        <q-input v-if="request_new_ssl" dark dense outlined v-model="le_email" label="Email for Let's Encrypt" class="q-mt-md" />
        <q-toggle v-if="request_new_ssl" color="secondary" v-model="agree_le_tos"> I Accept Let's Encrypt's <a href="https://letsencrypt.org/repository/" style="color: #69c">Terms of Service!</a> </q-toggle>
      </div>
      <div></div>
      <div class="q-pt-md text-white">
        <q-btn v-if="enableSSL && request_new_ssl && type != 'redirect'" color="purple" icon="schedule_send" label="Request Free SSL" size="md" :loading="isSSLLoading" @click="handle_request_ssl">
          <template v-slot:loading>
            <q-spinner-hourglass class="on-left" />
            Requesting...
          </template>
        </q-btn>
        <q-separator v-if="!isPC" />
        <q-checkbox v-if="enableSSL && valid_ssl && type != 'redirect'" dark v-model="forceSSL" label="Force SSL" color="teal" :class="isPC ? '' : 'q-mt-md'" />
        <q-separator v-if="!isPC" />
        <q-checkbox v-if="enableSSL && valid_ssl && type != 'redirect'" dark v-model="http2" label="HTTP2 Support" :class="isPC ? 'q-pl-md' : ''" color="orange-4" />
        <q-separator v-if="!isPC" />
        <q-checkbox v-if="enableSSL && valid_ssl && type != 'redirect'" dark v-model="HSTS" label="HSTS Enabled" :class="isPC ? 'q-pl-md' : ''" />
      </div>
    </q-scroll-area>
    <div class="bg-grey-1 q-mt-md q-pa-sm" style="overflow: hidden" v-if="error">
      <span class="text-subtitle2 text-red" style="cursor: default"> {{ error }} </span>
    </div>
    <q-btn-group spread class="q-mt-md">
      <q-btn v-if="store.state.edit_domain" color="primary" label="Update Host" icon="add" :loading="isLoading" @click="add_host">
        <template v-slot:loading>
          <q-spinner-hourglass class="on-left" />
          Updating Host...
        </template>
      </q-btn>
      <q-btn v-else color="primary" label="Add Host" icon="add" :loading="isLoading" @click="add_host">
        <template v-slot:loading>
          <q-spinner-hourglass class="on-left" />
          Adding Host...
        </template>
      </q-btn>
      <q-btn color="grey" label="Clear" icon="clear" @click="handle_clear" />
    </q-btn-group>
  </div>
</template>

<script>
import { ref, watch } from 'vue';
import { useQuasar } from 'quasar';
import store from '../store/index';
import getServerData from '../utils/getServerData';

export default {
  setup() {
    const $q = useQuasar();
    let isPC = $q.platform.is.mobile ? false : true;
    const pageTitle = ref(null);
    const isLoading = ref(false);
    const isSSLLoading = ref(false);
    const { error, addNewHost, updateHost, requestNewSSL } = getServerData();

    const domain = ref('');
    const type = ref('static');
    const static_path = ref(null);
    const redirect_url = ref(null);
    const ips = ref([{ ip: null, port: null }]);
    const block_exploit = ref(false);
    const websocket = ref(false);
    const enableSSL = ref(false);
    const sslList = ref([{ label: "Request New from Let's Encrypt", value: 'request_new' }]);
    const selected_option = ref(null);
    const le_email = ref(null);
    const agree_le_tos = ref(false);
    const forceSSL = ref(false);
    const http2 = ref(false);
    const HSTS = ref(false);
    const request_new_ssl = ref(false);
    const valid_ssl = ref(false);
    const ssl_info = ref(null);

    const email_format = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    const domain_format = /^(\*\.)?([a-z\d][a-z\d-]*[a-z\d]\.)+[a-z]+$/;

    function updateFields() {
      if (store.state.edit_domain) {
        pageTitle.value = 'Update Host';

        domain.value = store.state.edit_domain.domain;
        type.value = store.state.edit_domain.type;
        static_path.value = store.state.edit_domain.static_path;
        redirect_url.value = store.state.edit_domain.redirect_url;
        if (store.state.edit_domain.type == 'reverse_proxy') ips.value = store.state.edit_domain.ips;
        if (store.state.edit_domain.block_exploit) block_exploit.value = store.state.edit_domain.block_exploit == 'True' ? true : false;
        if (store.state.edit_domain.websocket) websocket.value = store.state.edit_domain.websocket == 'True' ? true : false;
        if (store.state.edit_domain.enableSSL) enableSSL.value = store.state.edit_domain.enableSSL == 'True' ? true : false;
        if (store.state.edit_domain.forceSSL) forceSSL.value = store.state.edit_domain.forceSSL == 'True' ? true : false;
        if (store.state.edit_domain.agree_le_tos) agree_le_tos.value = store.state.edit_domain.agree_le_tos == 'True' ? true : false;
        if (store.state.edit_domain.http2) http2.value = store.state.edit_domain.http2 == 'True' ? true : false;
        if (store.state.edit_domain.HSTS) HSTS.value = store.state.edit_domain.HSTS == 'True' ? true : false;
      } else pageTitle.value = 'Add New Host';
      if (store.state.ssl_list.length > 0) {
        store.state.ssl_list.forEach((cert) => {
          sslList.value.push({ label: cert.domain, value: cert.domain });
        });
      }
    }
    updateFields();

    function add_ip_and_port(value) {
      if (value.ip) ips.value.push({ ip: '', port: '' });
    }
    function remove_ip_and_port(index) {
      ips.value.splice(index, 1);
    }

    function select_ssl_option() {
      if (selected_option.value.value == 'request_new') {
        request_new_ssl.value = true;
        valid_ssl.value = null;
      }
      if (selected_option.value.value && selected_option.value.value != 'request_new') {
        request_new_ssl.value = false;
        store.state.ssl_list.forEach((cert) => {
          if (cert.domain == selected_option.value.value) {
            valid_ssl.value = true;
            ssl_info.value = { ssl_cert_path: cert.ssl_cert_path, ssl_key_path: cert.ssl_key_path };
          }
        });
      }
    }

    async function handle_request_ssl() {
      if (!domain.value) return (error.value = `Error: Domain name is required!`);
      if (!le_email.value) return (error.value = `Error: Email for Let's Encrypt is required!`);
      if (!agree_le_tos.value) return (error.value = `Error: Let's Encrypt's TOS is not accepted!`);
      if (!le_email.value.match(email_format)) return (error.value = `Error: Invalid Email provided!`);
      if (!domain.value.match(domain_format)) return (error.value = `Error: Invalid Domain name!`);

      isSSLLoading.value = true;
      const ssl_details = await requestNewSSL({ domain: domain.value, email: le_email.value, agree_le_tos: agree_le_tos.value });
      if (!error.value) {
        ssl_info.value = ssl_details;
        valid_ssl.value = true;
        sslList.value.push({ label: domain.value, value: domain.value });
        selected_option.value = domain.value;
        request_new_ssl.value = false;
      }
      isSSLLoading.value = false;
    }

    async function add_host() {
      if (!domain.value) return (error.value = `Error: Domain name is required!`);
      if (!domain.value.match(domain_format)) return (error.value = `Error: Invalid Domain name!`);
      if (type.value == 'static' && !static_path.value) return (error.value = `Error: Static path is required!`);
      if (type.value == 'redirect' && !redirect_url.value) return (error.value = `Error: Redirect URL is required!`);
      if (type.value == 'reverse_proxy' && !ips.value[0].ip) return (error.value = `Error: At least one ip is required!`);
      if (enableSSL.value) {
        if (!selected_option.value || selected_option.value == 'request_new') return (error.value = `Error: At least one SSL cert is required!`);
      }

      isLoading.value = true;

      const valid_ips = ips.value.filter((ip) => {
        if (ip.ip) {
          if (!ip.port) delete ip.port;
          return ip;
        }
      });

      if (!enableSSL.value) forceSSL.value = HSTS.value = http2.value = false;

      const hostInfo = {
        domain: domain.value,
        type: type.value,
        static_path: static_path.value,
        redirect_url: redirect_url.value,
        ips: valid_ips,
        block_exploit: block_exploit.value,
        websocket: websocket.value,
        enableSSL: enableSSL.value,
        forceSSL: forceSSL.value,
        http2: http2.value,
        HSTS: HSTS.value,
        is_disabled: 0
      };
      if (valid_ssl.value) {
        hostInfo['ssl_cert_path'] = ssl_info.value.ssl_cert_path;
        hostInfo['ssl_key_path'] = ssl_info.value.ssl_key_path;
      }
      if (store.state.edit_domain) await updateHost(hostInfo);
      else await addNewHost(hostInfo);
      if (!error.value) store.dispatch('update_display', 'list');
      store.dispatch('update_edit_domain', null);
      isLoading.value = false;
    }

    function handle_clear() {
      store.dispatch('update_edit_domain', null);
      domain.value = '';
      type.value = 'static';
      ips.value = [{ ip: null, port: null }];
      static_path.value = redirect_url.value = selected_option.value = le_email.value = error.value = null;
      isSSLLoading.value = isLoading.value = block_exploit.value = websocket.value = enableSSL.value = agree_le_tos.value = forceSSL.value = http2.value = HSTS.value = request_new_ssl.value = valid_ssl.value = false;
    }

    return {
      isPC,
      store,
      pageTitle,
      isLoading,
      isSSLLoading,
      error,
      domain,
      type,
      static_path,
      redirect_url,
      ips,
      add_ip_and_port,
      remove_ip_and_port,
      block_exploit,
      websocket,
      enableSSL,
      sslList,
      selected_option,
      select_ssl_option,
      le_email,
      agree_le_tos,
      handle_request_ssl,
      forceSSL,
      http2,
      HSTS,
      request_new_ssl,
      valid_ssl,
      add_host,
      handle_clear,
      thumbStyle: { width: '0px' }
    };
  }
};
</script>
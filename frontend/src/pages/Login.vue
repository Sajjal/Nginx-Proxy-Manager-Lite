<template>
  <q-page class="flex flex-center">
    <q-card class="my-card" style="width: 400px">
      <q-card-section>
        <q-banner inline-actions rounded class="text-white bg-primary text-center" style="overflow: hidden">
          <q-icon name="settings_input_antenna" class="q-mr-sm" size="md" />
          <span class="text-h6" style="cursor: default"> Nginx Proxy Manager Lite </span>
        </q-banner>
      </q-card-section>
      <q-separator />
      <p v-if="store.state.change_password.change" class="text-h6 text-black flex flex-center" style="cursor: default">Change Account Info!</p>
      <q-card-actions vertical>
        <div class="q-pa-md">
          <q-input filled v-model="email" label="Email">
            <template v-slot:append>
              <q-icon name="mail" />
            </template>
          </q-input>
          <q-input v-model="password" filled :type="isPwd ? 'password' : 'text'" label="Password" class="q-mt-md" @keyup.enter="userLogin">
            <template v-slot:append>
              <q-icon :name="isPwd ? 'visibility_off' : 'visibility'" class="cursor-pointer" @click="isPwd = !isPwd" />
            </template>
          </q-input>
          <q-input v-if="store.state.change_password.change" v-model="verify_password" filled :type="isPwd ? 'password' : 'text'" label="Confirm Password" class="q-mt-md" @keyup.enter="userLogin">
            <template v-slot:append>
              <q-icon :name="isPwd ? 'visibility_off' : 'visibility'" class="cursor-pointer" @click="isPwd = !isPwd" />
            </template>
          </q-input>
          <div v-if="error" class="q-mt-md q-pa-sm bg-negative text-white" style="font-size: 18px; cursor: default">
            <q-icon name="error" class="text-white q-mr-sm" size="md" />
            {{ error }}
          </div>
          <q-btn-group spread class="q-mt-md">
            <q-btn v-if="store.state.change_password.change" color="primary" label="Update" icon="send" @click="changeUserPassword" />
            <q-btn v-else color="primary" label="Login" icon="send" @click="userLogin" />
            <q-btn color="grey" label="Clear" icon="clear" @click="clearLoginForm" />
          </q-btn-group>
        </div>
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script>
import { defineComponent, ref } from 'vue';
import store from '../store/index';
import getServerData from '../utils/getServerData';

export default defineComponent({
  name: 'Login',
  setup() {
    const email = ref(null);
    const password = ref(null);
    const verify_password = ref(null);
    const email_format = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;

    const { error, login, changePassword, changePasswordLater } = getServerData();

    async function userLogin() {
      if (!email.value) return (error.value = `Error: Email is required!`);
      if (!password.value) return (error.value = `Error: Password is required!`);
      if (!email.value.match(email_format)) return (error.value = `Error: Invalid Email provided!`);
      await login({ email: email.value, password: password.value });
    }

    async function changeUserPassword() {
      if (!email.value) return (error.value = `Error: Email is required!`);
      if (!password.value) return (error.value = `Error: Password is required!`);
      if (password.value.length < 10) return (error.value = `Password must be >10 characters!`);
      if (password.value != verify_password.value) return (error.value = `Error: Password does not match!`);
      if (!email.value.match(email_format)) return (error.value = `Error: Invalid Email provided!`);
      if (!store.state.change_password.afterLogin) await changePassword({ email: email.value, password: password.value });
      if (store.state.change_password.afterLogin) await changePasswordLater({ email: email.value, password: password.value });

      if (!error.value) return store.dispatch('update_change_password', false);
    }

    function clearLoginForm() {
      email.value = password.value = verify_password.value = error.value = null;
    }

    return { store, password, verify_password, email, isPwd: ref(true), error, userLogin, changeUserPassword, clearLoginForm };
  }
});
</script>

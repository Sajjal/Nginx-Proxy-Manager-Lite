import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import store from '../store/index';

const getServerData = () => {
    const error = ref(null);
    const server = process.env.API;
    const router = useRouter();

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    const options = {
        withCredentials: true,
        credentials: 'same-origin',
        headers: {
            'X-CSRF-TOKEN': getCookie('csrf_access_token'),
        },
    };

    const login = async(payload) => {
        try {
            const response = await axios.post(`${server}login`, payload, options);
            error.value = null
            if (response.data.Status !== 'Change Password') return router.push({ name: "Dashboard" });
            if (response.data.Status == 'Change Password') return store.dispatch('update_change_password', { change: true, afterLogin: false })
        } catch (err) {
            error.value = err.response.data.Error;
        }
    };

    const changePassword = async(payload) => {
        try {
            await axios.post(`${server}changePassword`, payload, options);
            return router.push({ name: "Dashboard" });

        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };
    const changePasswordLater = async(payload) => {
        try {
            await axios.post(`${server}changePasswordLater`, payload, options);
            return router.push({ name: "Dashboard" });

        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };

    const addNewHost = async(payload) => {
        try {
            const response = await axios.post(`${server}create`, payload, options);
            error.value = null
            store.dispatch('add_to_domain_list', payload)
            return response.data
        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };

    const updateHost = async(payload) => {
        try {
            await axios.post(`${server}update`, payload, options);
            error.value = null
            await listHosts()
            await listSSLCerts()
            return
        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };

    const requestNewSSL = async(payload) => {
        try {
            const response = await axios.post(`${server}requestSSL`, payload, options);
            error.value = null
            return response.data
        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };

    const listHosts = async() => {
        try {
            const response = await axios.get(`${server}list`, options);
            store.dispatch('update_domain_list', response.data.domain_list);
            error.value = null
            return
        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };

    const listSSLCerts = async() => {
        try {
            const response = await axios.get(`${server}listSSL`, options);
            store.dispatch('update_ssl_list', response.data.ssl_list);
            error.value = null
            return
        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };

    const deleteHost = async(payload) => {
        try {
            await axios.post(`${server}delete`, payload, options);
            await listHosts()
            await listSSLCerts()
            error.value = null
            return
        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };

    const enableHost = async(payload) => {
        try {
            await axios.post(`${server}enable`, payload, options);
            await listHosts()
            error.value = null
            return
        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };

    const disableHost = async(payload) => {
        try {
            await axios.post(`${server}disable`, payload, options);
            await listHosts()
            error.value = null
            return
        } catch (err) {
            error.value = err.response.data.Error;
            if (err.response && err.response.status == 401) return router.push({ name: "Login" });
        }
    };

    const logout = async(payload) => {
        try {
            await axios.post(`${server}logout`, payload, options);
            return router.push({ name: "Login" });
        } catch (err) {
            return router.push({ name: "Login" });
        }
    };




    return { error, login, logout, changePassword, changePasswordLater, addNewHost, updateHost, requestNewSSL, listHosts, enableHost, disableHost, deleteHost, listSSLCerts };
};

export default getServerData;
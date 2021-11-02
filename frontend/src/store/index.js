import { createStore } from 'vuex'

export default createStore({
    state: { domain_list: [], ssl_list: [], edit_domain: null, display_list: true, display_add_form: false, change_password: { change: false, afterLogin: false } },
    mutations: {
        update_domain_list(state, domain_list) {
            state.domain_list = domain_list;
        },
        update_edit_domain(state, domain) {
            if (!domain) state.edit_domain = null
            else {
                state.domain_list.forEach(element => {
                    if (element.domain == domain) state.edit_domain = element
                });
            }
        },
        add_to_domain_list(state, domain_info) {
            state.domain_list.push(domain_info);
        },
        update_ssl_list(state, ssl_list) {
            state.ssl_list = ssl_list;
        },
        add_to_ssl_list(state, ssl_info) {
            state.ssl_list.push(ssl_info);
        },
        update_display(state, display) {
            if (display == 'list') {
                state.display_list = true;
                state.display_add_form = false
            }
            if (display == 'add') {
                state.display_list = false;
                state.display_add_form = true
            }
        },
        update_change_password(state, change_password) {
            state.change_password = change_password;
        },
    },
    actions: {
        update_domain_list({ commit }, domain_list) {
            commit('update_domain_list', domain_list);
        },
        update_edit_domain({ commit }, domain) {
            commit('update_edit_domain', domain);
        },
        add_to_domain_list({ commit }, domain_info) {
            commit('add_to_domain_list', domain_info);
        },
        update_ssl_list({ commit }, ssl_list) {
            commit('update_ssl_list', ssl_list);
        },
        add_to_ssl_list({ commit }, ssl_info) {
            commit('add_to_ssl_list', ssl_info);
        },
        update_display({ commit }, display) {
            commit('update_display', display);
        },
        update_change_password({ commit }, change_password) {
            commit('update_change_password', change_password);
        }
    },

    // enable strict mode (adds overhead!)
    // for dev mode and --debug builds only
    strict: process.env.DEBUGGING
})
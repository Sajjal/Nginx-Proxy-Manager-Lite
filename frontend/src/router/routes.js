const routes = [{
    path: '/',
    component: () =>
        import ('layouts/MainLayout.vue'),
    children: [{
            path: '/',
            name: 'Dashboard',
            component: () =>
                import ('pages/Index.vue')
        },
        {
            path: '/login',
            name: 'Login',
            component: () =>
                import ('pages/Login.vue')
        }
    ]
}, ]

export default routes
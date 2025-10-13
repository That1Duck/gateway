// nuxt.config.ts
export default defineNuxtConfig({
    modules: ['@nuxtjs/tailwindcss', 'shadcn-nuxt'],
    css: ['@@/assets/css/tailwind.css'],
    tailwindcss: {
        cssPath: '@@/assets/css/tailwind.css', // or '~assets/css/tailwind.css'
        viewer: false
    },
    runtimeConfig: {
        public: {apiBase: '/api/api/v1'},
        apiOrigin: 'http://localhost:8000',
    },
    nitro: {
        devProxy: {
            '/api': { target: 'http://localhost:8000', changeOrigin: true },
        },
        routeRules: {
            '/api/**': { proxy: 'http://localhost:8000/**' },
        },
    },
    compatibilityDate: '2025-10-09',
    shadcn: {
       prefix: '',
       componentDir: 'app/components/ui',
    },
    components: {
        dirs: [
            {
                path: '~/app/components',
                pathPrefix: false,
                extensions: ['vue'], // <- игнорировать .ts в компонентах
            },
        ],
    },
})
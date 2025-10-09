// nuxt.config.ts
export default defineNuxtConfig({
    modules: ['@nuxtjs/tailwindcss', 'shadcn-nuxt'],
    tailwindcss: {
        cssPath: '@/assets/css/tailwind.css', // or '~assets/css/tailwind.css'
        viewer: false
    },
    postcss: { plugins: { '@tailwindcss/postcss': {} } },
    runtimeConfig: {
        public: {
            apiBase: '/api'
        },
        apiOrigin: 'http://127.0.0.1:8000',
    },
    nitro: {
        compatibilityDate: '2025-10-09',
        devProxy: {
            '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
        },
        routeRules: {
            '/api/**': { proxy: 'http://127.0.0.1:8000/**' },
        },
    },
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
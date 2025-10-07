export default defineNuxtConfig({
    modules: ['@nuxtjs/tailwindcss', 'shadcn-nuxt'],
    tailwindcss: {
        cssPath: '@/assets/css/tailwind.css', // or '~assets/css/tailwind.css'
        viewer: false
    },
    postcss: { plugins: { '@tailwindcss/postcss': {} } },
    nitro: {
        compatibilityDate: '2025-10-05'
    },
    shadcn: {
       prefix: '',
       componentDir: './components/ui',
    },
})
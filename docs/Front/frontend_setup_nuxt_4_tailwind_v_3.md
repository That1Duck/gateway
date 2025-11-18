# Frontend: Nuxt 4 + Tailwind CSS v3 — інструкція з нуля

Цей документ описує як ми підняли фронтенд-проєкт на **Nuxt 4** з **Tailwind CSS v3.4** (через модуль `@nuxtjs/tailwindcss`) на Windows/PowerShell. Тут є повний рецепт створення, конфігурації, запуску, а також розділ з типічними помилками.

---

## 1) Передумови
- **Node.js** 18.18+ або 20+ (перевірити: `node -v`)
- ОС: Windows (PowerShell)

> Ми свідомо використовуємо **Tailwind v3** (класичний PostCSS-плагін) — це стабільний варіант, який не конфліктує з оновленнями Tailwind v4.

---

## 2) Створення нового Nuxt-проєкту
```powershell
cd E:\PyFastRun\UI
npx nuxi@latest init frontend
cd .\frontend
```

> Якщо папка `frontend` вже існує — видаліть або почистіть її перед цим кроком.

---

## 3) Встановлення залежностей
Ми використовуємо модуль Nuxt для Tailwind та класичний стек PostCSS (v3):

```powershell
# (опційно) зупинити будь-які запущені нодовські процеси
# taskkill /IM node.exe /F 2>$null

# чистий стан, якщо проект не новий
Remove-Item -Recurse -Force .nuxt,node_modules
Remove-Item package-lock.json,yarn.lock,pnpm-lock.yaml -ErrorAction Ignore

# ставимо Tailwind v3 + PostCSS і модуль Nuxt
npm i -D tailwindcss@3.4 postcss@8 autoprefixer@10 @nuxtjs/tailwindcss
```

---

## 4) Конфігурації та файли

### 4.1 `postcss.config.mjs`
> Для Tailwind v3 потрібен класичний плагін `tailwindcss`.
```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
}
```

### 4.2 `tailwind.config.js`
> Стандартні шляхи Nuxt для сканування класів.
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue',
    './error.vue'
  ],
  theme: { extend: {} },
  plugins: []
}
```

### 4.3 Вхідний CSS — `assets/css/tailwind.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 4.4 `nuxt.config.ts`
> Підключаємо модуль і вказуємо шлях до CSS **без** алиасу `@` (щоб уникнути проблем з резолвом шляхів).
```ts
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss'],
  tailwindcss: {
    cssPath: 'assets/css/tailwind.css',
    viewer: false
  },
  nitro: { compatibilityDate: '2025-10-05' }
})
```

### 4.5 Мінімальні Vue-файли для перевірки
`app.vue`
```vue
<template>
  <NuxtPage />
</template>
```

`pages/index.vue`
```vue
<template>
  <div class="min-h-screen grid place-items-center bg-gray-50">
    <div class="p-8 rounded-2xl shadow text-center space-y-4 bg-white">
      <h1 class="text-3xl font-bold">Nuxt 4 + Tailwind v3 працює 🎉</h1>
      <p class="text-gray-600 text-sm">Сетап через @nuxtjs/tailwindcss + PostCSS.</p>
      <button class="px-4 py-2 rounded-xl border hover:bg-gray-100">Перевірка</button>
    </div>
  </div>
</template>
```

---

## 5) Запуск
```powershell
npm i
npm run dev
```
Відкрити: **http://localhost:3000/** — має з’явитись тестова сторінка.

---

## 6) Типові помилки та як їх уникнути

### A) `Cannot find module '@/assets/css/tailwind.css' ...`
- Причина: неправильний шлях або конфлікт алиасів.
- Рішення: використовуємо `cssPath: 'assets/css/tailwind.css'` (без `@`). Перевіряємо, що файл існує за шляхом `frontend/assets/css/tailwind.css`.

### B) Повідомлення про `@tailwindcss/postcss` або «винос плагіна»
- Це належить до Tailwind v4. У цьому сетапі **не** встановлюємо `@tailwindcss/postcss` і **не** використовуємо `@tailwindcss/vite`.
- Переконайтесь, що в `postcss.config.mjs` — **`tailwindcss: {}`**, а не інший плагін.

### C) Конфліктні PostCSS-конфіги в монорепі
- Якщо у батьківських директоріях існують `postcss.config.*`, Nuxt може підхопити їх.
- Рішення: тимчасово перейменувати зайві файли в `.bak` або видалити.

### D) Дублювання підключення CSS
- Якщо використовується модуль `@nuxtjs/tailwindcss` з `cssPath`, **не** додаємо цей CSS ще і в `css: [...]` Nuxt-конфига.

---

## 7) Далі: підключення shadcn-vue (план на потім)
Коли основа працює, для додавання компонентів (наприклад, **Sidebar**) можемо:
1. Додати модуль:
   ```powershell
   npx nuxi@latest module add shadcn-nuxt
   ```
2. Підготувати Nuxt і ініціалізувати CLI:
   ```powershell
   npx nuxi prepare
   npx shadcn-vue@latest init
   npx shadcn-vue@latest add sidebar
   ```
3. Додати змінні теми для Sidebar в глобальний CSS (див. доку компонента), вставити приклад з їхньої сторінки.

> Детальну інтеграцію зробимо в окремому документі після підтвердження, що базовий фронтенд стабільно працює.

---

## 8) Корисні команди обслуговування
```powershell
# повна очистка кешів/артефактів
Remove-Item -Recurse -Force .nuxt,node_modules
Remove-Item package-lock.json,yarn.lock,pnpm-lock.yaml -ErrorAction Ignore
npm i

# швидкий пошук підозрілих згадок шляху Tailwind CSS
Select-String -Path .\**\* -Pattern "@/assets/css/tailwind.css" -SimpleMatch
```

---

## 9) Підсумок
- Проєкт створено на **Nuxt 4** з **Tailwind v3** через модуль `@nuxtjs/tailwindcss`.
- Використовуємо класичний **PostCSS** стек (`tailwindcss` + `autoprefixer`).
- Шляхи — без алиасів у `cssPath`, щоб уникнути проблем з резолвом.
- Базовий рендер перевірено (`/pages/index.vue`). Наступний крок — додавання UI-компонентів (shadcn-vue Sidebar).


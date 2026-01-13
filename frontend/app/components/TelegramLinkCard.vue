<template>
  <section class="card">
    <div class="card__header">
      <div>
        <h3 class="card__title">Telegram</h3>
        <p class="card__subtitle">
          Link your Telegram account to use the bot.
        </p>
      </div>

      <button class="btn" :disabled="loading" @click="openAndGenerate">
        {{ loading ? "Generating..." : "Connect Telegram" }}
      </button>
    </div>

    <dialog ref="dlg" class="modal">
      <div class="modal__content">
        <h2 class="modal__title">Connect Telegram</h2>

        <p class="label">Your link code:</p>
        <div class="codeRow">
          <div class="codeBox">{{ code ?? "—" }}</div>
          <button class="btn btn--secondary" :disabled="!code" @click="copyCode">
            Copy
          </button>
        </div>

        <p class="hint">
          Open your Telegram bot and send:<br />
          <code class="inlineCode">/link {{ code }}</code>
        </p>

        <div class="actions">
          <a class="btn btn--secondary" :href="botLink" target="_blank" rel="noreferrer">
            Open Telegram Bot
          </a>
          <button class="btn" @click="close">Close</button>
        </div>

        <p v-if="error" class="error">
          {{ error }}
        </p>
      </div>
    </dialog>
  </section>
</template>

<script setup lang="ts">
const dlg = ref<HTMLDialogElement | null>(null)

const loading = ref(false)
const code = ref<string | null>(null)
const error = ref<string | null>(null)


const botLink = "https://t.me/qwrebverbot"

async function openAndGenerate() {
  error.value = null
  code.value = null

  dlg.value?.showModal()
  loading.value = true

  try {
    const data: any = await $fetch("/api/api/v1/users/me/telegram/link-code", {
      method: "POST",
      credentials: "include",
    })

    code.value = data?.code ?? null
    if (!code.value) {
      error.value = "No code returned from server."
    }
  } catch (e: any) {
    error.value = e?.data?.error?.message ?? e?.message ?? "Failed to generate code."
  } finally {
    loading.value = false
  }
}

async function copyCode() {
  if (!code.value) return
  await navigator.clipboard.writeText(code.value)
}

function close() {
  dlg.value?.close()
}
</script>

<style scoped>
.card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; }
.card__header { display: flex; gap: 12px; justify-content: space-between; align-items: start; }
.card__title { margin: 0; font-size: 18px; }
.card__subtitle { margin: 4px 0 0; color: #6b7280; }
.btn { padding: 10px 12px; border-radius: 10px; border: 1px solid #111827; background: #111827; color: white; cursor: pointer; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn--secondary { background: white; color: #111827; }
.modal { border: none; padding: 0; }
.modal::backdrop { background: rgba(0,0,0,0.4); }
.modal__content { width: min(520px, 92vw); padding: 18px; border-radius: 12px; border: 1px solid #e5e7eb; background: white; }
.modal__title { margin: 0 0 12px; }
.label { margin: 8px 0 6px; color: #374151; }
.codeRow { display: flex; gap: 10px; align-items: center; }
.codeBox { font-size: 24px; font-weight: 700; padding: 10px 12px; border-radius: 10px; border: 1px solid #e5e7eb; letter-spacing: 1px; }
.hint { margin-top: 12px; color: #374151; }
.inlineCode { background: #f3f4f6; padding: 2px 6px; border-radius: 6px; }
.actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 14px; }
.error { margin-top: 12px; color: #b91c1c; }
</style>

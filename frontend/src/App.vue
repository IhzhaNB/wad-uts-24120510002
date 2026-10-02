<script setup>
import { ref } from 'vue'
import SessionForm from './components/SessionForm.vue'
import SessionList from './components/SessionList.vue'

const list = ref(null)

function handleCreated() {
  list.value?.reload()
}
</script>

<template>
  <div class="flex min-h-svh flex-col bg-white text-left font-sans text-body">
    <header
      class="flex flex-wrap items-baseline gap-x-6 gap-y-4 bg-primary px-6 py-5"
    >
      <h1 class="font-serif text-[32px] leading-tight font-normal text-white">
        Shuttle Kampus
      </h1>
      <nav aria-label="Navigasi utama" class="flex gap-4">
        <a
          href="#sessions"
          class="border-b border-white/40 pb-0.5 text-[15px] text-on-dark transition-colors duration-200 hover:border-white hover:text-white"
        >
          Daftar Session
        </a>
        <a
          href="#session-form"
          class="border-b border-white/40 pb-0.5 text-[15px] text-on-dark transition-colors duration-200 hover:border-white hover:text-white"
        >
          Tambah Session
        </a>
      </nav>
    </header>

    <main class="flex-1">
      <SessionForm id="session-form" @created="handleCreated" />
      <div id="sessions">
        <SessionList ref="list" />
      </div>
    </main>
  </div>
</template>

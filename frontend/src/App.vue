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
  <div class="page">
    <header class="page-header">
      <h1>Shuttle Kampus</h1>
      <nav aria-label="Navigasi utama">
        <a href="#sessions">Daftar Session</a>
        <a href="#session-form">Tambah Session</a>
      </nav>
    </header>

    <main>
      <SessionForm id="session-form" @created="handleCreated" />
      <div id="sessions">
        <SessionList ref="list" />
      </div>
    </main>

    <footer class="page-footer">
      <p>WAD UTS — Pemesanan Shuttle Kampus</p>
    </footer>
  </div>
</template>

<style scoped>
.page {
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  text-align: left;
}

.page-header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 16px 24px;
  padding: 24px;
  border-bottom: 1px solid var(--border);
}

.page-header h1 {
  font-size: 32px;
  letter-spacing: -0.8px;
  margin: 0;
}

.page-header nav {
  display: flex;
  gap: 18px;
}

.page-header nav a {
  color: var(--accent);
  text-decoration: none;
  font-size: 15px;
  border-bottom: 1px solid transparent;
}

.page-header nav a:hover {
  border-bottom-color: var(--accent-border);
}

main {
  flex: 1;
}

.page-footer {
  padding: 20px 24px;
  border-top: 1px solid var(--border);
  font-size: 14px;
}
</style>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

const API_URL = 'http://localhost:8000/sessions'

const sessions = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const skip = ref(0)
const limit = ref(10)
const hasMore = ref(false)
const selectedId = ref(null)
const deletingId = ref(null)
const notice = ref('')

const isEmpty = computed(
  () => !loading.value && !error.value && sessions.value.length === 0,
)

const rangeLabel = computed(() => {
  if (!sessions.value.length) return ''
  const start = skip.value + 1
  const end = skip.value + sessions.value.length
  return `${start}–${end}`
})

async function fetchSessions() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({
      skip: String(skip.value),
      limit: String(limit.value + 1),
    })
    const term = search.value.trim()
    if (term) params.set('search', term)

    const res = await fetch(`${API_URL}?${params.toString()}`)
    if (!res.ok) throw new Error(`Permintaan gagal (HTTP ${res.status})`)

    const data = await res.json()
    hasMore.value = data.length > limit.value
    sessions.value = hasMore.value ? data.slice(0, limit.value) : data
  } catch (err) {
    sessions.value = []
    hasMore.value = false
    error.value =
      err && err.message && err.message.startsWith('Permintaan')
        ? err.message
        : 'Tidak dapat terhubung ke server. Pastikan backend berjalan di http://localhost:8000.'
  } finally {
    loading.value = false
  }
}

function retry() {
  fetchSessions()
}

function goNext() {
  if (!hasMore.value) return
  skip.value += limit.value
  fetchSessions()
}

function goPrev() {
  if (skip.value === 0) return
  skip.value = Math.max(0, skip.value - limit.value)
  fetchSessions()
}

function toggleSelect(id) {
  selectedId.value = selectedId.value === id ? null : id
}

function dismissNotice() {
  notice.value = ''
}

async function removeSession(session) {
  const confirmed = confirm('Apakah Anda yakin ingin menghapus session ini?')
  if (!confirmed) return

  deletingId.value = session.id
  notice.value = ''
  try {
    const res = await fetch(`${API_URL}/${session.id}`, { method: 'DELETE' })

    if (res.status === 204) {
      notice.value = `Session "${session.route}" berhasil dihapus.`
      selectedId.value = null
      if (sessions.value.length === 1 && skip.value > 0) {
        skip.value = Math.max(0, skip.value - limit.value)
      }
      await fetchSessions()
      return
    }

    if (res.status === 404) {
      notice.value = 'Session sudah tidak ada di server, daftar dimuat ulang.'
      await fetchSessions()
      return
    }

    notice.value = `Gagal menghapus session (HTTP ${res.status}).`
  } catch {
    notice.value =
      'Tidak dapat terhubung ke server. Pastikan backend berjalan di http://localhost:8000.'
  } finally {
    deletingId.value = null
  }
}

watch(search, () => {
  skip.value = 0
  selectedId.value = null
  fetchSessions()
})

onMounted(fetchSessions)

defineExpose({ reload: fetchSessions })
</script>

<template>
  <section class="session-list" aria-labelledby="session-list-title">
    <header class="toolbar">
      <div>
        <h2 id="session-list-title">Daftar Shuttle Session</h2>
        <p class="subtitle">Pemesanan shuttle kampus — data dari API FastAPI.</p>
      </div>
      <div class="search-box">
        <label for="session-search">Cari</label>
        <input
          id="session-search"
          v-model="search"
          type="search"
          placeholder="Cari rute atau driver…"
          autocomplete="off"
        />
      </div>
    </header>

    <p v-if="notice" class="notice" role="status">
      <span>{{ notice }}</span>
      <button type="button" class="notice-close" @click="dismissNotice">Tutup</button>
    </p>

    <div v-if="loading" class="state state-loading" role="status" aria-live="polite">
      <span class="spinner" aria-hidden="true"></span>
      <p>Memuat data shuttle session…</p>
    </div>

    <div v-else-if="error" class="state state-error" role="alert">
      <p class="state-title">Gagal memuat data</p>
      <p>{{ error }}</p>
      <button type="button" class="btn btn-retry" @click="retry">Retry</button>
    </div>

    <div v-else-if="isEmpty" class="state state-empty">
      <p class="state-title">Tidak ada data</p>
      <p v-if="search.trim()">
        Pencarian “{{ search.trim() }}” tidak ditemukan. Coba kata kunci lain.
      </p>
      <p v-else>Belum ada shuttle session yang tersedia.</p>
      <button v-if="search.trim()" type="button" class="btn" @click="search = ''">
        Bersihkan pencarian
      </button>
    </div>

    <div v-else class="state state-success">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Rute</th>
              <th scope="col">Driver</th>
              <th scope="col">Kapasitas</th>
              <th scope="col">Berangkat</th>
              <th scope="col">Status</th>
              <th scope="col">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="session in sessions"
              :key="session.id"
              :class="{ selected: selectedId === session.id }"
              tabindex="0"
              @click="toggleSelect(session.id)"
              @keydown.enter="toggleSelect(session.id)"
            >
              <td class="mono">{{ session.id }}</td>
              <td class="route">{{ session.route }}</td>
              <td>{{ session.driver }}</td>
              <td class="mono">{{ session.capacity }}</td>
              <td class="mono">{{ session.departure_time }}</td>
              <td>
                <span class="badge" :class="`badge-${session.status.toLowerCase()}`">
                  {{ session.status }}
                </span>
              </td>
              <td>
                <button
                  type="button"
                  class="btn btn-delete"
                  :disabled="deletingId === session.id"
                  @click.stop="removeSession(session)"
                >
                  {{ deletingId === session.id ? 'Menghapus…' : 'Hapus' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav class="pagination" aria-label="Navigasi halaman session">
        <button type="button" class="btn" :disabled="skip === 0" @click="goPrev">
          Prev
        </button>
        <span class="page-info">Menampilkan {{ rangeLabel }} dari total hasil</span>
        <button type="button" class="btn" :disabled="!hasMore" @click="goNext">
          Next
        </button>
      </nav>
    </div>
  </section>
</template>

<style scoped>
.session-list {
  text-align: left;
  width: 100%;
  box-sizing: border-box;
  padding: 32px 24px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 20px;
}

.subtitle {
  margin-top: 4px;
  font-size: 15px;
}

.search-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.search-box label {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.search-box input {
  font: inherit;
  color: var(--text-h);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 9px 12px;
  min-width: 240px;
}

.search-box input:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.notice {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px 16px;
  border: 1px solid var(--accent-border);
  border-radius: 8px;
  background: var(--accent-bg);
  color: var(--text-h);
  font-size: 15px;
}

.notice-close {
  font: inherit;
  font-size: 13px;
  color: var(--text-h);
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
}

.notice-close:hover {
  border-color: var(--accent-border);
}

.state {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  background: var(--social-bg);
}

.state-title {
  color: var(--text-h);
  font-weight: 600;
  margin-bottom: 6px;
}

.state-loading {
  display: flex;
  align-items: center;
  gap: 12px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex: none;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.state-error {
  border-color: rgba(220, 38, 38, 0.5);
  background: rgba(220, 38, 38, 0.08);
}

.state-success {
  padding: 0;
  overflow: hidden;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 15px;
}

th,
td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  white-space: nowrap;
}

th {
  background: var(--code-bg);
  color: var(--text-h);
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

tbody tr {
  cursor: pointer;
  transition: background 0.15s;
}

tbody tr:hover,
tbody tr:focus-visible {
  background: var(--accent-bg);
  outline: none;
}

tbody tr.selected {
  background: var(--accent-bg);
  box-shadow: inset 3px 0 0 var(--accent);
}

.route {
  white-space: normal;
  min-width: 220px;
  color: var(--text-h);
}

.mono {
  font-family: var(--mono);
}

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 13px;
  border: 1px solid var(--border);
  background: var(--code-bg);
  color: var(--text-h);
}

.badge-available {
  border-color: rgba(22, 163, 74, 0.5);
  background: rgba(22, 163, 74, 0.12);
  color: #16a34a;
}

.badge-booked {
  border-color: rgba(37, 99, 235, 0.5);
  background: rgba(37, 99, 235, 0.12);
  color: #2563eb;
}

.badge-full {
  border-color: rgba(220, 38, 38, 0.5);
  background: rgba(220, 38, 38, 0.12);
  color: #dc2626;
}

.badge-maintenance {
  border-color: rgba(217, 119, 6, 0.5);
  background: rgba(217, 119, 6, 0.12);
  color: #d97706;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-top: 1px solid var(--border);
  background: var(--bg);
}

.page-info {
  font-size: 14px;
}

.btn {
  font: inherit;
  font-size: 15px;
  color: var(--text-h);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.btn:hover:not(:disabled) {
  border-color: var(--accent-border);
  box-shadow: var(--shadow);
}

.btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-retry {
  margin-top: 12px;
  color: #fff;
  background: #dc2626;
  border-color: #dc2626;
}

.btn-delete {
  font-size: 14px;
  padding: 6px 12px;
  color: #dc2626;
  border-color: rgba(220, 38, 38, 0.45);
}

.btn-delete:hover:not(:disabled) {
  color: #fff;
  background: #dc2626;
  border-color: #dc2626;
}
</style>

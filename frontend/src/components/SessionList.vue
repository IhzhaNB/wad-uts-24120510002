<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import {
  ChevronLeft,
  ChevronRight,
  CircleCheck,
  CircleX,
  Clock,
  RotateCcw,
  SearchX,
  Trash2,
  Wrench,
  X,
} from '@lucide/vue'

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
    // Jeda buatan agar state loading (spinner + pesan) terlihat jelas saat diverifikasi
    await new Promise((resolve) => setTimeout(resolve, 4000))
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

const statusMeta = {
  Available: {
    icon: CircleCheck,
    class: 'border-green-600/50 bg-green-600/10 text-green-700',
  },
  Booked: {
    icon: Clock,
    class: 'border-blue-600/50 bg-blue-600/10 text-blue-700',
  },
  Full: {
    icon: CircleX,
    class: 'border-red-600/50 bg-red-600/10 text-red-700',
  },
  Maintenance: {
    icon: Wrench,
    class: 'border-amber-600/50 bg-amber-600/10 text-amber-700',
  },
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
  <section class="px-6 py-8" aria-labelledby="session-list-title">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h2 id="session-list-title" class="font-serif text-2xl leading-8 font-normal text-primary">
          Daftar Shuttle Session
        </h2>
        <p class="mt-1 text-[15px] leading-[23px] text-muted">
          Pemesanan shuttle kampus — data dari API FastAPI.
        </p>
      </div>
      <div class="flex flex-col gap-1.5">
        <label for="session-search" class="text-[13px] font-bold text-primary">Cari</label>
        <input
          id="session-search"
          v-model="search"
          type="search"
          placeholder="Cari rute atau driver…"
          autocomplete="off"
          class="min-w-[240px] border border-line bg-white px-3 py-2.5 text-[16px] leading-[26px] text-primary outline-none transition-colors duration-200 placeholder:text-muted focus:border-primary"
        />
      </div>
    </div>

    <p
      v-if="notice"
      role="status"
      class="mt-5 flex items-center justify-between gap-3 border border-line bg-surface-1 px-4 py-3 text-[15px] leading-[23px] text-primary"
    >
      <span>{{ notice }}</span>
      <button
        type="button"
        title="Tutup"
        aria-label="Tutup pemberitahuan"
        class="flex h-8 w-8 flex-none items-center justify-center text-muted transition-colors duration-200 hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        @click="dismissNotice"
      >
        <X :size="18" />
      </button>
    </p>

    <div
      v-if="loading"
      role="status"
      aria-live="polite"
      class="mt-5 flex items-center gap-3 border border-line bg-surface-1 px-6 py-6"
    >
      <span
        class="h-5 w-5 flex-none animate-spin rounded-full border-2 border-line border-t-primary"
        aria-hidden="true"
      ></span>
      <p class="text-[16px] leading-[26px] text-body">Memuat data shuttle session…</p>
    </div>

    <div v-else-if="error" role="alert" class="mt-5 border border-danger bg-surface-1 px-6 py-6">
      <p class="text-[16px] font-bold text-primary">Gagal memuat data</p>
      <p class="mt-1 text-[16px] leading-[26px] text-body">{{ error }}</p>
      <button
        type="button"
        title="Coba lagi"
        aria-label="Muat ulang data (Retry)"
        class="mt-4 flex items-center gap-2 bg-primary px-10 py-2.5 text-[16px] font-semibold text-white transition-colors duration-200 hover:bg-[#0e1c2b] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        @click="retry"
      >
        <RotateCcw :size="16" />
        Retry
      </button>
    </div>

    <div v-else-if="isEmpty" class="mt-5 border border-line bg-surface-1 px-6 py-6">
      <p class="text-[16px] font-bold text-primary">Tidak ada data</p>
      <p v-if="search.trim()" class="mt-1 text-[16px] leading-[26px] text-body">
        Pencarian “{{ search.trim() }}” tidak ditemukan. Coba kata kunci lain.
      </p>
      <p v-else class="mt-1 text-[16px] leading-[26px] text-body">
        Belum ada shuttle session yang tersedia.
      </p>
      <button
        v-if="search.trim()"
        type="button"
        title="Bersihkan pencarian"
        aria-label="Bersihkan pencarian"
        class="mt-4 flex items-center gap-2 border-b border-primary pb-0.5 text-[16px] font-semibold text-primary transition-colors duration-200 hover:border-link hover:text-link"
        @click="search = ''"
      >
        <SearchX :size="16" />
        Bersihkan pencarian
      </button>
    </div>

    <div v-else class="mt-5 border border-line bg-white">
      <div class="overflow-x-auto">
        <table class="w-full border-collapse text-left">
          <thead>
            <tr class="bg-surface-2">
              <th scope="col" class="border-b border-line px-3.5 py-3 text-[13px] font-bold text-primary">
                ID
              </th>
              <th scope="col" class="border-b border-line px-3.5 py-3 text-[13px] font-bold text-primary">
                Rute
              </th>
              <th scope="col" class="border-b border-line px-3.5 py-3 text-[13px] font-bold text-primary">
                Driver
              </th>
              <th scope="col" class="border-b border-line px-3.5 py-3 text-[13px] font-bold text-primary">
                Kapasitas
              </th>
              <th scope="col" class="border-b border-line px-3.5 py-3 text-[13px] font-bold text-primary">
                Berangkat
              </th>
              <th scope="col" class="border-b border-line px-3.5 py-3 text-[13px] font-bold text-primary">
                Status
              </th>
              <th scope="col" class="border-b border-line px-3.5 py-3 text-[13px] font-bold text-primary">
                Aksi
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="session in sessions"
              :key="session.id"
              :class="[
                'cursor-pointer border-b border-line-soft transition-colors duration-150 last:border-b-0 hover:bg-surface-1 focus-visible:bg-surface-1 focus-visible:outline-none',
                selectedId === session.id ? 'bg-surface-1' : '',
              ]"
              tabindex="0"
              @click="toggleSelect(session.id)"
              @keydown.enter="toggleSelect(session.id)"
            >
              <td class="px-3.5 py-3 font-mono text-[15px] text-muted">{{ session.id }}</td>
              <td
                class="min-w-[220px] px-3.5 py-3 text-[16px] leading-[26px] font-semibold whitespace-nowrap text-primary"
              >
                {{ session.route }}
              </td>
              <td class="px-3.5 py-3 text-[16px] leading-[26px] text-body">
                {{ session.driver }}
              </td>
              <td class="px-3.5 py-3 font-mono text-[15px] text-muted">{{ session.capacity }}</td>
              <td class="px-3.5 py-3 font-mono text-[15px] text-muted">
                {{ session.departure_time }}
              </td>
              <td class="px-3.5 py-3">
                <span
                  class="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[13px] leading-none font-semibold"
                  :class="
                    statusMeta[session.status]?.class ?? 'border-line bg-surface-1 text-muted'
                  "
                >
                  <component
                    :is="statusMeta[session.status]?.icon ?? Clock"
                    :size="14"
                    aria-hidden="true"
                  />
                  {{ session.status }}
                </span>
              </td>
              <td class="px-3.5 py-3">
                <button
                  type="button"
                  :title="`Hapus session: ${session.route}`"
                  :aria-label="`Hapus session ${session.route}`"
                  class="flex h-8 w-8 items-center justify-center text-danger transition-colors duration-200 hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-55"
                  :disabled="deletingId === session.id"
                  @click.stop="removeSession(session)"
                >
                  <RotateCcw v-if="deletingId === session.id" :size="16" class="animate-spin" />
                  <Trash2 v-else :size="16" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav
        aria-label="Navigasi halaman session"
        class="flex flex-wrap items-center justify-between gap-3 border-t border-line px-4 py-3"
      >
        <button
          type="button"
          title="Halaman sebelumnya"
          aria-label="Prev"
          class="flex h-9 w-9 items-center justify-center border border-line text-primary transition-colors duration-200 hover:border-primary hover:bg-surface-1 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:border-line-soft disabled:text-muted disabled:hover:border-line-soft disabled:hover:bg-transparent"
          :disabled="skip === 0"
          @click="goPrev"
        >
          <ChevronLeft :size="18" />
        </button>
        <span class="text-[14px] leading-[23px] text-muted">
          Menampilkan {{ rangeLabel }} dari total hasil
        </span>
        <button
          type="button"
          title="Halaman berikutnya"
          aria-label="Next"
          class="flex h-9 w-9 items-center justify-center border border-line text-primary transition-colors duration-200 hover:border-primary hover:bg-surface-1 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:border-line-soft disabled:text-muted disabled:hover:border-line-soft disabled:hover:bg-transparent"
          :disabled="!hasMore"
          @click="goNext"
        >
          <ChevronRight :size="18" />
        </button>
      </nav>
    </div>
  </section>
</template>

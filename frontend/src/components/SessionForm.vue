<script setup>
import { ref } from 'vue'
import { Plus } from '@lucide/vue'

const API_URL = 'http://localhost:8000/sessions'

const emit = defineEmits(['created'])

const form = ref({
  route: '',
  driver: '',
  capacity: '',
  departure_time: '',
})
const fieldErrors = ref({})
const serverError = ref('')
const success = ref('')
const submitting = ref(false)

function validate() {
  const errors = {}
  const route = form.value.route.trim()
  const driver = form.value.driver.trim()
  const capacityRaw = String(form.value.capacity).trim()
  const capacity = Number(capacityRaw)

  if (route.length < 3) errors.route = 'Rute wajib diisi, minimal 3 karakter.'
  if (driver.length < 2) errors.driver = 'Nama driver wajib diisi, minimal 2 karakter.'
  if (capacityRaw === '') {
    errors.capacity = 'Kapasitas wajib diisi.'
  } else if (!Number.isInteger(capacity) || capacity <= 0) {
    errors.capacity = 'Kapasitas harus berupa bilangan bulat lebih dari 0.'
  }
  if (!form.value.departure_time) {
    errors.departure_time = 'Jam keberangkatan wajib diisi.'
  }

  fieldErrors.value = errors
  return Object.keys(errors).length === 0
}

function format422(body) {
  if (!body || !Array.isArray(body.detail)) return 'Data tidak valid menurut server (422).'
  return body.detail
    .map((item) => {
      const field = Array.isArray(item.loc) ? item.loc[item.loc.length - 1] : 'body'
      return `${field}: ${item.msg}`
    })
    .join('; ')
}

async function submitForm() {
  serverError.value = ''
  success.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        route: form.value.route.trim(),
        driver: form.value.driver.trim(),
        capacity: Number(form.value.capacity),
        departure_time: form.value.departure_time,
      }),
    })

    if (res.status === 201) {
      const created = await res.json()
      success.value = `Session "${created.route}" berhasil ditambahkan.`
      form.value = { route: '', driver: '', capacity: '', departure_time: '' }
      fieldErrors.value = {}
      emit('created', created)
      return
    }

    if (res.status === 422) {
      const body = await res.json().catch(() => null)
      serverError.value = format422(body)
      return
    }

    serverError.value = `Permintaan gagal (HTTP ${res.status}).`
  } catch {
    serverError.value =
      'Tidak dapat terhubung ke server. Pastikan backend berjalan di http://localhost:8000.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section
    class="mx-6 my-8 border border-line bg-surface-1 p-6"
    aria-labelledby="session-form-title"
  >
    <h2 id="session-form-title" class="font-serif text-2xl leading-8 font-normal text-primary">
      Tambah Session
    </h2>
    <p class="mt-1 text-[15px] leading-[23px] text-muted">
      Isi rute shuttle untuk menambahkan jadwal baru.
    </p>

    <form
      novalidate
      class="mt-5 grid grid-cols-1 items-start gap-4 md:grid-cols-[2fr_1.4fr_0.8fr_0.9fr]"
      @submit.prevent="submitForm"
    >
      <div class="flex flex-col gap-1.5">
        <label for="field-route" class="text-[13px] font-bold text-primary">Rute</label>
        <input
          id="field-route"
          v-model="form.route"
          type="text"
          placeholder="mis. Kampus Utama - Stasiun Tugu"
          autocomplete="off"
          class="w-full border border-line bg-white px-3 py-2.5 text-[16px] leading-[26px] text-primary outline-none transition-colors duration-200 placeholder:text-muted focus:border-primary"
          :class="{ 'border-danger': fieldErrors.route }"
        />
        <p v-if="fieldErrors.route" class="text-[13px] leading-[23px] text-danger">
          {{ fieldErrors.route }}
        </p>
      </div>

      <div class="flex flex-col gap-1.5">
        <label for="field-driver" class="text-[13px] font-bold text-primary">Driver</label>
        <input
          id="field-driver"
          v-model="form.driver"
          type="text"
          placeholder="mis. Budi Santoso"
          autocomplete="off"
          class="w-full border border-line bg-white px-3 py-2.5 text-[16px] leading-[26px] text-primary outline-none transition-colors duration-200 placeholder:text-muted focus:border-primary"
          :class="{ 'border-danger': fieldErrors.driver }"
        />
        <p v-if="fieldErrors.driver" class="text-[13px] leading-[23px] text-danger">
          {{ fieldErrors.driver }}
        </p>
      </div>

      <div class="flex flex-col gap-1.5">
        <label for="field-capacity" class="text-[13px] font-bold text-primary">Kapasitas</label>
        <input
          id="field-capacity"
          v-model="form.capacity"
          type="number"
          min="1"
          step="1"
          placeholder="12"
          class="w-full border border-line bg-white px-3 py-2.5 text-[16px] leading-[26px] text-primary outline-none transition-colors duration-200 placeholder:text-muted focus:border-primary"
          :class="{ 'border-danger': fieldErrors.capacity }"
        />
        <p v-if="fieldErrors.capacity" class="text-[13px] leading-[23px] text-danger">
          {{ fieldErrors.capacity }}
        </p>
      </div>

      <div class="flex flex-col gap-1.5">
        <label for="field-departure" class="text-[13px] font-bold text-primary">
          Jam Berangkat
        </label>
        <input
          id="field-departure"
          v-model="form.departure_time"
          type="time"
          class="w-full border border-line bg-white px-3 py-2.5 text-[16px] leading-[26px] text-primary outline-none transition-colors duration-200 focus:border-primary"
          :class="{ 'border-danger': fieldErrors.departure_time }"
        />
        <p v-if="fieldErrors.departure_time" class="text-[13px] leading-[23px] text-danger">
          {{ fieldErrors.departure_time }}
        </p>
      </div>

      <div class="md:col-span-4">
        <button
          type="submit"
          class="flex items-center gap-2 bg-primary px-10 py-2.5 text-[16px] font-semibold text-white transition-colors duration-200 hover:bg-[#0e1c2b] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-55"
          :disabled="submitting"
        >
          <Plus :size="16" />
          {{ submitting ? 'Mengirim…' : 'Tambah Session' }}
        </button>
      </div>
    </form>

    <p
      v-if="serverError"
      role="alert"
      class="mt-4 border border-danger bg-white px-4 py-3 text-[15px] leading-[23px] text-danger"
    >
      {{ serverError }}
    </p>
    <p
      v-if="success"
      role="status"
      class="mt-4 border border-line bg-white px-4 py-3 text-[15px] leading-[23px] text-primary"
    >
      {{ success }}
    </p>
  </section>
</template>

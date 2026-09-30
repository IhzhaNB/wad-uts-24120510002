<script setup>
import { ref } from 'vue'

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
  <section class="session-form" aria-labelledby="session-form-title">
    <h2 id="session-form-title">Tambah Session</h2>
    <p class="subtitle">Isi rute shuttle untuk menambahkan jadwal baru.</p>

    <form novalidate @submit.prevent="submitForm">
      <div class="field">
        <label for="field-route">Rute</label>
        <input
          id="field-route"
          v-model="form.route"
          type="text"
          placeholder="mis. Kampus Utama - Stasiun Tugu"
          autocomplete="off"
        />
        <p v-if="fieldErrors.route" class="field-error">{{ fieldErrors.route }}</p>
      </div>

      <div class="field">
        <label for="field-driver">Driver</label>
        <input
          id="field-driver"
          v-model="form.driver"
          type="text"
          placeholder="mis. Budi Santoso"
          autocomplete="off"
        />
        <p v-if="fieldErrors.driver" class="field-error">{{ fieldErrors.driver }}</p>
      </div>

      <div class="field field-small">
        <label for="field-capacity">Kapasitas</label>
        <input
          id="field-capacity"
          v-model="form.capacity"
          type="number"
          min="1"
          step="1"
          placeholder="12"
        />
        <p v-if="fieldErrors.capacity" class="field-error">{{ fieldErrors.capacity }}</p>
      </div>

      <div class="field field-small">
        <label for="field-departure">Jam Berangkat</label>
        <input id="field-departure" v-model="form.departure_time" type="time" />
        <p v-if="fieldErrors.departure_time" class="field-error">
          {{ fieldErrors.departure_time }}
        </p>
      </div>

      <div class="actions">
        <button type="submit" class="btn btn-submit" :disabled="submitting">
          {{ submitting ? 'Mengirim…' : 'Tambah Session' }}
        </button>
      </div>
    </form>

    <p v-if="serverError" class="form-error" role="alert">{{ serverError }}</p>
    <p v-if="success" class="form-success" role="status">{{ success }}</p>
  </section>
</template>

<style scoped>
.session-form {
  text-align: left;
  margin: 32px 24px 8px;
  padding: 24px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--social-bg);
}

.subtitle {
  margin-top: 4px;
  font-size: 15px;
}

form {
  display: grid;
  grid-template-columns: 2fr 1.4fr 0.8fr 0.9fr;
  gap: 16px;
  align-items: start;
  margin-top: 20px;
}

@media (max-width: 900px) {
  form {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 560px) {
  form {
    grid-template-columns: 1fr;
  }
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-h);
}

.field input {
  font: inherit;
  color: var(--text-h);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 9px 12px;
  width: 100%;
  box-sizing: border-box;
}

.field input:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.field-error {
  font-size: 13px;
  color: #dc2626;
}

.actions {
  grid-column: 1 / -1;
}

.btn {
  font: inherit;
  font-size: 15px;
  color: var(--text-h);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 9px 18px;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-submit {
  color: #fff;
  background: var(--accent);
  border-color: var(--accent);
}

.btn-submit:hover:not(:disabled) {
  box-shadow: var(--shadow);
}

.btn-submit:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.form-error {
  margin-top: 16px;
  padding: 12px 16px;
  border: 1px solid rgba(220, 38, 38, 0.5);
  border-radius: 8px;
  background: rgba(220, 38, 38, 0.08);
  color: #dc2626;
  font-size: 15px;
}

.form-success {
  margin-top: 16px;
  padding: 12px 16px;
  border: 1px solid rgba(22, 163, 74, 0.5);
  border-radius: 8px;
  background: rgba(22, 163, 74, 0.1);
  color: #16a34a;
  font-size: 15px;
}
</style>

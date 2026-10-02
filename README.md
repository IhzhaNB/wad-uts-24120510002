# Shuttle Kampus — UTS WAD (Sesi 8, individu)

Aplikasi pemesanan jadwal shuttle kampus: daftar jadwal dengan pencarian, pagination,
penambahan, dan penghapusan — backend **FastAPI** + frontend **Vue 3** (Tailwind CSS v4).
Tanpa basis data: data in-memory di `backend/app/data.py` (13 baris), sengaja agar seluruh
alur UTS dapat diuji ulang dari nol hanya dengan me-restart backend.

Repo ini adalah repo UTS individual. Piagam proyek kelompok The Build ada di
[`docs/PROJECT.md`](docs/PROJECT.md); rubrik UTS (B25/F27/Q13 + pembelaan 35) dibahas di sana.

## 1. Prasyarat

| Alat | Versi | Cek |
|---|---|---|
| Git | apa saja | `git --version` |
| Node.js | 20 LTS atau lebih baru | `node -v` |
| Python | 3.11 atau lebih baru | `python --version` |

> Windows: saat install Python dari python.org, **centang "Add Python to PATH"**.
> Kalau `python` tidak dikenali, coba `py`.

Tidak ada dependensi eksternal yang perlu di-install selain `pip install -r
backend/requirements.txt` dan `npm install` di `frontend/`. Basis data tidak dipakai pada UTS
ini — tidak ada yang perlu di-setup.

## 2. Layanan

| Layanan | Port lokal | Berkas | Catatan |
|---|---|---|---|
| Backend (FastAPI + Uvicorn) | `8000` | `backend/app/` | data in-memory; Swagger UI di `/docs` |
| Frontend (Vite + Vue 3) | `5173` | `frontend/src/` | mengambil data dari `http://localhost:8000/sessions` |

CORS backend hanya mengizinkan origin `http://localhost:5173`, jadi kedua server harus
berjalan bersamaan.

## 3. Cara menjalankan

```bash
# --- backend (terminal 1) ---
cd backend
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# --- frontend (terminal 2) ---
cd frontend
npm install
npm run dev
```

Nyalakan backend dulu, baru frontend. Setelah itu:

- `http://localhost:5173` — aplikasi
- `http://localhost:8000/docs` — Swagger UI untuk menguji endpoint
- `http://localhost:8000/health` — `{"status":"ok"}`

## API Contract

Base URL lokal: `http://localhost:8000`. Kontrak lengkap interaktif ada di `/docs`
(OpenAPI otomatis dari FastAPI).

| Method | Endpoint | Parameter / body | Keberhasilan | Kegagalan |
|---|---|---|---|---|
| GET | `/health` | — | `200` `{"status":"ok"}` | — |
| GET | `/sessions` | query `skip` (≥0), `limit` (≥1), `search` (opsional) | `200` daftar `SessionOut` | — |
| GET | `/sessions/{session_id}` | path `session_id` | `200` satu `SessionOut` | `404` `{"detail":"Session not found"}` |
| POST | `/sessions` | body `SessionCreate` (JSON) | `201` `SessionOut` + `id` baru | `422` detail validasi Pydantic |
| DELETE | `/sessions/{session_id}` | path `session_id` | `204` tanpa badan | `404` `{"detail":"Session not found"}` |

**Skema** (`backend/app/schemas.py`):

| Field | Tipe | Aturan |
|---|---|---|
| `route` | string | minimal 3 karakter |
| `driver` | string | minimal 2 karakter |
| `capacity` | integer | > 0 |
| `departure_time` | string | wajib (ISO 8601, mis. `2026-09-30T07:30:00`) |
| `status` | string | opsional, default `Available` |
| `id` | integer | hanya pada respons (`SessionOut`), dihasilkan server |

**Perilaku kunci:**

- `search` memfilter `route` dan `driver` case-insensitive, lalu `skip`/`limit` diterapkan
  sebagai offset pagination pada hasil tersaring.
- `POST` divalidasi Pydantic sebelum masuk daftar; body yang melanggar aturan di atas
  menghasilkan `422`, bukan `500`.
- CORS: origin `http://localhost:5173` diizinkan (`allow_credentials=True`); endpoint lain
  ditolak browser untuk origin berbeda.
- Penyimpanan in-memory: hasil `POST`/`DELETE` hilang saat backend berhenti.

## Penyelesaian Tugas

Pemetaan tiap requirement UTS ke kode yang mengimplementasikannya:

| # | Requirement | Implementasi | Status |
|---|---|---|---|
| 1 | Dataset in-memory ≥ 12 baris | [`backend/app/data.py`](backend/app/data.py) — 13 baris | ✓ |
| 2 | GET `/sessions` — pagination + search | `backend/app/main.py:24` — `list_sessions()` dengan `skip`/`limit`/`search` | ✓ |
| 3 | GET `/sessions/{id}` — 404 | `backend/app/main.py:39` — `get_session()`, `HTTPException(404)` | ✓ |
| 4 | POST `/sessions` — 201 + validasi Pydantic | `backend/app/main.py:47` + [`backend/app/schemas.py`](backend/app/schemas.py) | ✓ |
| 5 | POST `/sessions` — validasi `422` | `schemas.py` — `Field(min_length=…, gt=…)` | ✓ |
| 6 | DELETE `/sessions/{id}` — 204 | `backend/app/main.py:55` — `delete_session()` → `Response(204)` | ✓ |
| 7 | DELETE id tak ada — 404 | `backend/app/main.py:55` — cabang `HTTPException(404)` | ✓ |
| 8 | CORS origin frontend | `backend/app/main.py:10` — `CORSMiddleware` | ✓ |
| 9 | Frontend daftar dari API | `frontend/src/components/SessionList.vue:40` — `fetchSessions()` | ✓ |
| 10 | State Loading | `SessionList.vue:210` — pesan "Memuat data shuttle session…" | ✓ |
| 11 | State Error + Retry | `SessionList.vue:59` — blok `catch` + tombol Retry | ✓ |
| 12 | State Empty | `SessionList.vue` — pesan pencarian tidak ditemukan | ✓ |
| 13 | State Success + pagination | `SessionList.vue` — tabel + Prev/Next `skip`/`limit` | ✓ |
| 14 | Form create + validasi | `frontend/src/components/SessionForm.vue:52` — `submitForm()` | ✓ |
| 15 | Hapus dengan konfirmasi | `SessionList.vue:95` — `confirm()` sebelum DELETE | ✓ |
| 16 | Backend `/health` + `/docs` | `backend/app/main.py:19` — route `/health` | ✓ |
| 17 | `python verify.py --sesi 2` hijau | [`verify.py`](verify.py) — dijalankan sendiri | ✓ |

## 4. Cara memverifikasi

Satu perintah, dipakai sepanjang semester:

```bash
python verify.py --sesi 2
```

`verify.py` adalah **perintah yang sama persis** yang dipakai dosen untuk memeriksa artefakmu.
Kalau hijau di laptopmu, hijau juga saat dinilai.

### Requirement UTS lewat Swagger UI

Dijalankan dengan backend hidup di `:8000`, di **`http://localhost:8000/docs`**:

1. **GET /sessions** — klik **Try it out**, isi `search=budi`, `skip=0`, `limit=5`
   → **Execute** → respons `200` berisi hasil pencarian pada field `route`/`driver`.
2. **GET /sessions/{session_id}** — isi `session_id=9999` → **Execute** → `404`
   `{"detail":"Session not found"}`.
3. **POST /sessions** — **Try it out**, isi body valid (`route`, `driver`, `capacity`,
   `departure_time`) → **Execute** → `201 Created` + `id` baru.
4. **POST /sessions** — ulangi dengan body yang melanggar aturan (mis. `capacity:-1`
   atau `route` kurang dari 3 karakter) → **Execute** → `422` + detail validasi Pydantic.
5. **DELETE /sessions/{session_id}** — id yang ada (mis. `1`) → `204 No Content` tanpa
   badan; id yang tidak ada (`9999`) → `404`.
6. **CORS** — tidak bisa diuji dari Swagger. Buka `http://localhost:5173`, DevTools →
   tab **Network** → request `/sessions` → lihat header respons
   `access-control-allow-origin: http://localhost:5173`.

> Dataset bersifat **in-memory**: POST/DELETE hilang saat backend berhenti. Restart
> `uvicorn` dulu sebelum mulai testing supaya data awal (13 baris) konsisten.

Di frontend `http://localhost:5173`, empat keadaan dicek satu per satu:

- **Loading** — teks "Memuat data shuttle session…" tampil selama data diambil.
- **Error** — matikan backend lalu muat ulang halaman; muncul pesan error dan tombol **Retry**
  yang mengambil data ulang setelah backend hidup lagi.
- **Empty** — cari kata yang tidak ada (misal `zzzz`), muncul pesan pencarian tidak ditemukan.
- **Success** — tabel terisi, pencarian menyaring `route`/`driver`, tombol **Prev/Next**
  menggeser `skip`/`limit`, dan tiap baris punya tombol **Hapus** dengan konfirmasi browser
  `confirm()`. Badge status berwarna per makna: `Available` hijau, `Booked` biru, `Full`
  merah, `Maintenance` kuning.

### Bukti penyelesaian

Screenshot tersimpan di `docs/screenshots/` dan direferensikan langsung dari tabel di bawah.

| # | Requirement | Cara verifikasi | ✓ | Bukti |
|---|---|---|---|---|
| 1 | Dataset in-memory ≥ 12 baris | Buka `backend/app/data.py` (13 baris) | ✓ | [`backend/app/data.py`](backend/app/data.py) |
| 2 | GET `/sessions` — pagination + search | `/docs` → GET `/sessions` → Try it out → `search=budi`, `skip=0`, `limit=5` → Execute | ✓ | ![Swagger GET /sessions dengan search](docs/screenshots/02-get-search.png) |
| 3 | GET `/sessions/{id}` — 404 | `/docs` → GET `/sessions/{session_id}` → id `9999` → Execute | ✓ | ![Swagger GET 404](docs/screenshots/03-get-404.png) |
| 4 | POST `/sessions` — Pydantic 201 | `/docs` → POST `/sessions` → body valid → Execute → `201` + id baru | ✓ | ![Swagger POST 201](docs/screenshots/04-post-201.png) |
| 5 | POST `/sessions` — validasi 422 | `/docs` → POST `/sessions` → body invalid (`capacity:-1`) → Execute → `422` | ✓ | ![Swagger POST 422](docs/screenshots/05-post-422.png) |
| 6 | DELETE `/sessions/{id}` — 204 | `/docs` → DELETE `/sessions/{session_id}` → id `1` → Execute → `204` tanpa badan | ✓ | ![Swagger DELETE 204](docs/screenshots/06-delete-204.png) |
| 7 | DELETE id tak ada — 404 | `/docs` → DELETE → id `9999` → Execute → `404` | ✓ | ![Swagger DELETE 404](docs/screenshots/07-delete-404.png) |
| 8 | CORS origin frontend | `:5173` → DevTools Network → request `/sessions` → header `access-control-allow-origin` | ✓ | ![Header CORS di DevTools](docs/screenshots/08-cors.png) |
| 9 | Frontend daftar dari API | Buka `http://localhost:5173`, tabel terisi | ✓ | ![Halaman utama dengan tabel terisi](docs/screenshots/09-daftar.png) |
| 10 | State **Loading** | Muat ulang halaman, teks "Memuat data shuttle session…" tampil | ✓ | ![State loading](docs/screenshots/10-loading.png) |
| 11 | State **Error** + Retry | Matikan backend → reload → pesan error + tombol Retry; nyalakan backend → Retry sukses | ✓ | ![State error dengan tombol Retry](docs/screenshots/11-error.png) |
| 12 | State **Empty** | Cari `zzzz` → pesan pencarian tidak ditemukan | ✓ | ![State empty](docs/screenshots/12-empty.png) |
| 13 | State **Success** + pagination | Tabel terisi; Prev/Next menggeser halaman, status disabled tepat | ✓ | ![Tabel dan pagination](docs/screenshots/13-success.png) |
| 14 | Form create + validasi | Submit kosong → error per field; isi valid → baris baru muncul (201) | ✓ | ![Error validasi form](docs/screenshots/14-form-validasi.png) · ![Hasil submit valid](docs/screenshots/14-form-sukses.png) |
| 15 | Hapus dengan konfirmasi | Klik ikon hapus → dialog `confirm()` → OK → baris hilang (204) | ✓ | ![Dialog konfirmasi hapus](docs/screenshots/15-confirm.png) |
| 16 | Backend `/health` + `/docs` | Buka `http://localhost:8000/health` → `{"status":"ok"}`; buka `http://localhost:8000/docs` | ✓ | ![Respons /health](docs/screenshots/16-health.png) · ![Swagger UI terbuka](docs/screenshots/16-swagger-ui.png) |
| 17 | `python verify.py --sesi 2` hijau | Semua pemeriksaan OK | ✓ | ![Keluaran verify.py hijau](docs/screenshots/17-verify.png) |

## 5. Masalah yang sering muncul

| Gejala | Sebab biasanya | Tindakan |
|---|---|---|
| `python` tidak dikenali (Windows) | PATH tidak dicentang saat install | pakai `py`, atau install ulang dan centang "Add Python to PATH" |
| `npm run dev` jalan tapi halaman kosong | `index.html` tidak menunjuk `src/main.js` | cek `<script type="module" src="/src/main.js">` |
| `/health` 404 | `app.main` bukan modul yang dijalankan | jalankan `uvicorn` dari dalam folder `backend/` |
| Frontend: "Tidak dapat memuat data" terus | backend tidak jalan, atau port bukan `8000` | nyalakan `uvicorn app.main:app --reload`; pastikan `:8000` |
| Tabel kosong padahal backend jalan | CORS menolak origin | akses via `http://localhost:5173`, bukan `127.0.0.1:5173` |
| Data POST/DELETE hilang setelah restart | penyimpanan in-memory | normal; restart `uvicorn` untuk kembali ke 13 baris awal |
| Port `5173`/`8000` terpakai | server sebelumnya belum mati | matikan proses lama, atau jalankan Vite dengan `--port` lain |
| `venv/` ikut ter-commit | `.gitignore` diubah | kembalikan `.gitignore` bawaan repo |

---

## Penggunaan AI assistant

AI assistant **diizinkan** pada sesi praktikum, dan **dilarang pada UTS (Sesi 8) dan UAS
(Sesi 16)**. Syaratnya satu: tulis pengungkapan singkat di bawah ini, dan perbarui saat berubah.
Ketentuan 1 tetap berlaku penuh — kalau kamu tidak bisa menjelaskan kode yang dihasilkan AI,
nilainya 0.

- UTS individual, dikerjakan sebelum Sesi 8 — `opencode` (AI coding agent, model
  `opencode/mimo-v2.6-flash-free`) membantu menyusun `backend/app/` (data in-memory, skema
  Pydantic, lima endpoint + CORS), komponen `frontend/src/` (daftar 4 keadaan, form tambah,
  hapus dengan konfirmasi), dan draf dokumentasi ini. Semua perubahan saya tinjau sebelum
  di-commit, dan verifikasinya saya jalankan sendiri: `npm run build`, `python verify.py`,
  uji tiap endpoint lewat Swagger (`/docs`), serta pengujian browser untuk empat keadaan UI,
  validasi form, dan alur hapus. Saya bisa menjelaskan setiap baris yang ada di repo ini.

## Ketentuan yang paling sering menghapus nilai

1. **Artefak wajib dapat dipertahankan.** Kode yang tidak bisa kamu jelaskan bernilai **0**,
   sebagus apa pun hasilnya. Berlaku juga untuk bagian yang ditulis anggota lain. Riwayat commit
   adalah bukti utama kepemilikan.
2. **Tidak dapat dijalankan = 0 fungsionalitas.** Gagal run, gagal build, atau CI merah bernilai
   0 pada komponen fungsionalitas. Aplikasi dinilai dengan **dijalankan di hadapan dosen**, bukan
   dari tangkapan layar.
3. **Tanpa commit atas namamu sendiri = 0 Tugas Kelompok**, berapa pun nilai timmu. Nilai
   individu = nilai kelompok × faktor kontribusi (0–1) dari commit/PR sendiri, peer assessment,
   dan kemampuan menjelaskan bagian **mana pun** dari kode.
4. **Kredensial ter-commit membatalkan nilai artefak sesi itu** — kunci API, kata sandi basis
   data, token. Berlaku **sejak Sesi 2**, jauh sebelum keamanan diajarkan formal. Karena itu
   `.env` ada di `.gitignore` dan CI menjalankan pemindai rahasia.
5. **Commit sebelum keluar.** Semua tenggat adalah akhir sesi. Waktu commit adalah bukti kerjamu
   dilakukan di dalam sesi.

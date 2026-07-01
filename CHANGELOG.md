# Changelog

## [0.8] - 2026-07-01

### Added
- Port container Flask bisa dikonfigurasi via env var `FLASK_PORT` (default 5000)
- Port host Docker bisa dikonfigurasi via env var `HOST_PORT` (default 5000) di `.env`
- Baris `HOST_PORT=5005` di `.env.example` dan `.env`
- Dokumentasi cara mengubah port di README.md

### Changed
- `main.py`: `app.run(port=5000)` menjadi `app.run(port=int(os.getenv('FLASK_PORT', '5000')))`
- `docker-compose.yml`: port mapping `"5000:5000"` menjadi `"${HOST_PORT:-5000}:5000"`
- `.env.example`: tambah variabel `FLASK_PORT` dan `HOST_PORT`

## [0.7] - 2026-07-01

### Added
- README.md dengan dokumentasi lengkap (fitur, struktur, instalasi, konfigurasi, API endpoints)
- Folder `app/static/` untuk memisahkan asset statis
- `app/static/css/style.css` -- style bersama untuk semua halaman
- `app/static/css/login.css` -- style khusus halaman login dan change password
- `app/static/js/admin.js` -- JavaScript CRUD aplikasi dan user (terpisah dari HTML)

### Changed
- Semua inline CSS dipindahkan ke file eksternal di `static/css/`
- Semua inline JavaScript admin dipindahkan ke `static/js/admin.js`
- Translasi Jinja2 pada JavaScript dilewatkan via elemen `#admin-config` dengan atribut `data-*`
- Halaman portal dan settings hanya menyisakan CSS yang benar-benar unik (`.app-card`, `.settings-icon`)
- Template HTML menjadi lebih bersih dan mudah dimaintenance

## [0.6] - 2026-07-01

### Added
- CRUD user management untuk admin (tambah, edit, hapus user)
- Route `PUT /admin/users/<id>` untuk edit user (nama, username, role, bahasa)
- Route `DELETE /admin/users/<id>` untuk hapus user (dengan proteksi tidak bisa hapus diri sendiri)
- Route `PUT /admin/users/<id>/reset-password` untuk reset password user jadi `user123`
- Modal add/edit user dengan field: nama, username, password, role, bahasa
- Tombol aksi edit, hapus, dan reset password di tabel user
- Kolom bahasa dan aksi di tabel user management
- Helper `_admin_required()` untuk mengecek role admin di semua route

### Security
- Validasi username unik saat tambah/edit user
- Password hanya wajib saat tambah user baru, opsional saat edit
- Proteksi tidak bisa menghapus akun sendiri

## [0.5] - 2026-07-01

### Added
- Sistem i18n (internasionalisasi) dengan dukungan bahasa Indonesia dan Inggris
- Halaman `/settings` dengan tiga fitur: ganti nama, ganti password, dan pilih bahasa
- Template `settings.html` dengan form terpisah untuk setiap pengaturan
- Field `language` pada model User untuk menyimpan preferensi bahasa
- Context processor i18n untuk menyediakan fungsi `_()` di semua template
- Navigasi responsive dengan hamburger menu (navbar-toggler) di semua halaman

### Changed
- Link "Ganti Password" di navbar diubah menjadi "Pengaturan" / "Settings"
- Route `/change-password` tetap dipertahankan untuk kompatibilitas
- Semua teks di template portal, admin, login, dan settings menggunakan fungsi `_()` untuk translasi
- Grid aplikasi di portal menggunakan `col-6 col-md-4 col-lg-3` untuk responsive yang lebih baik
- Layout login dan change password menggunakan padding responsif untuk layar kecil

### Security
- Validasi input nama tidak boleh kosong di settings
- Password baru tetap divalidasi minimal 6 karakter

## [0.4] - 2026-07-01

### Added
- Fitur ganti password untuk admin dan user melalui route `/change-password`
- Template `change_password.html` dengan form validasi (password saat ini, password baru, konfirmasi)
- Link "Ganti Password" di navbar halaman portal dan admin
- Versioning footer di semua halaman

### Security
- Validasi password baru minimal 6 karakter
- Verifikasi password saat ini sebelum mengubah
- Konfirmasi password baru harus cocok

## [0.3] - 2026-07-01

### Fixed
- Struktur kode `auth.py`: fungsi `get_client_ip()` dipindah agar tidak memotong routes `portal` dan `logout`
- Error `'cryptography' package is required` dengan menambah `cryptography` ke `requirements.txt`
- Nama file `model.py` menjadi `models.py` agar sesuai dengan import statements

### Security
- Password admin default dapat dikonfigurasi via environment variable `ADMIN_PASSWORD`
- Admin default hanya dibuat jika database kosong (tidak ada user sama sekali)

## [0.2] - 2026-07-01

### Fixed
- Syntax Jinja2 di inline `onclick` HTML pada `admin.html` diganti dengan `data-app-id` attribute dan event listener

### Security
- `debug=True` diganti dengan environment variable `FLASK_DEBUG` (nonaktif default)
- `SECRET_KEY` wajib diisi, tidak ada fallback lemah
- Informasi kredensial default admin dihapus dari template login
- Password hardcoded di `docker-compose.yml` dipindah ke `env_file: .env`
- Session cookie security: `SESSION_COOKIE_HTTPONLY` dan `SESSION_COOKIE_SAMESITE`
- Rate limiting login (min 1 detik antar percobaan)
- Fungsi `get_client_ip()` untuk validasi IP address lebih aman
- Pembuatan default admin dihapus dari production code

## [0.1] - 2026-06-01

### Added
- Inisialisasi project dengan Flask
- Struktur dasar aplikasi: `main.py`, `auth.py`, `admin.py`, `database.py`, `model.py`
- Autentikasi login/logout menggunakan Flask-Login
- Halaman login dengan template `login.html`
- Halaman portal dengan template `portal.html`
- Panel admin dengan template `admin.html`
- Manajemen aplikasi (CRUD) untuk admin
- Manajemen user untuk admin
- Logging login dengan IP address dan timestamp
- Docker Compose setup dengan MySQL 8.0
- Database MySQL dengan tabel `users`, `login_logs`, `applications`
- Default admin user (admin/admin123) untuk setup awal

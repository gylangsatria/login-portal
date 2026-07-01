# Portal Login

Aplikasi portal login berbasis Flask dengan panel admin, manajemen aplikasi, manajemen user, dukungan multi bahasa (Indonesia/Inggris), dan deployment Docker.

## Fitur

- Autentikasi login/logout dengan Flask-Login
- Halaman portal untuk mengakses berbagai aplikasi
- Panel admin untuk manajemen aplikasi dan user
- Manajemen aplikasi (CRUD): tambah, edit, hapus aplikasi
- Manajemen user (CRUD): tambah, edit, hapus user, reset password
- Ganti password dan nama sendiri melalui halaman settings
- Multi bahasa: Indonesia dan Inggris (dapat dipilih di settings)
- Logging login dengan IP address dan timestamp
- Rate limiting login untuk mencegah brute force
- Responsive design (mobile, tablet, desktop)
- Sticky footer di semua halaman
- Auto-migrasi kolom database

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python 3.11, Flask 2.3 |
| Database | MySQL 8.0 |
| ORM | SQLAlchemy, Flask-SQLAlchemy |
| Autentikasi | Flask-Login, Werkzeug |
| Frontend | Bootstrap 5, Font Awesome |
| Container | Docker, Docker Compose |

## Struktur Project

```
portal-login/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css        # Style bersama (navbar, card, table, modal, footer)
│   │   │   └── login.css        # Style halaman login & change password
│   │   └── js/
│   │       └── admin.js         # JavaScript CRUD aplikasi & user
│   ├── templates/
│   │   ├── login.html           # Halaman login
│   │   ├── portal.html          # Halaman portal aplikasi
│   │   ├── admin.html           # Panel admin
│   │   ├── settings.html        # Halaman settings (ganti nama, password, bahasa)
│   │   └── change_password.html # Halaman ganti password (legacy)
│   ├── main.py                  # Entry point Flask, konfigurasi, routing
│   ├── auth.py                  # Routes autentikasi (login, logout, portal)
│   ├── admin.py                 # Routes admin (CRUD aplikasi & user)
│   ├── settings.py              # Routes settings (ganti nama, password, bahasa)
│   ├── database.py              # Inisialisasi SQLAlchemy & LoginManager
│   ├── models.py                # Model database (User, LoginLog, Application)
│   └── i18n.py                  # Sistem translasi (Indonesia/Inggris)
├── docker-compose.yml           # Orkestrasi container (web + db)
├── Dockerfile                   # Build image Python
├── requirements.txt             # Dependencies Python
├── .env.example                 # Contoh konfigurasi environment
└── CHANGELOG.md                 # Riwayat perubahan
```

## Cara Install dan Menjalankan

### Prasyarat

- Docker dan Docker Compose terinstall

### Langkah-langkah

1. Clone repository:

```bash
git clone <repository-url>
cd portal-login
```

2. Buat file `.env` dari contoh yang tersedia:

```bash
cp .env.example .env
```

3. Edit file `.env` sesuai kebutuhan (ubah `SECRET_KEY` dengan key random):

```
SECRET_KEY=generate-random-key-here
```

4. Jalankan dengan Docker Compose:

```bash
docker-compose up -d
```

5. Akses aplikasi di `http://localhost:5000`.

### Login Default

Saat pertama kali dijalankan dengan database kosong, aplikasi akan membuat admin default:

| Username | Password |
|----------|----------|
| admin | admin123 |

**Peringatan:** Segera ganti password default setelah login pertama melalui menu Settings.

## Konfigurasi Environment

Semua konfigurasi dilakukan melalui file `.env`:

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `MYSQL_HOST` | `db` | Host MySQL |
| `MYSQL_USER` | `portal_user` | User MySQL |
| `MYSQL_PASSWORD` | `portal123` | Password MySQL |
| `MYSQL_DB` | `portal_db` | Nama database |
| `MYSQL_ROOT_PASSWORD` | `root123` | Root password MySQL |
| `SECRET_KEY` | - | Secret key Flask (wajib diisi) |
| `FLASK_DEBUG` | `0` | Mode debug (1 = aktif) |
| `ADMIN_PASSWORD` | `admin123` | Password default admin |

## API Endpoints

### Autentikasi

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET/POST | `/` | Halaman login |
| GET | `/portal` | Halaman portal (login required) |
| GET | `/logout` | Logout |
| GET/POST | `/change-password` | Ganti password (login required) |
| GET/POST | `/settings` | Settings: ganti nama, password, bahasa (login required) |

### Admin

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/admin` | Dashboard admin |
| POST | `/admin/apps` | Tambah aplikasi |
| PUT | `/admin/apps/<id>` | Edit aplikasi |
| DELETE | `/admin/apps/<id>` | Hapus aplikasi |
| POST | `/admin/users` | Tambah user |
| PUT | `/admin/users/<id>` | Edit user |
| DELETE | `/admin/users/<id>` | Hapus user |
| PUT | `/admin/users/<id>/reset-password` | Reset password user |

## Pengembangan

Untuk menjalankan tanpa Docker (development):

```bash
# Buat virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan MySQL terpisah, sesuaikan .env
# Jalankan aplikasi
cd app
python main.py
```

## Changelog

Lihat [CHANGELOG.md](CHANGELOG.md) untuk riwayat perubahan lengkap.

## Lisensi

Hak cipta milik developer. Digunakan untuk keperluan internal.

# Udhëzime për Startimin e Projektit

## 1. Startimi i Backend

```bash
cd backend
source venv/bin/activate  # Ose: . venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Backend do të startojë në: http://127.0.0.1:8001

## 2. Startimi i Frontend

Në një terminal të ri:

```bash
cd frontend
npm install  # Vetëm nëse nuk i keni instaluar dependencies
npm run dev
```

Frontend do të startojë në: http://localhost:5173

## 3. Krijimi i Admin User

Pas startimit të backend, mund të krijoni admin user me:

```bash
curl -X POST http://127.0.0.1:8001/api/admin/create-admin-user \
  -H "Content-Type: application/json" \
  -d '{
    "username": "andigjikolli",
    "email": "andigjikollo@gmail.com",
    "password": "andi123"
  }'
```

Ose direkt në browser: http://127.0.0.1:8001/docs dhe përdorni endpoint-in `/api/admin/create-admin-user`

## 4. Login si Admin

1. Hapni http://localhost:5173
2. Login me:
   - Username: `andigjikolli`
   - Password: `andi123`
3. Do të drejtoheni automatikisht tek Admin Dashboard

## Probleme të Mundshme

### Backend nuk starton:
- Kontrolloni nëse venv është aktivizuar
- Kontrolloni nëse porti 8001 është i lirë
- Kontrolloni nëse të gjitha dependencies janë instaluar: `pip install -r requirements.txt`

### Frontend nuk starton:
- Kontrolloni nëse node_modules ekziston: `npm install`
- Kontrolloni nëse porti 5173 është i lirë
- Kontrolloni nëse ka gabime në console

### Admin Dashboard nuk shfaqet:
- Kontrolloni nëse `is_admin` është `true` në database për user
- Kontrolloni nëse localStorage ka `is_admin: 'true'`
- Kontrolloni console për errors


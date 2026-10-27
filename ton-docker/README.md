# TON Miner — React + Django starter

پروژه بازسازی‌شده از `TON Miner.html` با فرانت‌اند React/Vite، بک‌اند Django REST Framework و پنل مدیریت Django Admin. طراحی واکنش‌گرا، تم تیره با رنگ‌های طلایی، تصاویر تعبیه‌شده در فایل اصلی، داشبورد استخراج، پلن‌های Bronze/Silver/Gold، دعوت، برداشت و نمای اولیه پنل مدیریت React در این نسخه قرار دارند.

> **مهم:** فایل HTML اصلی خودش پرداخت واقعی انجام نمی‌داد: دکمه پرداخت صرفاً سپرده را در `localStorage` ثبت می‌کرد و برداشت هم فقط محلی بود. این پروژه هم عمداً پرداخت، درآمد یا انتقال TON واقعی را شبیه‌سازی می‌کند. هیچ پرداخت یا برداشت واقعی فعال نیست و درصدها/مقادیر صرفاً تنظیمات نمونه‌ای هستند که از HTML منبع استخراج شده‌اند. پیش از استفاده مالی واقعی باید تأیید تراکنش روی زنجیره، احراز هویت، سیاست‌های امنیتی، رسیدگی به دوباره‌خرج‌کردن، صف پردازش برداشت و ممیزی امنیتی اضافه شوند.

## ساختار

- `frontend/`: React + Vite، رابط فارسی RTL و واکنش‌گرا.
- `backend/`: Django + DRF، مدل‌های پلن، حساب استخراج، واریز، برداشت، ارجاع و تنظیمات.
- `/admin/`: پنل مدیریتی Django برای کنترل کاربران، پلن‌ها، واریزها، برداشت‌ها، ارجاع‌ها و تنظیمات.
- `frontend/public/assets/`: تصاویر استخراج‌شده از HTML اصلی.

## اجرای بک‌اند

نیازمند Python 3.10+ است.

```bash
cd backend
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations miner
python manage.py migrate
python manage.py seed_plans
python manage.py createsuperuser
python manage.py runserver
```

- API سلامت: `http://127.0.0.1:8000/api/health/`
- پلن‌های فعال: `http://127.0.0.1:8000/api/plans/`
- پنل ادمین: `http://127.0.0.1:8000/admin/`
- مسیرهای حساب/واریز/برداشت نیازمند ورود Django هستند: `/api/me/`, `/api/deposits/`, `/api/withdrawals/`.

## اجرای فرانت‌اند

در ترمینال جداگانه:

```bash
cd frontend
npm install
npm run dev
```

Vite به طور پیش‌فرض روی `http://localhost:5173` اجرا می‌شود. این نسخه UI فرانت‌اند هنوز به API متصل نشده و از `localStorage` فقط برای تجربه دمو استفاده می‌کند؛ بک‌اند و API به‌عنوان پایه‌ی امن‌تر برای اتصال مرحله بعد آماده شده‌اند.

## تنظیمات محیطی بک‌اند

برای استقرار، این متغیرها را تنظیم کنید و از مقادیر پیش‌فرض توسعه استفاده نکنید:

```bash
DJANGO_SECRET_KEY='a-long-random-secret'
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS='your-domain.example'
CORS_ALLOWED_ORIGINS='https://your-domain.example'
```

در محیط production از PostgreSQL، HTTPS، کوکی‌های امن، rate limiting، مانیتورینگ، پشتیبان‌گیری و احراز هویت مناسب استفاده کنید. پنل Django Admin به حساب staff/superuser نیاز دارد.

## آنچه از HTML اصلی حفظ شده

- ۹ پلن با نرخ‌های موجود در فایل: 3/6/9/20/40/60/100/300/1000 TON و نرخ‌های 0.5% تا 4%.
- حداقل افزایش قدرت 3 TON، حداقل برداشت 100 TON، پاداش پایه نمایشی 1 TON در چرخه 6 روزه، و سقف 2.5 برابر درآمد سپرده در تنظیمات اولیه.
- بخش‌های استخراج، موجودی، توان، درآمد تخمینی، دعوت، آدرس کیف پول، تاریخچه برداشت، و تم/زبان اولیه.

مقادیر اقتصادی منبع را بدون راستی‌آزمایی تجاری/حقوقی به عنوان وعده سود یا بازده واقعی نمایش ندهید.

## اجرای پروژه با Docker

پیش‌نیاز: Docker و Docker Compose نصب باشند. از ریشه پروژه اجرا کنید:

```bash
cp .env.example .env
docker compose up --build
```

- فرانت‌اند React/Vite: `http://localhost:9000`
- بک‌اند Django/API: `http://localhost:10000/api/`
- سلامت API: `http://localhost:10000/api/health/`
- پنل مدیریت: `http://localhost:10000/admin/`

برای ساخت کاربر مدیر در ترمینال دیگر:

```bash
docker compose exec backend python manage.py createsuperuser
```

توقف سرویس‌ها: `docker compose down`. دیتابیس SQLite در volume به نام `ton_miner_db` نگه‌داری می‌شود. برای پاک‌کردن دیتابیس و تمام داده‌ها، `docker compose down -v` را اجرا کنید. این دستور برگشت‌پذیر نیست.

> این Compose برای توسعه و تست است و از Django development server استفاده می‌کند. قبل از انتشار عمومی، `DJANGO_DEBUG=0`، کلید محرمانه قوی، دامنه و HTTPS، تنظیمات امنیتی، و سرور production مناسب را تنظیم کنید.

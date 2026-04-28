# ⚖️ نظام إدارة مكتب المحاماة
### Law Firm Management System — Django + Arabic RTL

---

## 📋 متطلبات التشغيل
- Python 3.9+
- pip

---

## 🚀 خطوات تشغيل المشروع

### 1. إنشاء بيئة افتراضية وتفعيلها
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### 3. تطبيق قاعدة البيانات
```bash
python manage.py makemigrations users companies cases documents
python manage.py migrate
```

### 4. إنشاء البيانات التجريبية
```bash
python manage.py create_sample_data
```

### 5. تشغيل الخادم
```bash
python manage.py runserver
```

### 6. افتح المتصفح على
```
http://127.0.0.1:8500
```

---

## 🔐 بيانات تسجيل الدخول

| الدور | اسم المستخدم | كلمة المرور | الصلاحيات |
|-------|------------|------------|-----------|
| 👑 مدير النظام | `admin` | `admin123` | جميع الصلاحيات |
| ⚖️ محامي | `lawyer1` | `lawyer123` | إضافة/تعديل/حذف |
| ⚖️ محامية | `lawyer2` | `lawyer123` | إضافة/تعديل/حذف |
| 👤 موظفة | `employee1` | `employee123` | عرض فقط |

### لوحة الإدارة (Django Admin)
```
http://127.0.0.1:8500/admin
```

---

## 🏗️ هيكل المشروع

```
lawfirm/
├── manage.py
├── requirements.txt
├── lawfirm/                    # إعدادات المشروع
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/                  # المستخدمون والصلاحيات
│   │   ├── models.py           # نموذج CustomUser
│   │   ├── views.py            # تسجيل دخول/خروج، إدارة المستخدمين
│   │   ├── dashboard_views.py  # لوحة التحكم والبحث
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── management/commands/create_sample_data.py
│   ├── companies/              # الشركات والعملاء
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   ├── cases/                  # القضايا والجلسات
│   │   ├── models.py           # Case + Session
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   └── documents/              # المستندات والملفات
│       ├── models.py
│       ├── views.py
│       ├── forms.py
│       └── urls.py
├── templates/                  # قوالب HTML
│   ├── base.html               # القالب الأساسي (Sidebar + RTL)
│   ├── dashboard.html
│   ├── users/
│   ├── companies/
│   ├── cases/
│   └── documents/
├── static/                     # ملفات CSS/JS
└── media/                      # ملفات مرفوعة
```

---

## ✨ المميزات

### 🏢 إدارة الشركات
- إضافة / تعديل / حذف الشركات
- عرض بيانات العميل (اسم، هاتف، إيميل، عنوان)
- إحصائيات القضايا لكل شركة

### ⚖️ إدارة القضايا
- ربط القضايا بالشركات
- تصنيف بالنوع: تجارية، مدنية، جنائية، عمالية، أسرية، إدارية
- حالات: مفتوحة / مغلقة / مؤجلة
- تعيين محامي مسؤول

### 📅 الجلسات
- جدولة جلسات لكل قضية
- تتبع حالة الجلسة: مجدولة / منعقدة / مؤجلة / ملغاة
- عرض الجلسات القادمة في لوحة التحكم

### 📁 المستندات
- رفع PDF, Word, Excel, صور
- ربط المستندات بالشركة أو القضية
- تحميل وحذف الملفات
- الحد الأقصى: 10 ميجابايت

### 🔍 البحث
- بحث موحد عبر لوحة التحكم
- تصفية القضايا بالحالة

### 👥 إدارة المستخدمين
- 3 أدوار: مدير النظام، محامي، موظف
- صلاحيات مختلفة لكل دور

---

## 🎨 التصميم
- RTL كامل (عربي)
- خط Cairo من Google Fonts
- ألوان هادئة: أبيض + رمادي فاتح + أزرق
- Sidebar على اليمين
- متجاوب مع الموبايل
- Bootstrap 5 RTL

---

## ⚙️ قاعدة البيانات
- SQLite (افتراضي للتطوير)
- لاستخدام PostgreSQL، عدّل DATABASES في `lawfirm/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lawfirm_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
ثم نفّذ: `pip install psycopg2-binary`

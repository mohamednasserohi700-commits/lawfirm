#!/bin/bash
echo ""
echo "===================================="
echo " نظام إدارة مكتب المحاماة"
echo "===================================="
echo ""

# تحقق من Python
if ! command -v python3 &>/dev/null; then
    echo "[خطأ] Python 3 غير مثبت."
    exit 1
fi

echo "[1/5] إنشاء البيئة الافتراضية..."
python3 -m venv venv

echo "[2/5] تفعيل البيئة..."
source venv/bin/activate

echo "[3/5] تثبيت المكتبات..."
pip install "django>=4.2,<5.0" pillow --quiet

echo "[4/5] إعداد قاعدة البيانات..."
python manage.py makemigrations users companies cases documents --no-input
python manage.py migrate --no-input
python manage.py create_sample_data

echo "[5/5] تشغيل الخادم..."
echo ""
echo " ✅ النظام جاهز! افتح المتصفح على:"
echo "    http://127.0.0.1:8500"
echo ""
echo " بيانات الدخول:"
echo "   admin / admin123"
echo "   lawyer1 / lawyer123"
echo "   employee1 / employee123"
echo ""
python manage.py runserver 8500

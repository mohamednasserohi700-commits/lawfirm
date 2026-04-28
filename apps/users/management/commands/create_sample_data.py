"""
أمر Django لإنشاء بيانات تجريبية
الاستخدام: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.companies.models import Company
from apps.cases.models import Case, Session
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'إنشاء بيانات تجريبية للنظام'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔄 جارٍ إنشاء البيانات التجريبية...'))

        # ==============================
        # إنشاء المستخدمين
        # ==============================
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'مدير',
                'last_name': 'النظام',
                'email': 'admin@lawfirm.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('  ✅ تم إنشاء المدير: admin / admin123'))

        lawyer1, created = User.objects.get_or_create(
            username='lawyer1',
            defaults={
                'first_name': 'أحمد',
                'last_name': 'الخالد',
                'email': 'ahmed@lawfirm.com',
                'role': 'lawyer',
                'phone': '0501234567',
            }
        )
        if created:
            lawyer1.set_password('lawyer123')
            lawyer1.save()
            self.stdout.write(self.style.SUCCESS('  ✅ تم إنشاء محامي: lawyer1 / lawyer123'))

        lawyer2, created = User.objects.get_or_create(
            username='lawyer2',
            defaults={
                'first_name': 'سارة',
                'last_name': 'المنصور',
                'email': 'sara@lawfirm.com',
                'role': 'lawyer',
                'phone': '0509876543',
            }
        )
        if created:
            lawyer2.set_password('lawyer123')
            lawyer2.save()
            self.stdout.write(self.style.SUCCESS('  ✅ تم إنشاء محامية: lawyer2 / lawyer123'))

        employee, created = User.objects.get_or_create(
            username='employee1',
            defaults={
                'first_name': 'فاطمة',
                'last_name': 'العمري',
                'email': 'fatima@lawfirm.com',
                'role': 'employee',
                'phone': '0551112233',
            }
        )
        if created:
            employee.set_password('employee123')
            employee.save()
            self.stdout.write(self.style.SUCCESS('  ✅ تم إنشاء موظفة: employee1 / employee123'))

        # ==============================
        # إنشاء الشركات
        # ==============================
        companies_data = [
            {
                'name': 'شركة الفيصل للتجارة',
                'client_name': 'عبدالله الفيصل',
                'phone': '0112345678',
                'email': 'info@alfaisal.com',
                'address': 'الرياض، حي العليا، شارع الملك فهد',
                'notes': 'عميل مهم - قضايا تجارية متعددة',
            },
            {
                'name': 'مجموعة النور العقارية',
                'client_name': 'محمد النور',
                'phone': '0501234000',
                'email': 'contact@alnour.sa',
                'address': 'جدة، حي الروضة، طريق المدينة',
                'notes': 'قضايا عقارية ونزاعات ملكية',
            },
            {
                'name': 'مؤسسة الأمين للمقاولات',
                'client_name': 'خالد الأمين',
                'phone': '0557891234',
                'email': 'alameen@construction.sa',
                'address': 'الدمام، حي الشاطئ',
                'notes': 'قضايا عمالية ومقاولات',
            },
            {
                'name': 'شركة رؤية للتقنية',
                'client_name': 'نورة السليم',
                'phone': '0543219876',
                'email': 'noura@vision-tech.sa',
                'address': 'الرياض، حي الملقا',
                'notes': 'قضايا ملكية فكرية وعقود تقنية',
            },
            {
                'name': 'مطاعم الذهب السلسلة',
                'client_name': 'يوسف الذهبي',
                'phone': '0500001111',
                'email': 'gold@restaurants.sa',
                'address': 'مكة المكرمة، حي العزيزية',
                'notes': 'نزاعات تجارية مع الموردين',
            },
        ]

        companies = []
        for data in companies_data:
            company, created = Company.objects.get_or_create(
                name=data['name'],
                defaults={**data, 'created_by': admin_user}
            )
            companies.append(company)
            if created:
                self.stdout.write(f'  ✅ شركة: {company.name}')

        # ==============================
        # إنشاء القضايا
        # ==============================
        cases_data = [
            # شركة الفيصل
            {
                'company': companies[0], 'case_number': '2024/1/تجاري',
                'court_name': 'المحكمة التجارية بالرياض', 'case_type': 'commercial',
                'opponent_name': 'شركة الربح والخسارة المحدودة', 'status': 'open',
                'assigned_lawyer': lawyer1,
                'notes': 'نزاع على عقد توريد بقيمة 500,000 ريال',
            },
            {
                'company': companies[0], 'case_number': '2024/2/تجاري',
                'court_name': 'المحكمة التجارية بالرياض', 'case_type': 'commercial',
                'opponent_name': 'مؤسسة البنا والتشييد', 'status': 'postponed',
                'assigned_lawyer': lawyer1,
                'notes': 'خلاف على شروط العقد',
            },
            # مجموعة النور
            {
                'company': companies[1], 'case_number': '2024/15/عقاري',
                'court_name': 'محكمة الاستئناف بجدة', 'case_type': 'civil',
                'opponent_name': 'ورثة حسن الشمري', 'status': 'open',
                'assigned_lawyer': lawyer2,
                'notes': 'نزاع على ملكية قطعة أرض 2000 م²',
            },
            {
                'company': companies[1], 'case_number': '2023/88/مدني',
                'court_name': 'المحكمة العامة بجدة', 'case_type': 'civil',
                'opponent_name': 'البنك الأهلي التجاري', 'status': 'closed',
                'assigned_lawyer': lawyer2,
                'notes': 'قضية مغلقة - تمت التسوية',
            },
            # مؤسسة الأمين
            {
                'company': companies[2], 'case_number': '2024/33/عمالي',
                'court_name': 'المحكمة العمالية بالدمام', 'case_type': 'labor',
                'opponent_name': 'مجموعة عمال المقاولات', 'status': 'open',
                'assigned_lawyer': lawyer1,
                'notes': 'نزاع عمالي جماعي - 15 عامل',
            },
            # شركة رؤية
            {
                'company': companies[3], 'case_number': '2024/7/إداري',
                'court_name': 'المحكمة الإدارية بالرياض', 'case_type': 'administrative',
                'opponent_name': 'وزارة التجارة', 'status': 'open',
                'assigned_lawyer': lawyer2,
                'notes': 'طعن في قرار إداري',
            },
            # مطاعم الذهب
            {
                'company': companies[4], 'case_number': '2024/22/تجاري',
                'court_name': 'المحكمة التجارية بمكة', 'case_type': 'commercial',
                'opponent_name': 'شركة أغذية الجودة', 'status': 'postponed',
                'assigned_lawyer': lawyer1,
                'notes': 'نزاع على عقد توريد مواد غذائية',
            },
        ]

        cases = []
        for data in cases_data:
            case, created = Case.objects.get_or_create(
                case_number=data['case_number'],
                defaults={**data, 'created_by': admin_user}
            )
            cases.append(case)
            if created:
                self.stdout.write(f'  ✅ قضية: {case.case_number}')

        # ==============================
        # إنشاء الجلسات
        # ==============================
        today = date.today()
        sessions_data = [
            # جلسات القضية الأولى
            {'case': cases[0], 'session_date': today - timedelta(days=30), 'status': 'held', 'notes': 'الجلسة الأولى - تقديم المستندات'},
            {'case': cases[0], 'session_date': today - timedelta(days=10), 'status': 'held', 'notes': 'جلسة الاستماع للشهود'},
            {'case': cases[0], 'session_date': today + timedelta(days=5),  'status': 'scheduled', 'notes': 'جلسة المرافعة النهائية'},
            {'case': cases[0], 'session_date': today + timedelta(days=20), 'status': 'scheduled', 'notes': 'جلسة النطق بالحكم'},
            # جلسات القضية الثانية
            {'case': cases[1], 'session_date': today - timedelta(days=60), 'status': 'held', 'notes': 'الجلسة الأولى'},
            {'case': cases[1], 'session_date': today + timedelta(days=3),  'status': 'scheduled', 'notes': 'جلسة استئناف بعد التأجيل'},
            # جلسات القضية الثالثة
            {'case': cases[2], 'session_date': today - timedelta(days=15), 'status': 'postponed', 'notes': 'تم التأجيل بطلب المدعي'},
            {'case': cases[2], 'session_date': today + timedelta(days=7),  'status': 'scheduled', 'notes': 'جلسة بعد التأجيل'},
            # جلسات القضية الخامسة (عمالي)
            {'case': cases[4], 'session_date': today + timedelta(days=2),  'status': 'scheduled', 'notes': 'جلسة مبدئية'},
            {'case': cases[4], 'session_date': today + timedelta(days=14), 'status': 'scheduled', 'notes': 'جلسة الاستماع'},
            # جلسات القضية السادسة
            {'case': cases[5], 'session_date': today + timedelta(days=1),  'status': 'scheduled', 'notes': 'جلسة عاجلة'},
        ]

        for data in sessions_data:
            session, created = Session.objects.get_or_create(
                case=data['case'],
                session_date=data['session_date'],
                defaults={**data, 'created_by': admin_user}
            )
            if created:
                self.stdout.write(f'  ✅ جلسة: {session.case.case_number} - {session.session_date}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('✅ تم إنشاء البيانات التجريبية بنجاح!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📋 بيانات تسجيل الدخول:'))
        self.stdout.write('  👑 المدير:   admin / admin123')
        self.stdout.write('  ⚖️  محامي 1:  lawyer1 / lawyer123')
        self.stdout.write('  ⚖️  محامية 2: lawyer2 / lawyer123')
        self.stdout.write('  👤 موظفة:   employee1 / employee123')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📊 ملخص البيانات المنشأة:'))
        self.stdout.write(f'  🏢 الشركات: {Company.objects.count()}')
        self.stdout.write(f'  ⚖️  القضايا: {Case.objects.count()}')
        self.stdout.write(f'  📅 الجلسات: {Session.objects.count()}')
        self.stdout.write(f'  👥 المستخدمون: {User.objects.count()}')

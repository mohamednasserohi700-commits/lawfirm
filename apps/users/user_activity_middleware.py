"""
Middleware لتتبع المستخدمين المتصلين - IP والجهاز وآخر ظهور
"""
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


def get_client_ip(request):
    """استخراج الـ IP الحقيقي للمستخدم"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def get_device_info(request):
    """استخراج معلومات الجهاز من User-Agent"""
    ua = request.META.get('HTTP_USER_AGENT', '')
    if not ua:
        return 'غير معروف'

    # تحديد نظام التشغيل
    if 'Windows NT 10' in ua:
        os_name = 'Windows 10/11'
    elif 'Windows NT 6.3' in ua:
        os_name = 'Windows 8.1'
    elif 'Windows NT 6.1' in ua:
        os_name = 'Windows 7'
    elif 'Windows' in ua:
        os_name = 'Windows'
    elif 'Mac OS X' in ua:
        os_name = 'macOS'
    elif 'Android' in ua:
        os_name = 'Android'
    elif 'iPhone' in ua or 'iPad' in ua:
        os_name = 'iOS'
    elif 'Linux' in ua:
        os_name = 'Linux'
    else:
        os_name = 'غير معروف'

    # تحديد المتصفح
    if 'Chrome' in ua and 'Edg' not in ua and 'OPR' not in ua:
        browser = 'Chrome'
    elif 'Edg' in ua:
        browser = 'Edge'
    elif 'Firefox' in ua:
        browser = 'Firefox'
    elif 'Safari' in ua and 'Chrome' not in ua:
        browser = 'Safari'
    elif 'OPR' in ua:
        browser = 'Opera'
    else:
        browser = 'متصفح غير معروف'

    return f'{browser} على {os_name}'


class UserActivityMiddleware(MiddlewareMixin):
    """تتبع نشاط المستخدمين المتصلين"""

    def process_request(self, request):
        if request.user.is_authenticated:
            from .models import CustomUser
            ip = get_client_ip(request)
            device = get_device_info(request)
            now = timezone.now()

            # تحديث بيانات المستخدم بشكل مباشر (بدون استدعاء save() الكامل)
            CustomUser.objects.filter(pk=request.user.pk).update(
                last_seen=now,
                last_ip=ip,
                last_device=device,
                is_online=True,
            )

    def process_response(self, request, response):
        return response

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('courses.urls')),
    path('users/', include('users.urls')),
    path('quiz/', include('quiz.urls')),
    path('ai/', include('ai_assistant.urls')),
    path('auth/', include('social_django.urls', namespace='social')),  # Google OAuth
]

# Serve media files in production (required for user avatars since WhiteNoise only handles static)
from django.urls import re_path
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

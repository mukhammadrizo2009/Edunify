from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .utils import ai_teacher_response
import json


@login_required
def ai_page_view(request):
    """AI Muallim — to'liq chat sahifasi"""
    return render(request, 'ai_assistant/chat.html')


@login_required
@require_POST
def ai_chat_view(request):
    """AJAX endpoint — savol yuborib javob olish"""
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()

        if not question:
            return JsonResponse({'error': "Savol bo'sh"}, status=400)

        if len(question) > 500:
            return JsonResponse({'error': 'Savol juda uzun (max 500 belgi)'}, status=400)

        answer = ai_teacher_response(question, request.user.id)
        return JsonResponse({'answer': answer})

    except Exception:
        return JsonResponse({'error': 'Xato yuz berdi'}, status=500)

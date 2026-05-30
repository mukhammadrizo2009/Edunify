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
            return JsonResponse({'error': 'Empty question'}, status=400)

        if len(question) > 500:
            return JsonResponse({'error': 'Question too long (max 500 chars)'}, status=400)

        # Session'dan tanlangan tilni olish
        lang = request.session.get('lang', 'en')

        answer = ai_teacher_response(question, request.user.id, lang=lang)
        return JsonResponse({'answer': answer})

    except Exception:
        return JsonResponse({'error': 'Server error'}, status=500)

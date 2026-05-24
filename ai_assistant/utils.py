from google import genai
from google.genai import types
from django.conf import settings
from django.core.cache import cache

# =============================================
# AI MUALLIM — Faqat ta'lim mavzularida
# =============================================

AI_TEACHER_PROMPT = """
Sen "Edunify" online ta'lim platformasining AI muallimisan.

QOIDALAR:
1. FAQAT quyidagi mavzularda javob berasan:
   - Matematika, Algebra, Geometriya
   - Fizika, Kimyo, Biologiya
   - Ingliz tili, Tojik tili, Rus tili, O'zbek tili
   - Tarix, Geografiya, Informatika

2. Agar o'quvchi boshqa mavzuda savol bersa:
   "Kechirasiz, men faqat ta'lim mavzularida yordam bera olaman." deb javob ber.

3. Javoblarni QISQA va TUSHUNARLI qilib ber.
4. Imkon bo'lsa, misol keltir.
5. O'zbek tilida javob ber (agar o'quvchi boshqa tilda yozsa, o'sha tilda javob ber).
"""

def _get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def ai_teacher_response(user_question, user_id):
    # Rate limiting — har foydalanuvchi minutiga 5 ta so'rov
    cache_key = f"ai_limit_{user_id}"
    requests_count = cache.get(cache_key, 0)

    if requests_count >= 5:
        return "Iltimos, 1 daqiqa kuting. So'rovlar limiti tugadi."

    cache.set(cache_key, requests_count + 1, timeout=60)

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == 'your_gemini_api_key':
        return "Tizimda Gemini API kaliti sozlanmagan. Iltimos, administrator bilan bog'laning."

    try:
        client = _get_client()
        prompt = f"{AI_TEACHER_PROMPT}\n\nO'quvchi savoli: {user_question}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return "Hozir AI muallim bilan bog'lanib bo'lmadi. Keyinroq urinib ko'ring."


# =============================================
# AI PROGRESS TAHLILCHI — Test so'ng feedback
# =============================================

def analyze_progress(student_data):
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == 'your_gemini_api_key':
        return "Tizimda Gemini API kaliti sozlanmagan, AI tahlil hozircha mavjud emas."

    try:
        client = _get_client()
        percentage = round((student_data['score'] / student_data['total']) * 100)

        prompt = f"""
O'quvchining test natijasini tahlil qil va qisqa feedback ber.

Ma'lumotlar:
- Fan: {student_data['subject']}
- Mavzu: {student_data['topic']}
- Natija: {student_data['score']}/{student_data['total']} ({percentage}%)
- Vaqt: {student_data['time_spent']} daqiqa
- Xato savollar soni: {len(student_data['wrong_questions'])}

Quyidagi formatda javob ber:
1. Qisqa baho (1 gap) — maqtov yoki dalda
2. Kuchli tomoni (1 gap)
3. Zaif tomoni (1 gap)
4. Tavsiya (1 gap) — nima qilsin keyingi?

Mehribon, rag'batlantiruvchi ohangda yoz. O'zbek tilida. 4 gapdan ko'p bo'lmasin.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception:
        return "AI tahlil hozircha mavjud emas."

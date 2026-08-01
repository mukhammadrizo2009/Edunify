# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
from django.conf import settings
from django.core.cache import cache

# =============================================
# AI MUALLIM — Faqat ta'lim mavzularida
# =============================================

AI_TEACHER_PROMPT = """
Sen "Edunify" online ta'lim platformasining AI muallimisan. Ismingiz "Edu".

═══════════════════════════════════════════
🎓 ASOSIY VAZIFANG
═══════════════════════════════════════════
O'quvchilarga quyidagi fanlar bo'yicha sifatli, tushunarli va qiziqarli tarzda yordam berish:

📐 Aniq fanlar:
  - Matematika (arifmetika, algebra, geometriya, trigonometriya, calculus)
  - Fizika (mexanika, elektr, optika, termodinamika, kvant fizikasi)
  - Kimyo (organik, anorganik, fizik kimyo, reaksiyalar, davriy jadval)
  - Informatika (dasturlash, algoritmlar, ma'lumotlar tuzilmasi, veb, sun'iy intellekt)

🔬 Tabiiy fanlar:
  - Biologiya (hujayra, genetika, evolyutsiya, anatomiya, ekologiya)
  - Geografiya (fizik, iqtisodiy, siyosiy geografiya, xaritalar)

📚 Gumanitar fanlar:
  - Tarix (jahon tarixi, Tojikiston tarixi, sivilizatsiyalar)
  - Adabiyot (o'zbek, rus, jahon adabiyoti, she'riyat tahlili)

🌐 Tillar:
  - O'zbek tili (grammatika, imlo, uslubiyat)
  - Ingliz tili (grammar, vocabulary, speaking, writing, IELTS/SAT tayyorgarlik)
  - Rus tili (грамматика, лексика, произношение)
  - Tojik tili (грамматика ва луғат)

═══════════════════════════════════════════
🗣️ TIL QOIDASI — ENG MUHIM
═══════════════════════════════════════════
- O'quvchi qaysi tilda yozsa, SEN HAM O'SHA TILDA javob ber
- O'zbek (lotin yoki kiril), Ingliz, Rus, Tojik — barchasi qabul
- Aralash tilda yozilgan bo'lsa, asosiy tilda javob ber
- HECH QACHON tilni o'zgartirma, tuzatma yoki boshqa tilda yozishni tavsiya qilma

═══════════════════════════════════════════
📋 JAVOB BERISH USLUBI
═══════════════════════════════════════════
1. TUSHUNTIRIB BER — oddiy va aniq so'zlar bilan
2. MISOL KELTIR — har doim amaliy misol bilan mustahkamla
3. BOSQICHMA-BOSQICH — murakkab masalalarni qadamlarga bo'l
4. FORMULA/QOIDA — kerak bo'lsa formulani aniq ko'rsat
5. TEKSHIR — javob oxirida asosiy fikrni qisqacha takrorla
6. RAG'BATLANTIR — o'quvchini rag'batlantiruvchi so'zlar qo'sh

Javob uzunligi:
  - Oddiy savol → 3-6 qator
  - Tushuntirish talab qiladigan mavzu → 10-20 qator
  - Murakkab masala → batafsil, lekin ortiqcha emas

═══════════════════════════════════════════
🧮 MATEMATIK / ILMIY MASALALAR
═══════════════════════════════════════════
- Formulani ko'rsat
- Qadamlarni raqamlab yoz
- Har bir qadamda nima qilayotganingni tushuntir
- Javobni birlik bilan yoz (m, kg, s, va h.)
- Mumkin bo'lsa, tekshirish usulini ham ko'rsat

Misol format:
  📌 Masala: ...
  ✏️ Yechim:
    1-qadam: ...
    2-qadam: ...
    3-qadam: ...
  ✅ Javob: ...

═══════════════════════════════════════════
🌍 TIL O'RGANISH (Ingliz/Rus/Tojik/O'zbek)
═══════════════════════════════════════════
- Grammatika qoidasini + 3 ta misol
- Talaffuz ko'rsatmasi (kerak bo'lsa)
- Umumiy xatolarni tushuntir
- Amaliy jumlalar bilan mustahkamla

═══════════════════════════════════════════
🚫 CHEKLOVLAR
═══════════════════════════════════════════
Quyidagi mavzularda JAVOB BERMA:
  - Siyosat, din, mafkura
  - Shaxsiy maslahatlar (tibbiy, yuridik, moliyaviy)
  - O'yin-kulgi, seriallar, sport yangiliklari
  - Zararli, noqonuniy yoki noo'rin kontent
  - Ta'lim bilan bog'liq bo'lmagan har qanday mavzu

Bunday savollarga javob:
  O'quvchi qaysi tilda yozgan bo'lsa, o'sha tilda: 
  "Kechirasiz, men faqat ta'lim mavzularida yordam bera olaman. 
   Matematika, fizika, tillar yoki boshqa darslar bo'yicha savol bering — 
   mamnuniyat bilan yordam beraman! 😊"

═══════════════════════════════════════════
💡 MAXSUS KO'RSATMALAR
═══════════════════════════════════════════
- O'quvchi xato qilsa → muloyimlik bilan tuzat, kamsitma
- Tushunmasa → boshqacha usul bilan tushuntir
- "Bilmadim" dema → "Keling, birgalikda ko'rib chiqaylik" de
- Har doim IJOBIY va QUVVATLOVCHI ton saqlat
- Emoji'dan o'rinli foydalanish mumkin (ortiqcha emas)
- "Edu" sifatida o'zingni tanishtir, lekin har gapda takrorlama

═══════════════════════════════════════════
🔑 MISOL JAVOBLAR
═══════════════════════════════════════════

[O'zbek tilida — matematika]
Savol: "Kvadrat tenglamani qanday yechaman?"
Javob:
"Kvadrat tenglama: ax² + bx + c = 0 ko'rinishida bo'ladi.

Yechish usuli — diskriminant formula:
  D = b² - 4ac

  • D > 0 → 2 ta yechim: x = (-b ± √D) / 2a
  • D = 0 → 1 ta yechim: x = -b / 2a
  • D < 0 → haqiqiy yechim yo'q

📌 Misol: x² - 5x + 6 = 0
  D = 25 - 24 = 1
  x₁ = (5 + 1)/2 = 3
  x₂ = (5 - 1)/2 = 2
✅ Javob: x = 3 va x = 2

Tekshirish: 3² - 5(3) + 6 = 9 - 15 + 6 = 0 ✓"

[English — grammar]
Question: "When do I use 'a' vs 'an'?"
Answer:
"Great question! The rule is simple:
  • Use 'a' before consonant sounds → a book, a cat, a university*
  • Use 'an' before vowel sounds → an apple, an hour*, an egg

*Note: It's about SOUND, not spelling!
  - 'university' starts with 'yu' sound → a university
  - 'hour' starts with 'ow' sound → an hour

Practice: a/an ___?
  • ___ orange ✓ an
  • ___ car ✓ a
  • ___ honest person ✓ an (silent h!)"

[Русский язык — физика]  
Вопрос: "Что такое скорость?"
Ответ:
"Скорость — это физическая величина, показывающая, какой путь тело проходит за единицу времени.

📐 Формула: v = s / t
  • v — скорость (м/с)
  • s — расстояние (м)  
  • t — время (с)

📌 Пример: Автомобиль проехал 150 км за 2 часа.
  v = 150 / 2 = 75 км/ч

✅ Чем больше скорость, тем быстрее движется тело!"
"""

def _get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def ai_teacher_response(user_question, user_id, lang='en'):
    # Rate limiting — har foydalanuvchi minutiga 5 ta so'rov
    cache_key = f"ai_limit_{user_id}"
    requests_count = cache.get(cache_key, 0)

    if requests_count >= 5:
        msgs = {
            'ru': 'Пожалуйста, подождите 1 минуту. Лимит запросов исчерпан.',
            'tj': 'Лутфан 1 дақиқа интизор шавед. Лимити дархостҳо тамом шуд.',
            'en': 'Please wait 1 minute. Request limit reached.',
        }
        return msgs.get(lang, msgs['en'])

    cache.set(cache_key, requests_count + 1, timeout=60)

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == 'your_gemini_api_key':
        msgs = {
            'ru': 'Ключ API Gemini не настроен. Обратитесь к администратору.',
            'tj': 'Калиди API Gemini танзим нашудааст. Ба маъмур муроҷиат кунед.',
            'en': 'Gemini API key is not configured. Please contact the administrator.',
        }
        return msgs.get(lang, msgs['en'])

    # Language instruction injected at the TOP of the prompt
    lang_force = {
        'ru': '⚠️ ОБЯЗАТЕЛЬНО: Отвечай ТОЛЬКО на русском языке, независимо от языка вопроса.',
        'tj': '⚠️ ҲАТМАН: Фақат ба забони тоҷикӣ ҷавоб деҳ, сарфи назар аз забони савол.',
        'en': '⚠️ MANDATORY: Answer ONLY in English, regardless of the question language.',
        'uz': '⚠️ MAJBURIY: Faqat O\'zbek tilida javob ber, savolning tilididan qat\'iy nazar.',
    }.get(lang, '⚠️ MANDATORY: Answer ONLY in English.')

    try:
        client = _get_client()
        prompt = f"{lang_force}\n\n{AI_TEACHER_PROMPT}\n\nStudent question: {user_question}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        import traceback
        traceback.print_exc()
        msgs = {
            'ru': 'AI-учитель временно недоступен. Попробуйте позже.',
            'tj': 'Муаллими AI муваққатан дастнорас аст. Баъдтар кӯшиш кунед.',
            'en': 'AI Teacher is temporarily unavailable. Please try again later.',
        }
        return msgs.get(lang, msgs['en'])



# =============================================
# AI PROGRESS TAHLILCHI — Test so'ng feedback
# =============================================

def analyze_progress(student_data, lang='en'):
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == 'your_gemini_api_key':
        return "Gemini API key is not configured in the system, AI analysis is currently unavailable."

    try:
        client = _get_client()
        percentage = round((student_data['score'] / student_data['total']) * 100)

        # Til bo'yicha ko'rsatma
        lang_instruction = {
            'ru': 'Отвечай на русском языке. Используй дружественный и мотивирующий тон.',
            'tj': 'Ба забони тоҷикӣ ҷавоб деҳ. Оҳанги дӯстона ва ҳавасмандкунанда истифода бар.',
            'en': 'Answer in English. Use a friendly and motivating tone.',
        }.get(lang, 'Answer in English. Use a friendly and motivating tone.')

        prompt = f"""
Analyze the student's quiz result and give short feedback.

{lang_instruction}

Data:
- Subject: {student_data['subject']}
- Topic: {student_data['topic']}
- Result: {student_data['score']}/{student_data['total']} ({percentage}%)
- Time: {student_data['time_spent']} minutes
- Number of wrong answers: {len(student_data['wrong_questions'])}

Respond in EXACTLY this format (4 sentences max):
1. Brief assessment (1 sentence) — praise or encouragement
2. Strong point (1 sentence)
3. Weak point (1 sentence)
4. Recommendation (1 sentence) — what to do next?

IMPORTANT: Write ONLY in the language specified above. No more than 4 sentences.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception:
        return "AI analysis is currently unavailable."


# =============================================
# AI TEST GENERATOR — O'qituvchilar uchun
# =============================================

QUIZ_GENERATOR_PROMPT = """
Sen professional ta'lim test generatorisan. O'qituvchi senga test yaratishni so'raydi.
Sen FAQAT JSON formatida javob berishing kerak.

QOIDALAR:
1. Savollar ilmiy jihatdan to'g'ri bo'lishi kerak
2. 4 ta variant (A, B, C, D) bo'lishi shart
3. Faqat BITTA to'g'ri javob bo'lishi kerak
4. Savollar berilgan fan va sinf darajasiga mos bo'lishi kerak
5. Variantlar bir-biriga o'xshash, lekin faqat bittasi to'g'ri bo'lishi kerak
6. Har bir savol aniq va tushunarli bo'lishi kerak

MUHIM: Javobingni FAQAT quyidagi JSON formatida ber, boshqa hech narsa yozma:

{
  "title": "Test nomi",
  "subject": "Fan nomi",
  "grade": "Sinf",
  "questions": [
    {
      "text": "Savol matni",
      "option_a": "A varianti",
      "option_b": "B varianti",
      "option_c": "C varianti",
      "option_d": "D varianti",
      "correct": "A"
    }
  ]
}

MUHIM QOIDALAR:
- "correct" qiymati faqat "A", "B", "C" yoki "D" bo'lishi kerak
- Hech qanday izoh, tushuntirish yoki qo'shimcha matn YOZMA
- FAQAT JSON qaytar
- Savollar soni o'qituvchi so'ragan miqdorda bo'lsin
- Agar o'qituvchi sonini ko'rsatmasa, 10 ta savol yarat
"""


def generate_quiz_with_ai(teacher_prompt, lang='en'):
    """
    O'qituvchining so'roviga asosan AI yordamida test savollarini yaratadi.
    Returns: dict with 'title', 'subject', 'grade', 'questions' list
    Raises: Exception on failure
    """
    import json
    import re

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == 'your_gemini_api_key':
        raise ValueError("Gemini API key is not configured.")

    # Til bo'yicha ko'rsatma
    lang_instruction = {
        'ru': 'Саволлар ва вариантларни РУСЧА ёз. JSON ichidagi barcha матнлар русский тилда бўлсин.',
        'tj': 'Саволҳо ва вариантҳоро бо ЗАБОНИ ТОҶИКӢ нависед. Ҳамаи матнҳо бояд тоҷикӣ бошанд.',
        'en': 'Write all questions and options in ENGLISH.',
    }.get(lang, 'Write all questions and options in ENGLISH.')

    try:
        client = _get_client()
        full_prompt = (
            f"{lang_instruction}\n\n"
            f"{QUIZ_GENERATOR_PROMPT}\n\n"
            f"O'qituvchining so'rovi: {teacher_prompt}"
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
        )

        raw_text = response.text.strip()

        # JSON ni ajratib olish (```json ... ``` yoki oddiy JSON)
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw_text)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # To'g'ridan-to'g'ri JSON sifatida parse qilishga harakat
            # Boshidan { topib, oxiridan } topamiz
            start = raw_text.find('{')
            end = raw_text.rfind('}')
            if start != -1 and end != -1:
                json_str = raw_text[start:end + 1]
            else:
                raise ValueError("AI javobida JSON topilmadi.")

        data = json.loads(json_str)

        # Validatsiya
        if 'questions' not in data or not isinstance(data['questions'], list):
            raise ValueError("AI javobi noto'g'ri formatda — 'questions' topilmadi.")

        if len(data['questions']) == 0:
            raise ValueError("AI hech qanday savol yaratmadi.")

        # Har bir savolni tekshirish
        valid_questions = []
        for i, q in enumerate(data['questions']):
            if not all(k in q for k in ('text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct')):
                continue  # Bu savolni o'tkazib yuboramiz
            if q['correct'] not in ('A', 'B', 'C', 'D'):
                q['correct'] = 'A'  # Default
            valid_questions.append(q)

        if not valid_questions:
            raise ValueError("AI yaratgan savollar noto'g'ri formatda.")

        data['questions'] = valid_questions
        data.setdefault('title', 'AI Test')
        data.setdefault('subject', '')
        data.setdefault('grade', '')

        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"AI javobini JSON sifatida o'qib bo'lmadi: {str(e)}")
    except Exception as e:
        if 'JSONDecodeError' in str(type(e).__name__):
            raise ValueError(f"AI javobini JSON sifatida o'qib bo'lmadi: {str(e)}")
        raise

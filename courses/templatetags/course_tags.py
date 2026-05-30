"""
Kategoriya nomini tanlangan tilda qaytaruvchi template filter.
Ishlatish: {{ cat|cat_name:lang }}
"""
from django import template

register = template.Library()

# Agar DB da tarjima yo'q bo'lsa — fallback map
CATEGORY_MAP = {
    'Fizika':     {'tj': 'Физика', 'ru': 'Физика', 'en': 'Physics'},
    'Ingliz Tili':{'tj': 'Забони Англисӣ', 'ru': 'Английский Язык', 'en': 'English Language'},
    'Matematika': {'tj': 'Математика', 'ru': 'Математика', 'en': 'Mathematics'},
    'Kimyo':      {'tj': 'Химия', 'ru': 'Химия', 'en': 'Chemistry'},
    'Biologiya':  {'tj': 'Биология', 'ru': 'Биология', 'en': 'Biology'},
    'Tarix':      {'tj': 'Таърих', 'ru': 'История', 'en': 'History'},
    'Informatika':{'tj': 'Информатика', 'ru': 'Информатика', 'en': 'IT / Computer Science'},
    'Geografiya': {'tj': 'Ҷуғрофия', 'ru': 'География', 'en': 'Geography'},
    'Adabiyot':   {'tj': 'Адабиёт', 'ru': 'Литература', 'en': 'Literature'},
}

@register.filter
def cat_name(category, lang):
    if lang == 'tj':
        name = getattr(category, 'name_tj', '') or ''
        if not name:
            name = CATEGORY_MAP.get(category.name, {}).get('tj', category.name)
    elif lang == 'ru':
        name = getattr(category, 'name_ru', '') or ''
        if not name:
            name = CATEGORY_MAP.get(category.name, {}).get('ru', category.name)
    elif lang == 'en':
        name = getattr(category, 'name_en', '') or ''
        if not name:
            name = CATEGORY_MAP.get(category.name, {}).get('en', category.name)
    else:
        name = category.name
    return name

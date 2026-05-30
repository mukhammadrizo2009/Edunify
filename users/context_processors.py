def language_processor(request):
    """
    Context processor to handle multi-language settings (en, tj, ru).
    English is the main default language. Uzbek is completely replaced by English.
    Saves selected language in the session for persistence across pages.
    """
    lang = request.GET.get('lang')
    if lang in ['en', 'tj', 'ru']:
        request.session['lang'] = lang
    
    current_lang = request.session.get('lang', 'en')
    if current_lang not in ['en', 'tj', 'ru']:
        current_lang = 'en'
        request.session['lang'] = 'en'
        
    return {
        'lang': current_lang
    }

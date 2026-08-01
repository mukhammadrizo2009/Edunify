def language_processor(request):
    """
    Context processor to handle multi-language settings (en, tj, ru).
    The actual language switching via GET parameter is now handled by 
    users.middleware.LanguageMiddleware to ensure views get the correct language.
    """
    current_lang = request.session.get('lang', 'en')
    if current_lang not in ['en', 'tj', 'ru']:
        current_lang = 'en'
        
    return {
        'lang': current_lang
    }

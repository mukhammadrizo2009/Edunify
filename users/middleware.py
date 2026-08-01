class LanguageMiddleware:
    """
    Middleware to intercept 'lang' GET parameter and set it in the session
    before the request reaches any views. This fixes the issue where
    language switching required two clicks because the context processor
    ran after views were executed.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get('lang')
        if lang in ['en', 'tj', 'ru']:
            request.session['lang'] = lang
            
        current_lang = request.session.get('lang', 'en')
        if current_lang not in ['en', 'tj', 'ru']:
            request.session['lang'] = 'en'

        return self.get_response(request)

# backend/core/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

class LanguageMiddleware(MiddlewareMixin):
    """Middleware to handle language preferences"""
    
    def process_request(self, request):
        # Get language from session, cookie, or default to English
        language = request.session.get('language')
        
        if not language:
            # Check cookie
            language = request.COOKIES.get('language')
        
        if not language:
            # Check URL parameter
            language = request.GET.get('lang')
        
        if not language:
            # Default to English
            language = 'en'
        
        # Validate language
        if language not in ['en', 'sw']:
            language = 'en'
        
        request.LANGUAGE = language
        request.session['language'] = language

class TranslationContextMiddleware(MiddlewareMixin):
    """Add translation function to template context"""
    
    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            # Add translation function to context
            from core.services.translation import translator
            response.context_data['translate'] = lambda text: translator.translate(text, 'SW' if request.LANGUAGE == 'sw' else 'EN')
            response.context_data['current_language'] = request.LANGUAGE
        return response
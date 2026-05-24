# backend/core/services/translation.py
import requests
import json
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class DeepLTranslator:
    """DeepL API client for language translation"""
    
    def __init__(self):
        # Get API key from Django settings (which reads from .env)
        self.api_key = settings.DEEPL_API_KEY
        self.base_url = settings.DEEPL_API_URL
        self.supported_languages = ['EN', 'SW']  # English, Swahili
        
        # Warn if no API key
        if not self.api_key:
            logger.warning("DeepL API key not found. Translation will not work.")
    
    def translate(self, text, target_lang='SW', source_lang='EN'):
        """
        Translate text using DeepL API with Header Authentication
        
        Args:
            text: Text to translate (string or list)
            target_lang: Target language code (SW for Swahili, EN for English)
            source_lang: Source language code (default EN)
        
        Returns:
            Translated text or None if error
        """
        if not text:
            return text
        
        # If no API key, return original text
        if not self.api_key:
            return text
        
        # Check cache first (cache for 24 hours)
        cache_key = f"deepl_{source_lang}_{target_lang}_{hash(text)}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # NEW: Use Header Authentication instead of form body
            headers = {
                'Authorization': f'DeepL-Auth-Key {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            # Prepare request body
            data = {
                'text': [text],
                'target_lang': target_lang,
                'source_lang': source_lang,
            }
            
            response = requests.post(
                self.base_url, 
                headers=headers,
                json=data, 
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result['translations'][0]['text']
                
                # Cache the result
                cache.set(cache_key, translated, 3600 * 24)  # 24 hours
                return translated
            else:
                logger.error(f"DeepL API error: {response.status_code} - {response.text}")
                return text  # Return original text on error
                
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Return original text on error
    
    def translate_batch(self, texts, target_lang='SW', source_lang='EN'):
        """Translate multiple texts at once"""
        if not texts:
            return texts
        
        try:
            headers = {
                'Authorization': f'DeepL-Auth-Key {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            data = {
                'text': texts,
                'target_lang': target_lang,
                'source_lang': source_lang,
            }
            
            response = requests.post(
                self.base_url, 
                headers=headers,
                json=data, 
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return [t['text'] for t in result['translations']]
            else:
                logger.error(f"DeepL API batch error: {response.status_code}")
                return texts
                
        except Exception as e:
            logger.error(f"Batch translation error: {str(e)}")
            return texts

# Singleton instance
translator = DeepLTranslator()
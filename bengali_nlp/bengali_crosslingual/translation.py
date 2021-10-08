import os
from google.oauth2 import service_account
from google.cloud import translate_v2 as translate
import six


class GoogleTranslateTranslator():
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    
    def __init__(self, ROOT = "bengali_crosslingual") -> None:
        credential_path = os.path.join(ROOT, "MultilingualTranslationAccess.json")
        credentials = service_account.Credentials.from_service_account_file(credential_path)
        self.translate_client = translate.Client(credentials=credentials)

        self.MAX_TEXT_LENGTH = 8192

    def translate_bulk(self, text, target_lang, source_lang=None):
        """"Ad Hoc Method for translating large texts """
        def splits_gen(text):
            if len(text) < self.MAX_TEXT_LENGTH:
                yield text
                return
            
            i = self.MAX_TEXT_LENGTH - text[self.MAX_TEXT_LENGTH::-1].index(" ")
            yield text[:i]
            
            for e in splits_gen(text[i+1:]):
                yield e
                
        return " ".join(translate(segment, target_lang, source_lang)['text'] for segment in splits_gen(text))

    def translate(self, text, target_lang, source_lang=None):
        # Translate a single text
        if isinstance(text, six.binary_type):
            text = text.decode('utf-8')

        if source_lang:
            result = self.translate_client.translate(text, source_language=source_lang, target_language=target_lang)
            detected_lang = None
        else:
            result = self.translate_client.translate(text, source_language=source_lang, target_language=target_lang)
            detected_lang = result['detectedSourceLanguage']
            # print(u'Detected source language: {}'.format(detected_lang))

        # print(u'Text: {}'.format(result['input']))
        # print(u'Translation: {}'.format(result['translatedText']))
        return {
            "text": result['translatedText'],
            "detected_language": detected_lang
        }


    def translate_list(self, text, target_lang, source_lang=None):
        # Translate a sequence of texts
        if isinstance(text, six.binary_type):
            text = text.decode('utf-8')

        if source_lang:
            result = self.translate_client.translate(text, source_language=source_lang, target_language=target_lang)
            detected_lang = None
            return {
                "text": [res['translatedText'] for res in result],
                "detected_language": [None for res in result]
            }
        else:
            result = self.translate_client.translate(text, source_language=source_lang, target_language=target_lang)
            return {
                "text": [res['translatedText'] for res in result],
                "detected_language": [res['detectedSourceLanguage'] for res in result]
            }
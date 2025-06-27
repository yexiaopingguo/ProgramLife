from google.cloud import translate_v2 as translate

def translate_query(query, source_lang, target_lang):
    # Instantiates a client
    client = translate.Client()

    # Translates the query from the source language to the target language
    translation = client.translate(query, source_language=source_lang, target_language=target_lang)

    # Extracts the translated text from the response
    translated_query = translation['translatedText']

    return translated_query
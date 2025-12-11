"""
Context processors for the dashboard app.
"""


def language_context(request):
    """Add language-related context variables."""
    current_language = request.session.get('language', 'en')
    return {
        'current_language': current_language,
        'available_languages': [
            {'code': 'en', 'name': 'English', 'flag': '🇺🇸'},
            {'code': 'es', 'name': 'Español', 'flag': '🇪🇸'},
        ],
    }

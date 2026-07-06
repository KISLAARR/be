# app/web/components/styles.py

def get_base_styles() -> str:
    """
    Возвращает HTML-теги для подключения CSS-файлов.
    Костыль чтобы не переписывать все упоминания. 
    """
    return """
    <link rel="stylesheet" href="/static/src/css/main.css">
    <script src="/static/dist/main.js" defer></script>
    """
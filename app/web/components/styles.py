# app/web/components/styles.py

def get_base_styles() -> str:
    """
    Возвращает HTML-теги для подключения CSS-файлов.
    Костыль чтобы не переписывать все упоминания. 
    """
    return """
    <link rel="stylesheet" href="/static/css/global.css">
    <link rel="stylesheet" href="/static/css/components.css">
    <link rel="stylesheet" href="/static/css/pages.css">
    """
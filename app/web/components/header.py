# app/web/components/header.py
from app.web.components.icons import ICON_MENU

def render_header(current_page: str = "home") -> str:
    return f"""
    <header id="main-header">
        <div id="header-nav">
            <div id="header-logo-wrapper">
                <a href="/" id="header-logo">руми.</a>
            </div>
            <button id="header-burger" aria-label="Открыть меню">
                {ICON_MENU}
            </button>
        </div>
    </header>
    """
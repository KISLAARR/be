# app/web/components/header.py
def render_header(current_page: str = "home", user=None) -> str:
    return f"""
    <header id="main-header">
        <div id="header-nav">
            <a href="/" id="header-logo">руми.</a>
        </div>
    </header>
    """
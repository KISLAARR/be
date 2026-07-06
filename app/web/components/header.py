# app/web/components/header.py
def render_header(current_page: str = "home", user=None) -> str:
    """Хедер с обновлёнными стилями и поведением."""
    
    if user:
        auth_block = f"""
        <a href="/profile" id="user-greeting" class="auth-link">
            👤 <span>{user.full_name or 'Профиль'}</span>
        </a>
        """
        mobile_auth_block = f"""
        <a href="/profile" id="mobile-user-greeting" class="auth-link">
            👤 <span>{user.full_name or 'Профиль'}</span>
        </a>
        """
    else:
        auth_block = '<a href="/login" id="login-btn" class="login-btn">Войти</a>'
        mobile_auth_block = '<a href="/login" id="mobile-login-btn" class="login-btn">Войти</a>'
    
    return f"""
    <header id="main-header">
        <nav id="header-nav">
            <a href="/" id="header-logo">руми.</a>
            
            <ul id="header-menu">
                <li><a class="header-menu-link {'active' if current_page == 'home' else ''}" href="/">Главная</a></li>
                <li><a class="header-menu-link {'active' if current_page == 'salons' else ''}" href="/salons">Салоны</a></li>
                <li><a class="header-menu-link {'active' if current_page == 'business' else ''}" href="/business">Для бизнеса</a></li>
                <li><a class="header-menu-link {'active' if current_page == 'offer' else ''}" href="/offer">Предложения</a></li>
                <li><a class="header-menu-link {'active' if current_page == 'about' else ''}" href="/about">Манифест</a></li>
            </ul>
            
            <div id="header-auth">
                {auth_block}
            </div>

            <button id="mobile-menu-btn" aria-label="Открыть меню">
                <svg viewBox="0 0 24 24" width="28" height="28" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none">
                    <path d="M3 12h18M3 6h18M3 18h18"/>
                </svg>
            </button>
        </nav>

        <div id="mobile-dropdown">
            <ul id="mobile-menu-list">
                <li><a class="header-menu-link" href="/">Главная</a></li>
                <li><a class="header-menu-link" href="/salons">Салоны</a></li>
                <li><a class="header-menu-link" href="/business">Для бизнеса</a></li>
                <li><a class="header-menu-link" href="/offer">Предложения</a></li>
                <li><a class="header-menu-link" href="/about">Манифест</a></li>
            </ul>
            <div id="mobile-auth-container">
                {mobile_auth_block}
            </div>
        </div>
    </header>

    <script>
    (function() {{
        const menuBtn = document.getElementById('mobile-menu-btn');
        const dropdown = document.getElementById('mobile-dropdown');
        
        if (menuBtn && dropdown) {{
            menuBtn.addEventListener('click', function() {{
                dropdown.classList.toggle('active');
            }});
        }}
    }})();
    </script>
    """
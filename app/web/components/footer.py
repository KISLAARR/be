# app/web/components/footer.py

def render_footer() -> str:
    """Возвращает HTML-подвал сайта."""
    return """
    <footer style="border-top: 1px solid var(--color-border); padding: 2rem 0; text-align: center; color: var(--color-muted); font-size: 0.875rem; margin-top: 4rem;">
        <div class="section-container">
            <p>© 2026 руми. Все права защищены.</p>
        </div>
    </footer>
    """
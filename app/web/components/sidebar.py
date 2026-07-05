# app/web/components/sidebar.py

def render_sidebar(current_page: str = "home", user=None) -> str:
    """Боковая панель навигации."""
    # У незарегистрированного пользователя бокового меню быть не должно
    if not user:
        return ""
    
    # Секция "Бизнес/Стать моделью" должны показываться соответвенно - бизнес аккаунту/обычному пользователю.
    business_section = ""
    if hasattr(user, 'role') and user.role.value == "client":
        business_section = """
        <div class="mt-6 border-t border-border pt-4">
            <div class="space-y-1">
                <a class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-muted transition-colors hover:bg-surface-alt hover:text-heading" href="/model/dashboard/">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-camera" aria-hidden="true"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path><circle cx="12" cy="13" r="3"></circle></svg>
                    Стать моделью
                </a>
                <a class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-muted transition-colors hover:bg-surface-alt hover:text-heading" href="/business/dashboard/">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-briefcase" aria-hidden="true"><path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path><rect width="20" height="14" x="2" y="6" rx="2"></rect></svg>
                    Бизнес
                </a>
            </div>
        </div>
        """

    # Вспомогательная функция для выделения активной страницы
    def get_active_class(page_id):
        return "bg-accent-light text-heading" if current_page == page_id else "text-muted hover:bg-surface-alt hover:text-heading"

    return f"""
    <!-- Оверлей для закрытия меню при клике мимо (только на мобильных) -->
    <div id="sidebar-overlay" class="fixed inset-0 z-40 hidden bg-black/50 lg:hidden" onclick="toggleUserSidebar()"></div>

    <aside id="user-sidebar" class="fixed right-0 top-0 z-50 flex h-screen w-64 flex-col border-l border-border bg-surface transition-transform translate-x-full lg:translate-x-0 lg:flex">
        <div class="flex h-full flex-col">
            <div class="flex items-center justify-between border-b border-border px-5 py-4">
                <a class="text-display text-xl" href="/">
                    <span style="color:var(--color-primary)">руми.</span>
                </a>
                <div class="flex items-center gap-2">
                    <button class="rounded-full p-1.5 text-muted transition-colors hover:bg-surface-alt hover:text-heading lg:hidden" onclick="toggleUserSidebar()">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x" aria-hidden="true">
                            <path d="M18 6 6 18"></path>
                            <path d="m6 6 12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="flex-1 overflow-y-auto px-3 py-4">
                <div class="space-y-1">
                    <a class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors {get_active_class('profile')}" href="/profile/">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user" aria-hidden="true"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                        Мой профиль
                    </a>
                    <a class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors {get_active_class('bookings')}" href="/bookings/">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar-days" aria-hidden="true"><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path><path d="M8 14h.01"></path><path d="M12 14h.01"></path><path d="M16 14h.01"></path><path d="M8 18h.01"></path><path d="M12 18h.01"></path><path d="M16 18h.01"></path></svg>
                        Мои записи
                    </a>
                    <a class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors {get_active_class('favorites')}" href="/favorites/">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-heart" aria-hidden="true"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path></svg>
                        Избранное
                    </a>
                    <a class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors {get_active_class('settings')}" href="/settings/">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-settings" aria-hidden="true"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                        Настройки
                    </a>
                </div>
                
                {business_section}
                
                <div class="mt-6 border-t border-border pt-4">
                    <button onclick="location.href='/logout'" class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors hover:bg-surface-alt" style="color:var(--color-primary)">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-log-out" aria-hidden="true"><path d="m16 17 5-5-5-5"></path><path d="M21 12H9"></path><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path></svg>
                        Выход
                    </button>
                </div>
            </div>
        </div>
    </aside>
    """
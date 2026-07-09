# app/web/components/icons.py
"""SVG-иконки для использования в компонентах и страницах."""

ICON_SEARCH = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-search w-5 h-5 sm:w-6 sm:h-6 text-white" aria-hidden="true">'
    '<path d="m21 21-4.34-4.34"></path><circle cx="11" cy="11" r="8"></circle></svg>'
)

ICON_SCISSORS = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-scissors w-4 h-4" aria-hidden="true">'
    '<circle cx="6" cy="6" r="3"></circle><path d="M8.12 8.12 12 12"></path>'
    '<path d="M20 4 8.12 15.88"></path><circle cx="6" cy="18" r="3"></circle>'
    '<path d="M14.8 14.8 20 20"></path></svg>'
)

ICON_SPARKLES = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-sparkles w-4 h-4" aria-hidden="true">'
    '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"></path>'
    '<path d="M20 3v4"></path><path d="M22 5h-4"></path><path d="M4 17v2"></path><path d="M5 18H3"></path></svg>'
)

ICON_MAP_PIN = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-map-pin h-4 w-4 shrink-0" aria-hidden="true">'
    '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"></path>'
    '<circle cx="12" cy="10" r="3"></circle></svg>'
)

ICON_CLOCK = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-clock h-4 w-4 shrink-0" aria-hidden="true">'
    '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
)

ICON_CHECK = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-check h-5 w-5" aria-hidden="true">'
    '<path d="M20 6 9 17l-5-5"></path></svg>'
)

ICON_CHECK_SMALL = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-check h-4 w-4 shrink-0" aria-hidden="true">'
    '<path d="M20 6 9 17l-5-5"></path></svg>'
)

# Декоративная графика для hero-секции
HERO_DECORATIVE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 500" width="100%" height="100%" id="beauty-bg-elements">
  <g transform="translate(100, 120) rotate(-25)">
    <rect x="10" y="40" width="30" height="50" rx="4" fill="#F3EBF1" stroke="#A3629B" stroke-width="3" />
    <rect x="15" y="25" width="20" height="15" fill="none" stroke="#A3629B" stroke-width="3" />
    <path d="M 15 25 L 15 5 L 35 15 L 35 25 Z" fill="#A3629B" stroke="#A3629B" stroke-width="3" stroke-linejoin="round" />
    <line x1="10" y1="55" x2="40" y2="55" stroke="#A3629B" stroke-width="2" />
  </g>
  <g transform="translate(380, 90) rotate(35)">
    <circle cx="30" cy="120" r="16" fill="none" stroke="#A3629B" stroke-width="3" />
    <circle cx="65" cy="120" r="16" fill="none" stroke="#A3629B" stroke-width="3" />
    <path d="M 30 104 L 55 20 C 55 20, 52 40, 45 65" fill="none" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <path d="M 65 104 L 40 20 C 40 20, 43 40, 50 65" fill="none" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <circle cx="47.5" cy="75" r="4" fill="#A3629B" />
  </g>
  <g transform="translate(60, 320) rotate(15)">
    <path d="M 10 15 L 210 15 C 215 15, 215 25, 210 25 L 10 25 C 5 25, 5 15, 10 15 Z" fill="#A3629B" />
    <line x1="25" y1="25" x2="25" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <line x1="45" y1="25" x2="45" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <line x1="65" y1="25" x2="65" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <line x1="85" y1="25" x2="85" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <line x1="105" y1="25" x2="105" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <line x1="125" y1="25" x2="125" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <line x1="145" y1="25" x2="145" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <line x1="165" y1="25" x2="165" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <line x1="185" y1="25" x2="185" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
    <line x1="195" y1="25" x2="195" y2="60" stroke="#A3629B" stroke-width="3" stroke-linecap="round" />
  </g>
  <g transform="translate(340, 260) rotate(-10)">
    <rect x="10" y="10" width="130" height="90" rx="8" fill="#F3EBF1" stroke="#A3629B" stroke-width="3" />
    <circle cx="40" cy="38" r="14" fill="none" stroke="#A3629B" stroke-width="2" />
    <circle cx="40" cy="38" r="10" fill="#A3629B" opacity="0.3" />
    <circle cx="80" cy="38" r="14" fill="none" stroke="#A3629B" stroke-width="2" />
    <circle cx="80" cy="38" r="10" fill="#A3629B" />
    <circle cx="40" cy="72" r="14" fill="none" stroke="#A3629B" stroke-width="2" />
    <circle cx="40" cy="72" r="10" fill="#A3629B" />
    <circle cx="80" cy="72" r="14" fill="none" stroke="#A3629B" stroke-width="2" />
    <circle cx="80" cy="72" r="10" fill="#F3EBF1" stroke="#A3629B" stroke-width="1" />
    <rect x="112" y="25" width="10" height="60" rx="2" fill="none" stroke="#A3629B" stroke-width="2" />
    <line x1="112" y1="35" x2="122" y2="35" stroke="#A3629B" stroke-width="2" />
  </g>
</svg>"""

ICON_PERCENT = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-percent" aria-hidden="true">'
    '<line x1="19" x2="5" y1="5" y2="19"></line>'
    '<circle cx="6.5" cy="6.5" r="2.5"></circle>'
    '<circle cx="17.5" cy="17.5" r="2.5"></circle>'
    '</svg>'
)

ICON_STORE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-store" aria-hidden="true">'
    '<path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>'
    '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>'
    '<path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>'
    '<path d="M2 7h20"></path>'
    '<path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>'
    '</svg>'
)

ICON_ARROW_RIGHT = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-arrow-right h-4 w-4" aria-hidden="true">'
    '<path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path>'
    '</svg>'
)

# ========== Иконки для сайдбара (размер 18x18) ==========
ICON_HOUSE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-house" aria-hidden="true">'
    '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path>'
    '<path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>'
    '</svg>'
)

ICON_BUILDING2 = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-building2" aria-hidden="true">'
    '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"></path>'
    '<path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"></path>'
    '<path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"></path>'
    '<path d="M10 6h4"></path><path d="M10 10h4"></path><path d="M10 14h4"></path><path d="M10 18h4"></path>'
    '</svg>'
)

ICON_BRIEFCASE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-briefcase" aria-hidden="true">'
    '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>'
    '<rect width="20" height="14" x="2" y="6" rx="2"></rect>'
    '</svg>'
)

ICON_GIFT = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-gift" aria-hidden="true">'
    '<path d="M20 12v10H4V12"></path>'
    '<path d="M2 7h20v5H2z"></path>'
    '<path d="M12 22V7"></path>'
    '<path d="M12 7h7.5a2.5 2.5 0 0 0 0-5h-5A2.5 2.5 0 0 0 12 4a2.5 2.5 0 0 0-2.5-2.5h-5a2.5 2.5 0 0 0 0 5H12z"></path>'
    '</svg>'
)

ICON_FILE_TEXT = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-file-text" aria-hidden="true">'
    '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path>'
    '<path d="M14 2v4a2 2 0 0 0 2 2h4"></path>'
    '<path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path>'
    '</svg>'
)

ICON_USER = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-user" aria-hidden="true">'
    '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>'
    '<circle cx="12" cy="7" r="4"></circle>'
    '</svg>'
)

# Иконка бургер-меню 28x28
ICON_MENU = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-menu" aria-hidden="true">'
    '<path d="M3 12h18"></path><path d="M3 6h18"></path><path d="M3 18h18"></path>'
    '</svg>'
)

# Иконки для страницы "Для бизнеса"
ICON_CALENDAR_DAYS = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-calendar-days h-6 w-6" aria-hidden="true">'
    '<path d="M8 2v4"></path><path d="M16 2v4"></path>'
    '<rect width="18" height="18" x="3" y="4" rx="2"></rect>'
    '<path d="M3 10h18"></path>'
    '<path d="M8 14h.01"></path><path d="M12 14h.01"></path><path d="M16 14h.01"></path>'
    '<path d="M8 18h.01"></path><path d="M12 18h.01"></path><path d="M16 18h.01"></path>'
    '</svg>'
)

ICON_CHART_COLUMN = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-chart-column h-6 w-6" aria-hidden="true">'
    '<path d="M3 3v16a2 2 0 0 0 2 2h16"></path>'
    '<path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path>'
    '</svg>'
)

ICON_USERS = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-users h-6 w-6" aria-hidden="true">'
    '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>'
    '<path d="M16 3.128a4 4 0 0 1 0 7.744"></path>'
    '<path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>'
    '<circle cx="9" cy="7" r="4"></circle>'
    '</svg>'
)

ICON_SHIELD_CHECK = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-shield-check h-6 w-6" aria-hidden="true">'
    '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path>'
    '<path d="m9 12 2 2 4-4"></path>'
    '</svg>'
)

ICON_TRENDING_UP = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-trending-up h-6 w-6" aria-hidden="true">'
    '<path d="M16 7h6v6"></path>'
    '<path d="m22 7-8.5 8.5-5-5L2 17"></path>'
    '</svg>'
)

ICON_SETTINGS = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-settings h-6 w-6" aria-hidden="true">'
    '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>'
    '<circle cx="12" cy="12" r="3"></circle>'
    '</svg>'
)

ICON_MEGAPHONE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-megaphone h-6 w-6" aria-hidden="true">'
    '<path d="m3 11 18-5v12L3 14v-3z"></path>'
    '<path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"></path>'
    '</svg>'
)

ICON_ROCKET = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-rocket h-6 w-6" aria-hidden="true">'
    '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path>'
    '<path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path>'
    '<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path>'
    '<path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path>'
    '</svg>'
)

ICON_CIRCLE_CHECK = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-circle-check h-4 w-4 shrink-0" aria-hidden="true">'
    '<circle cx="12" cy="12" r="10"></circle>'
    '<path d="m9 12 2 2 4-4"></path>'
    '</svg>'
)

ICON_ARROW_LEFT = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-arrow-left h-4 w-4" aria-hidden="true">'
    '<path d="m12 19-7-7 7-7"></path><path d="M19 12H5"></path>'
    '</svg>'
)

ICON_LOCK = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'class="lucide lucide-lock h-4 w-4" aria-hidden="true">'
    '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect>'
    '<path d="M7 11V7a5 5 0 0 1 10 0v4"></path>'
    '</svg>'
)
# app/web/components/styles.py

def get_base_styles() -> str:
    """Возвращает общие CSS-стили для всех страниц."""
    return """
    <style>
        :root {
            --color-primary: #F28C6F;
            --color-accent: #E8A0BF;
            --color-heading: #1a1a2e;
            --color-body: #4a4a5a;
            --color-muted: #6b7280;
            --color-border: #e5e7eb;
            --color-surface: #ffffff;
            --color-surface-alt: #f9fafb;
            --color-accent-light: #fef3f0;
            --font-heading: 'Inter', sans-serif;
            --font-body: 'Inter', sans-serif;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: var(--font-body);
            color: var(--color-body);
            background: var(--color-surface);
            line-height: 1.6;
        }
        
        .section-container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .section-py { padding: 5rem 0; }
        
        .text-display {
            font-family: var(--font-heading);
            color: var(--color-heading);
            font-weight: 800;
        }
        
        .text-subtitle {
            color: #2d2d3a;
            font-weight: 600;
        }
        
        .text-body { color: var(--color-body); }
        .text-muted { color: var(--color-muted); }
        .text-label { color: var(--color-heading); font-weight: 500; }
        
        .bg-surface { background: var(--color-surface); }
        .bg-surface-alt { background: var(--color-surface-alt); }
        
        .badge {
            display: inline-block;
            background: var(--color-accent-light);
            color: var(--color-primary);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.375rem 1rem;
            border-radius: 2rem;
        }
        
        .btn-primary {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 2rem;
            font-weight: 600;
            font-size: 0.875rem;
            text-decoration: none;
            border: none;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
        }
        
        .btn-primary:hover {
            transform: scale(1.05);
            opacity: 0.95;
        }
        
        .btn-outline {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            border: 2px solid var(--color-border);
            color: var(--color-heading);
            padding: 0.75rem 1.5rem;
            border-radius: 2rem;
            font-weight: 600;
            font-size: 0.875rem;
            text-decoration: none;
            transition: background 0.2s;
        }
        
        .btn-outline:hover { background: var(--color-surface); }
        
        .card {
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 1rem;
            padding: 1.5rem;
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }
        
        .grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3 {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """
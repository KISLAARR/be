# app/web/pages/business/tabs/warehouse.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import (
    InventoryItem, InventoryAudit, InventoryAuditItem, InventoryAuditStatus,
    Service as ServiceModel, User as UserModel,
)
from app.services.inventory_service import InventoryService


async def render_warehouse_tab(db: AsyncSession, salon, masters, master_ids, warehouse_filters: dict) -> str:
    """Вкладка «Склад» — мини-склады мастеров, приход, инвентаризация."""

    master_user_names = {}
    for m in masters:
        mu = (await db.execute(select(UserModel).where(UserModel.id == m.user_id))).scalar_one_or_none()
        master_user_names[m.id] = mu.full_name if mu else "—"

    # Остатки по всем мастерам
    all_items: list[tuple] = []  # (master_id, InventoryItem)
    for m in masters:
        for item in await InventoryService.get_master_stock(db, m.id):
            all_items.append((m.id, item))

    low_stock = [it for _mid, it in all_items if it.quantity <= it.min_quantity]

    stock_rows = ""
    for mid, item in sorted(all_items, key=lambda t: (master_user_names.get(t[0], ""), t[1].name)):
        is_low = item.quantity <= item.min_quantity
        qty_style = "color:#ef4444;font-weight:700" if is_low else "font-weight:600"
        stock_rows += f"""
        <tr>
            <td>{master_user_names.get(mid, '—')}</td>
            <td>{item.name}</td>
            <td><span style="{qty_style}">{item.quantity:g}</span> {item.unit}</td>
            <td>{item.min_quantity:g} {item.unit}</td>
            <td>{item.cost_per_unit} ₽/{item.unit}</td>
        </tr>"""

    master_options = "".join(f'<option value="{m.id}">{master_user_names.get(m.id, "—")}</option>' for m in masters)

    # Незакрытые списания — визиты без формы расхода
    unreported = await InventoryService.unreported_bookings(db, salon.id)
    unreported_rows = ""
    for b in unreported[:30]:
        service = (await db.execute(select(ServiceModel).where(ServiceModel.id == b.service_id))).scalar_one_or_none()
        client = (await db.execute(select(UserModel).where(UserModel.id == b.client_id))).scalar_one_or_none()
        unreported_rows += f"""
        <tr>
            <td>{b.start_time.strftime('%d.%m.%Y %H:%M')}</td>
            <td>{client.full_name if client else '—'}</td>
            <td>{master_user_names.get(b.master_id, '—')}</td>
            <td>{service.name if service else '—'}</td>
        </tr>"""

    # Открытая инвентаризация (?audit_id=...), если указана и принадлежит салону
    audit_html = ""
    audit_id_raw = warehouse_filters.get("audit_id")
    if audit_id_raw and audit_id_raw.isdigit():
        audit = (await db.execute(
            select(InventoryAudit).where(InventoryAudit.id == int(audit_id_raw))
        )).scalar_one_or_none()
        if audit and audit.master_id in master_ids and audit.status == InventoryAuditStatus.DRAFT:
            audit_items = (await db.execute(
                select(InventoryAuditItem, InventoryItem)
                .join(InventoryItem, InventoryItem.id == InventoryAuditItem.item_id)
                .where(InventoryAuditItem.audit_id == audit.id)
            )).all()
            rows = "".join(f"""
                <tr>
                    <td>{item.name}</td>
                    <td>{ai.expected_quantity:g} {item.unit}</td>
                    <td><input type="number" step="0.01" class="audit-actual" data-item-id="{item.id}"
                        value="{ai.expected_quantity:g}" style="width:6rem;padding:0.4rem;border:1px solid var(--color-border);border-radius:0.4rem"></td>
                </tr>""" for ai, item in audit_items)
            audit_html = f"""
            <div class="card" style="margin-bottom:1.5rem;border:2px solid var(--color-primary)">
                <h3 style="margin-bottom:0.25rem">📋 Инвентаризация — {master_user_names.get(audit.master_id, '—')}</h3>
                <p class="text-muted" style="margin-bottom:1rem;font-size:0.85rem">Акт #{audit.id}. Укажите фактический остаток по каждой позиции и подтвердите — расхождения спишутся/зачислятся автоматически.</p>
                <table>
                    <thead><tr><th>Позиция</th><th>Ожидается</th><th>Факт</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
                <button id="confirmAuditBtn" class="btn-primary" style="margin-top:1rem" data-audit-id="{audit.id}">Подтвердить инвентаризацию</button>
            </div>"""

    return f"""
    <div id="tab-warehouse" class="tab-content">
        <div class="analytics-kpi">
            <div class="kpi-card"><div class="kpi-label">Позиций на складах</div><div class="kpi-value">{len(all_items)}</div></div>
            <div class="kpi-card"><div class="kpi-label">Заканчиваются</div><div class="kpi-value" style="color:#ef4444">{len(low_stock)}</div></div>
            <div class="kpi-card"><div class="kpi-label">Визитов без списания</div><div class="kpi-value" style="color:#f59e0b">{len(unreported)}</div></div>
        </div>

        {audit_html}

        <div class="grid-2" style="margin-bottom:1.5rem">
            <div class="card">
                <h3 style="margin-bottom:1rem">➕ Новая позиция номенклатуры</h3>
                <form id="newItemForm">
                    <select name="master_id" required style="width:100%;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem;margin-bottom:0.5rem">
                        <option value="">Мастер</option>{master_options}
                    </select>
                    <input name="name" placeholder="Название (например, Краска Wella 60мл)" required style="width:100%;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem;margin-bottom:0.5rem">
                    <div style="display:flex;gap:0.5rem;margin-bottom:0.5rem">
                        <input name="unit" placeholder="Ед. (мл/г/шт)" required style="flex:1;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem">
                        <input name="cost_per_unit" type="number" placeholder="Цена за ед., ₽" required style="flex:1;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem">
                        <input name="min_quantity" type="number" step="0.01" placeholder="Мин. остаток" value="0" style="flex:1;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem">
                    </div>
                    <button type="submit" class="btn-primary" style="width:100%">Добавить позицию</button>
                </form>
            </div>
            <div class="card">
                <h3 style="margin-bottom:1rem">📥 Приход на склад</h3>
                <form id="receiveForm">
                    <select name="master_id" id="receiveMaster" required style="width:100%;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem;margin-bottom:0.5rem">
                        <option value="">Мастер</option>{master_options}
                    </select>
                    <select name="item_id" id="receiveItem" required style="width:100%;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem;margin-bottom:0.5rem">
                        <option value="">Сначала выберите мастера</option>
                    </select>
                    <div style="display:flex;gap:0.5rem;margin-bottom:0.5rem">
                        <input name="quantity" type="number" step="0.01" placeholder="Количество" required style="flex:1;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem">
                        <input name="comment" placeholder="Комментарий (необязательно)" style="flex:2;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem">
                    </div>
                    <button type="submit" class="btn-primary" style="width:100%">Оприходовать</button>
                </form>
            </div>
        </div>

        <div class="card" style="overflow-x:auto;margin-bottom:1.5rem">
            <h3 style="margin-bottom:1rem">Остатки по складам</h3>
            <table>
                <thead><tr><th>Мастер</th><th>Позиция</th><th>Остаток</th><th>Мин. остаток</th><th>Цена</th></tr></thead>
                <tbody>{stock_rows or '<tr><td colspan="5" style="text-align:center;padding:2rem;color:var(--color-muted)">Номенклатура пуста — добавьте первую позицию</td></tr>'}</tbody>
            </table>
        </div>

        <div class="card" style="overflow-x:auto;margin-bottom:1.5rem">
            <h3 style="margin-bottom:1rem">⚠️ Визиты без списания расходников</h3>
            <table>
                <thead><tr><th>Дата</th><th>Клиент</th><th>Мастер</th><th>Услуга</th></tr></thead>
                <tbody>{unreported_rows or '<tr><td colspan="4" style="text-align:center;padding:2rem;color:var(--color-muted)">Всё списано</td></tr>'}</tbody>
            </table>
        </div>

        <div class="card">
            <h3 style="margin-bottom:1rem">📋 Инвентаризация</h3>
            <p class="text-muted" style="margin-bottom:1rem;font-size:0.85rem">Открывает акт пересчёта для выбранного мастера — фиксирует текущие системные остатки как ожидаемые.</p>
            <form method="post" id="startAuditForm" style="display:flex;gap:0.5rem">
                <select name="master_id_path" id="auditMaster" required style="flex:1;padding:0.6rem;border:1px solid var(--color-border);border-radius:0.5rem">
                    <option value="">Мастер</option>{master_options}
                </select>
                <button type="submit" class="btn-outline">Начать инвентаризацию</button>
            </form>
        </div>
    </div>

    <script>
    (function() {{
        const salonId = {salon.id};

        const newItemForm = document.getElementById('newItemForm');
        if (newItemForm) newItemForm.addEventListener('submit', function(e) {{
            const masterId = this.master_id.value;
            if (!masterId) {{ e.preventDefault(); alert('Выберите мастера'); return; }}
            this.action = '/api/v1/inventory/master/' + masterId + '/items';
            this.method = 'post';
        }});

        const receiveMaster = document.getElementById('receiveMaster');
        const receiveItem = document.getElementById('receiveItem');
        if (receiveMaster) receiveMaster.addEventListener('change', async function() {{
            const masterId = this.value;
            receiveItem.innerHTML = '<option value="">Загрузка…</option>';
            if (!masterId) {{ receiveItem.innerHTML = '<option value="">Сначала выберите мастера</option>'; return; }}
            try {{
                const res = await fetch('/api/v1/inventory/master/' + masterId + '/stock');
                const items = await res.json();
                receiveItem.innerHTML = '<option value="">Позиция</option>' + items.map(
                    i => `<option value="${{i.id}}">${{i.name}} (остаток ${{i.quantity}} ${{i.unit}})</option>`
                ).join('');
            }} catch (err) {{
                receiveItem.innerHTML = '<option value="">Ошибка загрузки</option>';
            }}
        }});

        const receiveForm = document.getElementById('receiveForm');
        if (receiveForm) receiveForm.addEventListener('submit', function(e) {{
            const masterId = this.master_id.value;
            if (!masterId) {{ e.preventDefault(); alert('Выберите мастера'); return; }}
            this.action = '/api/v1/inventory/master/' + masterId + '/receive';
            this.method = 'post';
        }});

        const startAuditForm = document.getElementById('startAuditForm');
        if (startAuditForm) startAuditForm.addEventListener('submit', function(e) {{
            const masterId = this.master_id_path.value;
            if (!masterId) {{ e.preventDefault(); alert('Выберите мастера'); return; }}
            this.action = '/api/v1/inventory/master/' + masterId + '/audit/start';
        }});

        const confirmBtn = document.getElementById('confirmAuditBtn');
        if (confirmBtn) confirmBtn.addEventListener('click', async function() {{
            const auditId = this.dataset.auditId;
            const inputs = document.querySelectorAll('.audit-actual');
            const actual_quantities = {{}};
            inputs.forEach(inp => {{ actual_quantities[inp.dataset.itemId] = parseFloat(inp.value) || 0; }});
            try {{
                const res = await fetch('/api/v1/inventory/audit/' + auditId + '/confirm', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ actual_quantities: actual_quantities }})
                }});
                if (res.ok) {{
                    window.location.href = '/business/dashboard?salon_id=' + salonId + '&tab=warehouse';
                }} else {{
                    const data = await res.json().catch(() => ({{}}));
                    alert(data.detail || 'Не удалось подтвердить инвентаризацию');
                }}
            }} catch (err) {{
                alert('Ошибка соединения с сервером');
            }}
        }});
    }})();
    </script>"""

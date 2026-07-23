# app/web/pages/business/tabs/services.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Service, Master, User as UserModel
from app.web.components.icons import ICON_EDIT, ICON_TRASH


async def render_services_tab(db: AsyncSession, salon, masters, can_manage: bool = False) -> str:
    """Вкладка Услуги — управление услугами мастеров."""

    master_ids = [m.id for m in masters]
    services_rows = ""

    if master_ids:
        # Фильтруем только активные услуги (is_active == True)
        services_result = await db.execute(
            select(Service, Master).join(Master, Service.master_id == Master.id)
            .where(Service.master_id.in_(master_ids), Service.is_active == True)
            .order_by(Master.id, Service.price)
        )
        services_data = services_result.all()

        total_services = len(services_data)

        for service, master in services_data:
            user_result = await db.execute(select(UserModel).where(UserModel.id == master.user_id))
            master_user = user_result.scalar_one_or_none()
            master_name = master_user.full_name if master_user else "—"

            actions_cell = ""
            if can_manage:
                actions_cell = f"""
                <td class="services-actions-cell">
                    <button class="services-edit-btn" onclick="openEditModal({service.id}, '{service.name.replace("'", "\\'")}', {service.price}, {service.duration_minutes}, '{service.description.replace("'", "\\'") if service.description else ''}', {service.master_id})" title="Редактировать">
                        {ICON_EDIT}
                    </button>
                    <form method="post" action="/api/v1/services/{service.id}/delete" style="display:inline-block; margin:0;">
                        <button type="submit" class="services-delete-btn" title="Удалить" onclick="return confirm('Удалить услугу «{service.name.replace("'", "\\'")}»?')">
                            {ICON_TRASH}
                        </button>
                    </form>
                </td>
                """

            services_rows += f"""
            <tr>
                <td><strong>{service.name}</strong></td>
                <td>{master_name}</td>
                <td>{service.duration_minutes} мин</td>
                <td><strong>{service.price:,} ₽</strong></td>
                <td class="services-desc">{service.description or '—'}</td>
                {actions_cell}
            </tr>"""
    else:
        total_services = 0

    # Список мастеров для выпадающего списка
    master_options = ""
    for m in masters:
        user_result = await db.execute(select(UserModel).where(UserModel.id == m.user_id))
        master_user = user_result.scalar_one_or_none()
        master_name = master_user.full_name if master_user else "—"
        master_options += f'<option value="{m.id}">{master_name} — {m.specialization}</option>'

    # Кнопка добавления (только если есть права)
    add_btn = ""
    if can_manage:
        add_btn = f'''
        <button class="services-add-btn" id="servicesAddBtn">
            + Добавить услугу
        </button>
        '''

    # Заголовок с количеством услуг и кнопкой
    header_html = f"""
    <div class="services-header">
        <div class="services-stats">
            <span class="services-count">{total_services}</span>
            <span class="services-label">Всего услуг</span>
        </div>
        {add_btn}
    </div>
    """

    # Таблица с услугами
    table_html = f"""
    <div class="services-table-wrap">
        <table class="services-table">
            <thead>
                <tr>
                    <th>Услуга</th>
                    <th>Мастер</th>
                    <th>Длительность</th>
                    <th>Цена</th>
                    <th>Описание</th>
                    {f'<th class="services-actions-header">Действия</th>' if can_manage else ''}
                </tr>
            </thead>
            <tbody>
                {services_rows or '<tr><td colspan="6" class="services-empty">Пока нет услуг</td></tr>'}
            </tbody>
        </table>
    </div>
    """

    # Модальное окно (только если есть права)
    modal_html = ""
    if can_manage:
        modal_html = f"""
        <div class="services-modal-overlay" id="servicesModal">
            <div class="services-modal-box">
                <button class="services-modal-close" id="servicesModalClose">&times;</button>
                <h2 id="servicesModalTitle">Добавить услугу</h2>
                <form id="servicesForm" method="post" action="/api/v1/services/create">
                    <input type="hidden" name="service_id" id="serviceId">
                    <div class="services-form-group">
                        <label for="serviceMaster">Мастер *</label>
                        <select name="master_id" id="serviceMaster" required>
                            <option value="">Выберите мастера</option>
                            {master_options}
                        </select>
                    </div>
                    <div class="services-form-group">
                        <label for="serviceName">Название услуги *</label>
                        <input type="text" name="name" id="serviceName" required placeholder="Например: Стрижка машинкой">
                    </div>
                    <div class="services-form-row">
                        <div class="services-form-group">
                            <label for="servicePrice">Цена (₽) *</label>
                            <input type="number" name="price" id="servicePrice" required placeholder="1500">
                        </div>
                        <div class="services-form-group">
                            <label for="serviceDuration">Длительность (мин) *</label>
                            <input type="number" name="duration_minutes" id="serviceDuration" required placeholder="30">
                        </div>
                    </div>
                    <div class="services-form-group">
                        <label for="serviceDescription">Описание</label>
                        <textarea name="description" id="serviceDescription" rows="2" placeholder="Подробнее об услуге..."></textarea>
                    </div>
                    <div class="services-modal-actions">
                        <button type="button" class="services-btn-cancel" id="servicesModalCancel">Отмена</button>
                        <button type="submit" class="services-btn-save">Сохранить</button>
                    </div>
                </form>
            </div>
        </div>
        """

    return f"""
    <div id="tab-services" class="tab-content services-tab">
        {header_html}
        {table_html}
        {modal_html}
    </div>
    """
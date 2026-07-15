// static/js/pages/salon-detail.js

document.addEventListener('DOMContentLoaded', function() {
    let selectedSlot = null;
    let selectedMasterId = null;
    let selectedServiceId = null;

    // ===== ИЗБРАННОЕ (салон и мастера) =====
    async function loadFavorites() {
        try {
            const response = await fetch('/api/v1/favorites/my');
            if (response.ok) {
                const data = await response.json();
                
                // Салоны
                document.querySelectorAll('.salon-top-fav[data-type="salon"]').forEach(btn => {
                    const id = parseInt(btn.dataset.id);
                    if (data.salon_ids.includes(id)) {
                        btn.classList.add('liked');
                    } else {
                        btn.classList.remove('liked');
                    }
                });
                
                // Мастера
                document.querySelectorAll('.master-fav[data-type="master"]').forEach(btn => {
                    const id = parseInt(btn.dataset.id);
                    if (data.master_ids.includes(id)) {
                        btn.classList.add('liked');
                    } else {
                        btn.classList.remove('liked');
                    }
                });
            }
        } catch (e) {
            // пользователь не авторизован
        }
    }

    document.querySelectorAll('.salon-top-fav, .master-fav').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            const type = this.dataset.type;
            const id = this.dataset.id;
            const isLiked = this.classList.contains('liked');

            try {
                const response = await fetch(`/api/v1/favorites/toggle-${type}/${id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                });
                if (response.ok) {
                    if (isLiked) {
                        this.classList.remove('liked');
                    } else {
                        this.classList.add('liked');
                    }
                } else if (response.status === 302) {
                    window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                } else {
                    alert('Не удалось изменить избранное. Попробуйте позже.');
                }
            } catch (err) {
                console.error(err);
                alert('Ошибка соединения.');
            }
        });
    });

    loadFavorites();

    // ===== ПЕРЕКЛЮЧЕНИЕ МЕЖДУ СПИСКОМ И ДЕТАЛЬНЫМ ВИДОМ =====
    const mastersListContainer = document.getElementById('masters-list-container');
    const masterDetailContainer = document.getElementById('master-detail-container');

    // Кнопки "Записаться" в карточках мастеров
    document.querySelectorAll('.master-book-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const masterId = this.dataset.masterId;
            showMasterDetail(masterId);
        });
    });

    // Клик по всей карточке мастера тоже может открывать детали (опционально)
    document.querySelectorAll('.master-card').forEach(card => {
        card.addEventListener('click', function() {
            const masterId = this.dataset.masterId;
            showMasterDetail(masterId);
        });
    });

    function showMasterDetail(masterId) {
        // Скрываем список мастеров
        mastersListContainer.style.display = 'none';
        // Показываем детальный вид нужного мастера
        document.querySelectorAll('.master-detail').forEach(el => {
            el.classList.add('hidden');
        });
        const detail = document.querySelector(`.master-detail[data-master-id="${masterId}"]`);
        if (detail) {
            detail.classList.remove('hidden');
        }
    }

    // Кнопка "Назад к мастерам"
    document.querySelectorAll('.back-to-masters').forEach(btn => {
        btn.addEventListener('click', function() {
            // Скрываем все детали
            document.querySelectorAll('.master-detail').forEach(el => {
                el.classList.add('hidden');
            });
            // Показываем список
            mastersListContainer.style.display = '';
        });
    });

    // ===== ВЫБОР УСЛУГИ (в детальном виде) =====
    document.querySelectorAll('.service-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const masterId = parseInt(this.dataset.masterId);
            const serviceId = parseInt(this.dataset.serviceId);
            const serviceName = this.dataset.serviceName;
            const price = this.dataset.price;
            const duration = parseInt(this.dataset.duration);

            // Убираем выделение с других кнопок (опционально)
            document.querySelectorAll('.service-btn').forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');

            selectedMasterId = masterId;
            selectedServiceId = serviceId;

            // Скрываем все контейнеры слотов
            document.querySelectorAll('.slots-container').forEach(c => c.classList.add('hidden'));

            // Показываем контейнер слотов для этого мастера
            const slotsContainer = document.getElementById(`detail-slots-${masterId}`);
            const slotsTitle = document.getElementById(`detail-slots-title-${masterId}`);
            const slotGrid = document.getElementById(`detail-slot-grid-${masterId}`);

            if (slotsContainer && slotsTitle && slotGrid) {
                slotsTitle.innerHTML = `
                    📅 Время для «${serviceName}» (${price} ₽):
                    <br>
                    <input type="date" id="detail-datePicker-${masterId}" value="${new Date().toISOString().split('T')[0]}" class="date-picker">
                `;
                slotGrid.innerHTML = '<p class="text-muted text-xs">Выберите дату для загрузки слотов...</p>';
                slotsContainer.classList.remove('hidden');

                loadSlotsForDetail(masterId, serviceId, serviceName, price, duration);

                // Обработчик изменения даты
                setTimeout(() => {
                    const datePicker = document.getElementById(`detail-datePicker-${masterId}`);
                    if(datePicker) {
                        datePicker.addEventListener('change', function() {
                            loadSlotsForDetail(masterId, serviceId, serviceName, price, duration);
                        });
                    }
                }, 50);
            }
        });
    });

    // Функция загрузки слотов (адаптирована для детального вида)
    async function loadSlotsForDetail(masterId, serviceId, serviceName, price, duration) {
        const datePicker = document.getElementById(`detail-datePicker-${masterId}`);
        const dateStr = datePicker ? datePicker.value : new Date().toISOString().split('T')[0];
        const slotGrid = document.getElementById(`detail-slot-grid-${masterId}`);

        if (!slotGrid) return;

        slotGrid.innerHTML = '<p class="text-muted text-xs">Загружаем слоты...</p>';

        try {
            const response = await fetch(`/api/v1/bookings/available/${masterId}?date=${dateStr}&service_id=${serviceId}`);
            const data = await response.json();

            if (data.slots && data.slots.length > 0) {
                const now = new Date();
                const todayStr = new Date().toISOString().split('T')[0];
                let slotsHtml = '';
                for (const slot of data.slots) {
                    const slotDate = new Date(slot);
                    if (dateStr === todayStr && slotDate < now) continue;

                    const timeStr = slotDate.toTimeString().slice(0, 5);
                    const fullSlot = slotDate.getFullYear() + '-' + 
                        String(slotDate.getMonth() + 1).padStart(2, '0') + '-' + 
                        String(slotDate.getDate()).padStart(2, '0') + 'T' + 
                        String(slotDate.getHours()).padStart(2, '0') + ':' + 
                        String(slotDate.getMinutes()).padStart(2, '0');

                    slotsHtml += `<button class="slot-btn" data-fullslot="${fullSlot}" data-master="${masterId}" data-service="${serviceId}" data-name="${serviceName}" data-price="${price}">${timeStr}</button>`;
                }
                if (slotsHtml) {
                    slotGrid.innerHTML = slotsHtml;
                } else {
                    slotGrid.innerHTML = '<p class="text-muted text-xs">Нет свободных окон на выбранную дату.</p>';
                }
            } else {
                slotGrid.innerHTML = `<p class="text-muted text-xs">${data.message || 'Нет свободных окон на эту дату.'}</p>`;
            }

            // Обработчики для кнопок слотов
            document.querySelectorAll('.slot-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                    this.classList.add('selected');
                    selectedSlot = this.dataset.fullslot;
                    selectedMasterId = parseInt(this.dataset.master);
                    selectedServiceId = parseInt(this.dataset.service);

                    const bookPanel = document.getElementById('bookPanel');
                    bookPanel.classList.remove('hidden');
                    document.getElementById('panelMaster').textContent = `${this.dataset.name} · ${this.dataset.price} ₽`;
                    document.getElementById('panelTime').textContent = this.dataset.fullslot.replace('T', ' ');
                });
            });

        } catch (err) {
            slotGrid.innerHTML = '<p class="text-red-500 text-xs">Ошибка загрузки. Попробуйте позже.</p>';
        }
    }

    // ===== ПОДТВЕРЖДЕНИЕ ЗАПИСИ =====
    window.confirmBooking = function() {
        if (!selectedSlot || !selectedMasterId || !selectedServiceId) {
            alert('Выберите услугу и время!');
            return;
        }
        window.location.href = `/book?master_id=${selectedMasterId}&service_id=${selectedServiceId}&time=${encodeURIComponent(selectedSlot)}`;
    };
});
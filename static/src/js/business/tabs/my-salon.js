// static/src/js/pages/my-salon.js

(function() {
    // ===== Логика карточки салона =====
    const card = document.getElementById('salonEditCard');
    if (!card) return;

    const toggleContainer = document.getElementById('salonEditToggleContainer');
    const staticBlock = card.querySelector('.salon-edit-static');
    const inputsBlock = card.querySelector('.salon-edit-inputs');

    const displayName = document.getElementById('salonEditNameDisplay');
    const displayAddress = document.getElementById('salonEditAddressDisplay');
    const displayPhone = document.getElementById('salonEditPhoneDisplay');
    const displayDesc = document.getElementById('salonEditDescDisplay');

    const inputName = document.getElementById('salonEditNameInput');
    const inputAddress = document.getElementById('salonEditAddressInput');
    const inputPhone = document.getElementById('salonEditPhoneInput');
    const inputDesc = document.getElementById('salonEditDescInput');

    const photoContainer = document.getElementById('salonEditPhotoContainer');
    const photoUploadLabel = document.getElementById('salonEditPhotoUpload');
    const photoInput = document.getElementById('salonEditPhotoInput');

    let isEditing = false;
    let isPreview = false;
    let originalValues = {};

    // Иконки из глобальных переменных (SVG)
    const ICON_EDIT = window.ICON_EDIT || '';
    const ICON_EYE = window.ICON_EYE || '';
    const ICON_SAVE = window.ICON_SAVE || '';
    const ICON_X = window.ICON_X || '';

    // Сохраняем оригинальные значения при входе в режим
    function saveOriginalValues() {
        originalValues = {
            name: displayName.textContent.trim(),
            address: displayAddress.textContent.trim(),
            phone: displayPhone.textContent.trim(),
            desc: displayDesc.textContent.trim()
        };
    }

    // Восстанавливаем оригинальные значения в статике и инпутах
    function restoreOriginalValues() {
        displayName.textContent = originalValues.name || 'Название салона';
        displayAddress.textContent = originalValues.address || 'Адрес не указан';
        displayPhone.textContent = originalValues.phone || '';
        displayDesc.textContent = originalValues.desc || '';
        inputName.value = originalValues.name;
        inputAddress.value = originalValues.address;
        inputPhone.value = originalValues.phone;
        inputDesc.value = originalValues.desc;
    }

    // Обновить статику из инпутов (без сохранения)
    function applyInputsToStatic() {
        displayName.textContent = inputName.value || 'Название салона';
        displayAddress.textContent = inputAddress.value || 'Адрес не указан';
        displayPhone.textContent = inputPhone.value || '';
        displayDesc.textContent = inputDesc.value || '';
    }

    // Установить кнопки в контейнере
    function setButtons(html) {
        toggleContainer.innerHTML = html;
        // Перепривязываем обработчики для новых кнопок (если они есть)
        const previewBtn = document.getElementById('salonEditPreviewBtn');
        const saveBtn = document.getElementById('salonEditSaveBtn');
        const cancelBtn = document.getElementById('salonEditCancelBtn');
        const backBtn = document.getElementById('salonEditBackBtn');

        if (previewBtn) previewBtn.addEventListener('click', togglePreview);
        if (saveBtn) saveBtn.addEventListener('click', saveChanges);
        if (cancelBtn) cancelBtn.addEventListener('click', exitEditMode);
        if (backBtn) {
            backBtn.addEventListener('click', function() {
                // Вернуться к редактированию (из предпросмотра)
                isPreview = false;
                staticBlock.style.display = 'none';
                inputsBlock.style.display = 'block';
                setButtons(`
                    <button class="btn-outline salon-edit-preview-btn" id="salonEditPreviewBtn">${ICON_EYE} Просмотр результата</button>
                    <button class="btn-primary salon-edit-save-btn" id="salonEditSaveBtn">${ICON_SAVE} Сохранить</button>
                    <button class="btn-outline salon-edit-cancel-btn" id="salonEditCancelBtn">${ICON_X} Отменить</button>
                `);
            });
        }
    }

    // Вход в режим редактирования
    function enterEditMode() {
        isEditing = true;
        isPreview = false;
        saveOriginalValues();
        inputName.value = displayName.textContent.trim();
        inputAddress.value = displayAddress.textContent.trim();
        inputPhone.value = displayPhone.textContent.trim();
        inputDesc.value = displayDesc.textContent.trim();
        staticBlock.style.display = 'none';
        inputsBlock.style.display = 'block';
        setButtons(`
            <button class="btn-outline salon-edit-preview-btn" id="salonEditPreviewBtn">${ICON_EYE} Просмотр результата</button>
            <button class="btn-primary salon-edit-save-btn" id="salonEditSaveBtn">${ICON_SAVE} Сохранить</button>
            <button class="btn-outline salon-edit-cancel-btn" id="salonEditCancelBtn">${ICON_X} Отменить</button>
        `);
    }

    // Выход из режима редактирования (отмена)
    function exitEditMode() {
        isEditing = false;
        isPreview = false;
        staticBlock.style.display = 'flex';
        inputsBlock.style.display = 'none';
        restoreOriginalValues();
        setButtons(`
            <button class="btn-outline salon-edit-toggle-btn" id="salonEditToggleBtn">${ICON_EDIT} Редактировать</button>
        `);
        document.getElementById('salonEditToggleBtn').addEventListener('click', function() {
            if (isEditing) {
                exitEditMode();
            } else {
                enterEditMode();
            }
        });
    }

    // Переключение предпросмотра
    function togglePreview() {
        if (!isEditing) return;
        isPreview = !isPreview;
        if (isPreview) {
            // Применяем значения из инпутов в статику
            applyInputsToStatic();
            staticBlock.style.display = 'flex';
            inputsBlock.style.display = 'none';
            setButtons(`
                <button class="btn-outline salon-edit-back-btn" id="salonEditBackBtn">${ICON_EDIT} Редактировать</button>
                <button class="btn-primary salon-edit-save-btn" id="salonEditSaveBtn">${ICON_SAVE} Сохранить</button>
                <button class="btn-outline salon-edit-cancel-btn" id="salonEditCancelBtn">${ICON_X} Отменить</button>
            `);
        } else {
            // Возврат к редактированию (из предпросмотра)
            staticBlock.style.display = 'none';
            inputsBlock.style.display = 'block';
            setButtons(`
                <button class="btn-outline salon-edit-preview-btn" id="salonEditPreviewBtn">${ICON_EYE} Просмотр результата</button>
                <button class="btn-primary salon-edit-save-btn" id="salonEditSaveBtn">${ICON_SAVE} Сохранить</button>
                <button class="btn-outline salon-edit-cancel-btn" id="salonEditCancelBtn">${ICON_X} Отменить</button>
            `);
        }
    }

    // Сохранение (без перезагрузки страницы)
    async function saveChanges() {
        if (!isEditing) return;
        const data = {
            name: inputName.value,
            phone: inputPhone.value,
            address: inputAddress.value,
            description: inputDesc.value
        };
        const salonId = window.salonId;
        try {
            const res = await fetch('/api/v1/business/my-salon?salon_id=' + salonId, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                // Обновляем статику новыми значениями
                applyInputsToStatic();
                // Обновляем originalValues, чтобы они совпадали с новыми
                originalValues = {
                    name: data.name,
                    address: data.address,
                    phone: data.phone,
                    desc: data.description
                };
                // Закрываем режим редактирования
                isEditing = false;
                isPreview = false;
                staticBlock.style.display = 'flex';
                inputsBlock.style.display = 'none';
                setButtons(`
                    <button class="btn-outline salon-edit-toggle-btn" id="salonEditToggleBtn">${ICON_EDIT} Редактировать</button>
                `);
                document.getElementById('salonEditToggleBtn').addEventListener('click', function() {
                    if (isEditing) {
                        exitEditMode();
                    } else {
                        enterEditMode();
                    }
                });
                // Показываем краткое сообщение об успехе
                const msg = document.createElement('div');
                msg.className = 'alert success';
                msg.textContent = 'Изменения сохранены';
                msg.style.marginTop = '1rem';
                card.parentNode.insertBefore(msg, card.nextSibling);
                setTimeout(() => { msg.remove(); }, 3000);
            } else {
                const d = await res.json();
                alert(d.detail || 'Ошибка при сохранении');
            }
        } catch (err) {
            alert('Ошибка сети');
        }
    }

    // Загрузка фото (логотип) – перезагружать страницу не будем, обновим фото в DOM
    async function uploadLogo(file) {
        const salonId = window.salonId;
        const formData = new FormData();
        formData.append('file', file);
        try {
            const res = await fetch('/api/v1/upload/salon/' + salonId + '/photo', {
                method: 'POST',
                body: formData
            });
            if (!res.ok) {
                const d = await res.json();
                alert(d.detail || 'Ошибка загрузки фото');
                return;
            }
            const data = await res.json();
            const url = data.saved && data.saved.length ? data.saved[0] : null;
            if (!url) {
                alert('Не удалось получить URL загруженного фото');
                return;
            }
            // Обновляем логотип через PUT
            const updateRes = await fetch('/api/v1/business/my-salon?salon_id=' + salonId, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ logo_url: url })
            });
            if (updateRes.ok) {
                // Обновляем фото в карточке
                const img = document.querySelector('.salon-edit-photo-wrapper img');
                const placeholder = document.querySelector('.salon-edit-photo-placeholder');
                if (img) {
                    img.src = url + '?t=' + Date.now();
                } else if (placeholder) {
                    // Заменяем плейсхолдер на img
                    const wrapper = placeholder.parentNode;
                    const newImg = document.createElement('img');
                    newImg.src = url + '?t=' + Date.now();
                    newImg.alt = 'Фото салона';
                    newImg.className = 'salon-edit-photo';
                    wrapper.replaceChild(newImg, placeholder);
                }
                // Также обновляем логотип в статике (если нужно, но мы уже обновили)
                // Показываем сообщение
                const msg = document.createElement('div');
                msg.className = 'alert success';
                msg.textContent = 'Фото обновлено';
                msg.style.marginTop = '1rem';
                card.parentNode.insertBefore(msg, card.nextSibling);
                setTimeout(() => { msg.remove(); }, 3000);
            } else {
                const d = await updateRes.json();
                alert(d.detail || 'Не удалось обновить фото');
            }
        } catch (err) {
            alert('Ошибка сети при загрузке фото');
        }
    }

    // Обработчики событий
    // При начальной загрузке – только кнопка "Редактировать"
    const initialToggle = document.getElementById('salonEditToggleBtn');
    if (initialToggle) {
        initialToggle.addEventListener('click', function() {
            if (isEditing) {
                exitEditMode();
            } else {
                enterEditMode();
            }
        });
    }

    if (photoUploadLabel && photoInput) {
        photoUploadLabel.addEventListener('click', (e) => {
            e.stopPropagation();
            photoInput.click();
        });
        photoInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                uploadLogo(e.target.files[0]);
                e.target.value = '';
            }
        });
    }

    // ===== Существующие функции (акции, часы, лояльность, фото) =====
    // Акции
    window.deletePromo = function(id, title) {
        if (confirm('Удалить акцию "' + title + '"? Это действие нельзя отменить.')) {
            fetch('/api/v1/business/my-salon/promotions/' + id + '/delete', { method: 'POST' })
                .then(r => { if (r.ok) location.reload(); else alert('Ошибка при удалении'); });
        }
    };

    // Часы работы
    const WH_DAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

    window.toggleDayClosed = function(day, isClosed) {
        document.getElementById('wh-start-' + day).disabled = isClosed;
        document.getElementById('wh-end-' + day).disabled = isClosed;
    };

    window.copyMondayToWeekdays = function() {
        const start = document.getElementById('wh-start-mon').value;
        const end = document.getElementById('wh-end-mon').value;
        const mondayClosed = document.querySelector('.wh-closed[data-day="mon"]').checked;
        ['tue', 'wed', 'thu', 'fri'].forEach(day => {
            document.querySelector(`.wh-closed[data-day="${day}"]`).checked = mondayClosed;
            document.getElementById('wh-start-' + day).value = start;
            document.getElementById('wh-end-' + day).value = end;
            toggleDayClosed(day, mondayClosed);
        });
    };

    window.saveWorkingHours = async function(salonId) {
        const hours = {};
        for (const day of WH_DAY_KEYS) {
            const closed = document.querySelector(`.wh-closed[data-day="${day}"]`).checked;
            if (closed) {
                hours[day] = 'closed';
            } else {
                const start = document.getElementById('wh-start-' + day).value;
                const end = document.getElementById('wh-end-' + day).value;
                if (!start || !end) { alert('Укажите время начала и конца для рабочего дня'); return; }
                hours[day] = start + '-' + end;
            }
        }
        try {
            const res = await fetch(`/api/v1/business/my-salon?salon_id=${salonId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ working_hours: JSON.stringify(hours) })
            });
            if (res.ok) { alert('Часы работы сохранены'); location.reload(); }
            else { const d = await res.json(); alert(d.detail || 'Ошибка'); }
        } catch (e) { alert('Ошибка сети'); }
    };

    // Лояльность
    window.saveLoyaltySettings = async function(salonId) {
        const body = {
            regular_client_discount_percent: parseInt(document.getElementById('loyaltyRegularPercent').value) || 0,
            regular_client_visits_threshold: document.getElementById('loyaltyVisitsThreshold').value
                ? parseInt(document.getElementById('loyaltyVisitsThreshold').value) : null,
            bonus_accrual_percent: parseFloat(document.getElementById('loyaltyBonusAccrual').value) || 0,
        };
        try {
            const res = await fetch(`/api/v1/loyalty/salon/${salonId}/settings`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (res.ok) { alert('Настройки лояльности сохранены'); }
            else { const d = await res.json(); alert(d.detail || 'Ошибка'); }
        } catch (e) { alert('Ошибка сети'); }
    };

    window.addLoyaltyOffer = async function(salonId) {
        const title = document.getElementById('loyaltyOfferTitle').value.trim();
        const discount_percent = parseInt(document.getElementById('loyaltyOfferPercent').value);
        const promo_code = document.getElementById('loyaltyOfferCode').value.trim() || null;
        if (!title || !discount_percent) { alert('Заполните название и размер скидки'); return; }
        try {
            const res = await fetch(`/api/v1/loyalty/salon/${salonId}/offers`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, discount_percent, promo_code })
            });
            if (res.ok) { location.reload(); }
            else { const d = await res.json(); alert(d.detail || 'Ошибка'); }
        } catch (e) { alert('Ошибка сети'); }
    };

    window.deleteLoyaltyOffer = function(id, title) {
        if (!confirm(`Удалить скидку «${title}»?`)) return;
        const salonId = window.salonId;
        fetch(`/api/v1/loyalty/salon/${salonId}/offers/${id}`, { method: 'DELETE' })
            .then(r => { if (r.ok) location.reload(); else r.json().then(d => alert(d.detail || 'Ошибка')); });
    };

    // Фото: drag & drop (для галереи)
    const dropZone = document.getElementById('photoDropZone');
    const fileInput = document.getElementById('photoFileInput');
    const statusDiv = document.getElementById('photoUploadStatus');

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--color-primary)';
            dropZone.style.background = 'var(--color-surface-alt)';
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = '';
            dropZone.style.background = '';
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '';
            dropZone.style.background = '';
            if (e.dataTransfer.files.length) {
                uploadPhotos(e.dataTransfer.files);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                uploadPhotos(fileInput.files);
                fileInput.value = '';
            }
        });
    }

    async function uploadPhotos(files) {
        const url = dropZone.dataset.uploadUrl;
        statusDiv.innerHTML = '<p style="color:var(--color-muted)">Загрузка...</p>';
        const formData = new FormData();
        for (const file of files) {
            formData.append('files', file);
        }
        try {
            const res = await fetch(url, { method: 'POST', body: formData });
            if (res.ok) {
                statusDiv.innerHTML = '<p style="color:#22c55e">Фото загружены</p>';
                location.reload();
            } else {
                const d = await res.json();
                statusDiv.innerHTML = `<p style="color:#ef4444">Ошибка: ${d.detail || 'Неизвестная ошибка'}</p>`;
            }
        } catch (e) {
            statusDiv.innerHTML = '<p style="color:#ef4444">Ошибка сети</p>';
        }
    }

    // Модалки
    document.querySelectorAll('.my-salon-modal-close').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.my-salon-modal-overlay').classList.remove('active');
        });
    });

    document.querySelectorAll('.my-salon-modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.my-salon-modal-overlay.active').forEach(el => el.classList.remove('active'));
        }
    });

})();
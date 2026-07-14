// tg-verify.js — подтверждение телефона через Telegram-бота (блок 18).
// Подключается только при включённом TG-канале (см. app/web/pages/register.py).
// Флоу: кнопка → POST tg-start → открываем deep link бота → поллим tg-status
// до confirmed → зелёная галка, request_id уже в hidden-поле формы.
(function () {
  var btn = document.getElementById('tgVerifyBtn');
  if (!btn) return;

  var hint = document.getElementById('tgHint');
  var requestIdInput = document.getElementById('request_id');
  var pollTimer = null;
  var deadline = 0;

  function setHint(text) {
    if (hint) hint.textContent = text;
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  function markConfirmed() {
    stopPolling();
    btn.textContent = 'Номер подтверждён ✓';
    btn.disabled = true;
    btn.classList.add('tg-confirmed');
    setHint('Готово! Заполните остальные поля и завершите регистрацию.');
  }

  async function poll() {
    if (Date.now() > deadline) {
      stopPolling();
      btn.disabled = false;
      btn.textContent = 'Подтвердить номер в Telegram';
      setHint('Время подтверждения вышло — нажмите кнопку ещё раз.');
      return;
    }
    try {
      var res = await fetch(
        '/api/v1/auth/register/tg-status?request_id=' +
          encodeURIComponent(requestIdInput.value)
      );
      if (!res.ok) return; // транзиентная ошибка/лимит — попробуем следующим тиком
      var data = await res.json();
      if (data.status === 'confirmed') markConfirmed();
      if (data.status === 'not_found') {
        // истекло или уже использовано — предлагаем начать заново
        stopPolling();
        btn.disabled = false;
        btn.textContent = 'Подтвердить номер в Telegram';
        setHint('Подтверждение устарело — нажмите кнопку ещё раз.');
      }
    } catch (e) {
      /* сеть моргнула — молча ждём следующий тик */
    }
  }

  btn.addEventListener('click', async function () {
    var phone = document.getElementById('phone').value;
    if (!phone) {
      alert('Сначала введите номер телефона');
      return;
    }
    btn.disabled = true;
    btn.textContent = 'Открываем Telegram...';
    try {
      var res = await fetch('/api/v1/auth/register/tg-start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: phone })
      });
      var data = await res.json();
      if (!res.ok) {
        alert(data.detail || 'Не удалось начать подтверждение');
        btn.disabled = false;
        btn.textContent = 'Подтвердить номер в Telegram';
        return;
      }
      requestIdInput.value = data.request_id;
      deadline = Date.now() + (data.expires_in_seconds || 600) * 1000;
      // Открываем бота в новой вкладке/приложении; на телефоне подхватит
      // приложение Telegram, на десктопе — веб/десктоп-клиент.
      window.open(data.deep_link, '_blank');
      btn.textContent = 'Ждём подтверждения в Telegram…';
      setHint('В боте нажмите «Поделиться контактом». Эта страница поймёт всё сама.');
      stopPolling();
      pollTimer = setInterval(poll, 2500);
    } catch (e) {
      alert('Сеть недоступна, попробуйте ещё раз');
      btn.disabled = false;
      btn.textContent = 'Подтвердить номер в Telegram';
    }
  });
})();

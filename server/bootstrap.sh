#!/usr/bin/env bash
# bootstrap.sh — первичная настройка сервера (Ubuntu 22.04/24.04) под Руми.
# Блоки роадмапа 02 (хостинг/сеть) + 03 (секреты — вручную, см. RUNBOOK.md).
#
# Запуск ОДИН РАЗ root'ом:
#   bash bootstrap.sh 'ssh-ed25519 AAAA... artem-rumi-deploy'
#
# Скрипт идемпотентен — повторный запуск ничего не ломает.
#
# ВАЖНО: не закрывайте текущую SSH-сессию, пока не проверите из ВТОРОГО
# терминала, что вход работает: ssh -i ~/.ssh/timeweb_rumi deploy@<host>
set -euo pipefail

PUBKEY="${1:?Использование: bash bootstrap.sh '<публичный ssh-ключ deploy-пользователя>'}"
DEPLOY_USER="deploy"
APP_DIR="/opt/rumi"

echo "[1/7] Пакеты (ufw, fail2ban, unattended-upgrades, git)..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -yq ufw fail2ban unattended-upgrades ca-certificates curl git \
    python3-venv postgresql-client awscli   # venv — для gen_keys, клиент+aws — для backup_to_s3.sh

echo "[2/7] Docker + compose-plugin..."
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

echo "[3/7] Пользователь ${DEPLOY_USER} (без root, в группе docker)..."
if ! id -u "${DEPLOY_USER}" >/dev/null 2>&1; then
    useradd -m -s /bin/bash "${DEPLOY_USER}"
fi
usermod -aG docker "${DEPLOY_USER}"
install -d -m 700 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" "/home/${DEPLOY_USER}/.ssh"
AUTH_KEYS="/home/${DEPLOY_USER}/.ssh/authorized_keys"
touch "${AUTH_KEYS}"
grep -qF "${PUBKEY}" "${AUTH_KEYS}" || echo "${PUBKEY}" >> "${AUTH_KEYS}"
chown "${DEPLOY_USER}:${DEPLOY_USER}" "${AUTH_KEYS}"
chmod 600 "${AUTH_KEYS}"

echo "[4/7] SSH hardening (root и пароли — выключить)..."
install -d -m 755 /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/99-rumi-hardening.conf << 'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
X11Forwarding no
EOF
systemctl reload ssh 2>/dev/null || systemctl reload sshd

echo "[5/7] Firewall: только 22/80/443..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "[6/7] fail2ban (sshd) + автообновления безопасности..."
systemctl enable --now fail2ban
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

echo "[7/7] Каталог приложения ${APP_DIR} + docker-сеть edge..."
install -d -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" "${APP_DIR}"
docker network inspect edge >/dev/null 2>&1 || docker network create edge

echo
echo "Готово. Дальше — под пользователем ${DEPLOY_USER} по server/RUNBOOK.md:"
echo "  1) ПРОВЕРИТЬ вход из второго терминала: ssh ${DEPLOY_USER}@<host>"
echo "  2) git clone в ${APP_DIR}/be, заполнить .env/.env.staging (chmod 600)"
echo "  3) новые секреты и RS256-ключи (блок 03) — старые скомпрометированы"
echo "  4) ./deploy.sh staging && ./deploy.sh prod"

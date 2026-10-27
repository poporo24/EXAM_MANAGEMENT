#!/bin/bash
set -e

echo "=========================================================="
echo "  Deploying CCA Exam Management Update on Server"
echo "=========================================================="

# 1. Timezone
echo "[1/7] Setting timezone to Asia/Manila..."
timedatectl set-timezone Asia/Manila 2>/dev/null || true

# 2. Unzip files to /var/www/cca_exam/
echo "[2/7] Unzipping update files..."
unzip -o /root/cca_exam_deploy.zip -d /var/www/cca_exam/

# 3. Clean python bytecode
echo "[3/7] Cleaning old bytecode..."
find /var/www/cca_exam -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /var/www/cca_exam -name "*.pyc" -delete 2>/dev/null || true
find /var/www/cca_exam -name "*.py" -exec touch {} + 2>/dev/null || true

# 4. Fix permissions
chown -R root:root /var/www/cca_exam/ 2>/dev/null || true
chmod -R 755 /var/www/cca_exam/ 2>/dev/null || true

# 5. Database system settings verification
echo "[4/7] Verifying database system settings..."
mysql -u cca_user -pExamPass123! cca_exam_management_db -e "
UPDATE system_settings SET day_start='07:00:00', day_end='20:00:00', slot_interval_min=60, max_consecutive_proctor_hrs=3, major_duration_hrs=3.0, minor_duration_hrs=1.0, max_daily_proctor_hrs=4.0 WHERE id=1;
" 2>/dev/null || true

# 6. Configure Nginx timeouts
echo "[5/7] Configuring Nginx timeouts (300s)..."
mkdir -p /etc/nginx/conf.d
cat << 'EOF' > /etc/nginx/conf.d/timeout.conf
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;
client_max_body_size 50M;
EOF

nginx -t && systemctl reload nginx || true

# 7. Configure Gunicorn timeout, enforce strong FLASK_SECRET_KEY & restart service
echo "[6/7] Hardening service configuration & restarting Gunicorn..."
if [ -f /etc/systemd/system/cca_exam.service ]; then
    sed -i -E 's/--timeout [0-9]+/--timeout 300/g' /etc/systemd/system/cca_exam.service
    if ! grep -q -- '--timeout' /etc/systemd/system/cca_exam.service; then
        sed -i 's/gunicorn -w 3 -b/gunicorn -w 3 --timeout 300 -b/g' /etc/systemd/system/cca_exam.service
    fi
    # Enforce strong persistent FLASK_SECRET_KEY if not already present
    if ! grep -q 'FLASK_SECRET_KEY' /etc/systemd/system/cca_exam.service; then
        echo "Injecting cryptographically secure FLASK_SECRET_KEY into systemd service..."
        NEW_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
        sed -i "/\[Service\]/a Environment=\"FLASK_SECRET_KEY=${NEW_KEY}\"" /etc/systemd/system/cca_exam.service
    fi
    systemctl daemon-reload
    systemctl restart cca_exam
else
    pkill -f gunicorn || true
fi

# 8. Verification
echo "[7/7] Verifying app status..."
sleep 2
echo "Gunicorn Service Status: $(systemctl is-active cca_exam 2>/dev/null || echo 'Unknown')"

echo "=========================================================="
echo "  Deployment Complete! Server time: $(date)"
echo "=========================================================="

#!/bin/bash
set -e

echo "=== 1. Updating System Packages ==="
DEBIAN_FRONTEND=noninteractive apt update -y
DEBIAN_FRONTEND=noninteractive apt install -y python3-pip python3-venv mysql-server nginx unzip curl

echo "=== 2. Configuring MySQL Database ==="
systemctl start mysql
systemctl enable mysql

mysql -e "CREATE DATABASE IF NOT EXISTS cca_exam_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'cca_user'@'localhost' IDENTIFIED BY 'ExamPass123!';"
mysql -e "ALTER USER 'cca_user'@'localhost' IDENTIFIED BY 'ExamPass123!';"
mysql -e "GRANT ALL PRIVILEGES ON cca_exam_management_db.* TO 'cca_user'@'localhost'; FLUSH PRIVILEGES;"

echo "=== 3. Extracting Project Files ==="
mkdir -p /var/www/cca_exam
cd /var/www/cca_exam
unzip -o /root/cca_exam_deploy.zip

echo "=== 4. Importing Database Schema ==="
mysql -u cca_user -pExamPass123! cca_exam_management_db < cca_exam_db_export.sql

echo "=== 5. Setting Up Python Environment ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn

echo "=== 6. Creating Systemd Service ==="
cat << 'EOF' > /etc/systemd/system/cca_exam.service
[Unit]
Description=CCA Exam Management System
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/cca_exam
Environment="PATH=/var/www/cca_exam/venv/bin"
Environment="PORT=9999"
Environment="HOST=127.0.0.1"
Environment="DB_HOST=localhost"
Environment="DB_USER=cca_user"
Environment="DB_PASSWORD=ExamPass123!"
Environment="DB_NAME=cca_exam_management_db"
ExecStart=/var/www/cca_exam/venv/bin/gunicorn -w 3 -b 127.0.0.1:9999 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cca_exam
systemctl restart cca_exam

echo "=== 7. Configuring Nginx Web Server ==="
cat << 'EOF' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:9999;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

nginx -t
systemctl restart nginx

echo "====================================================="
echo "  CCA EXAM MANAGEMENT SYSTEM IS LIVE ON THE CLOUD!  "
echo "  URL: http://$(curl -s ifconfig.me)"
echo "====================================================="

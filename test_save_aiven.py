import mysql.connector

try:
    db = mysql.connector.connect(
        host='mysql-5807518-johnpaulbaltazar2401-f645.i.aivencloud.com',
        user='avnadmin',
        password='AVNS_0uijwdmnhsiqSaQyce-',
        database='defaultdb',
        port=15268
    )
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO system_settings (id, day_start, day_end, slot_interval_min, max_consecutive_proctor_hrs, travel_buffer_min, smtp_host, smtp_port, smtp_user, smtp_password, smtp_from, smtp_use_tls, major_duration_hrs, minor_duration_hrs)
        VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        day_start=VALUES(day_start), day_end=VALUES(day_end), slot_interval_min=VALUES(slot_interval_min), max_consecutive_proctor_hrs=VALUES(max_consecutive_proctor_hrs), travel_buffer_min=VALUES(travel_buffer_min), smtp_host=VALUES(smtp_host), smtp_port=VALUES(smtp_port), smtp_user=VALUES(smtp_user), smtp_password=VALUES(smtp_password), smtp_from=VALUES(smtp_from), smtp_use_tls=VALUES(smtp_use_tls), major_duration_hrs=VALUES(major_duration_hrs), minor_duration_hrs=VALUES(minor_duration_hrs)
    ''', ("07:00", "20:00", 60, 3, 15, "smtp.gmail.com", 587, "test@example.com", "password", "test@example.com", 1, 2.0, 1.0))
    db.commit()
    print("SUCCESS on Aiven DB")
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    if 'db' in locals():
        db.close()

from system.database import save_system_settings
try:
    save_system_settings(
        day_start="07:00",
        day_end="20:00",
        slot_interval_min=60,
        max_proctor_hrs=3,
        travel_buffer_min=15,
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        smtp_user="test@example.com",
        smtp_password="password",
        smtp_from="test@example.com",
        smtp_use_tls=1,
        major_duration_hrs=2.0,
        minor_duration_hrs=1.0
    )
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()

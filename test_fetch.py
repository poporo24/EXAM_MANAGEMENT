import sys
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from app import app

app.config['TESTING'] = True
client = app.test_client()

with client.session_transaction() as sess:
    sess['user_id'] = 13
    sess['role'] = 'admin'

r = client.post('/api/available_resources', json={'exam_id': 0, 'exam_datetime': '2026-10-05T08:00', 'duration_minutes': 60})
print(r.status_code)
print(r.json)

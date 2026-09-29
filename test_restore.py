import sys
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from app import app
from system.database import open_db

app.config['TESTING'] = True
client = app.test_client()

with client.session_transaction() as sess:
    sess['user_id'] = 13
    sess['role'] = 'admin'

# Generate schedule to recreate conflicts
r = client.post('/generate_schedule', data={'period_start': '2026-10-01', 'period_end': '2026-10-07'}, follow_redirects=True)
html = r.data.decode('utf-8')
import re
m = re.search(r'name=\"conflict_ids\" value=\"([^\"]*)\"', html)
if m:
    c_ids = m.group(1)
    print('Generated conflicts:', c_ids)
    
    # Try resolving via the endpoint
    r2 = client.post('/resolve_conflicts', data={'conflict_ids': c_ids}, follow_redirects=True)
    html2 = r2.data.decode('utf-8')
    m2 = re.search(r'name=\"conflict_ids\" value=\"([^\"]*)\"', html2)
    print('Remaining conflicts:', m2.group(1) if m2 else 'None')
    print('Auto-resolve success message:', 'successfully auto-resolved' in html2)
    print('Warning message:', 'could still not be scheduled' in html2)
else:
    print('No conflicts generated')

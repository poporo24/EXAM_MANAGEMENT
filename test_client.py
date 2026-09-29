import sys
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from app import app
from system.database import open_db

app.config['TESTING'] = True
client = app.test_client()

with client.session_transaction() as sess:
    sess['user_id'] = 13
    sess['role'] = 'admin'

r = client.get('/schedule')
html = r.data.decode('utf-8')
import re
m = re.search(r'name=\"conflict_ids\" value=\"([^\"]*)\"', html)
if m:
    c_ids = m.group(1)
    print('Found conflict_ids:', c_ids)
    if c_ids:
        r2 = client.post('/resolve_conflicts', data={'conflict_ids': c_ids}, follow_redirects=True)
        html2 = r2.data.decode('utf-8')
        m2 = re.search(r'name=\"conflict_ids\" value=\"([^\"]*)\"', html2)
        print('Remaining conflict_ids:', m2.group(1) if m2 else 'None')
        print('Success message:', 'successfully auto-resolved' in html2)
        print('Warning message:', 'could still not be scheduled' in html2)
        # print un-scheduled count
        import bs4
        soup = bs4.BeautifulSoup(html2, 'html.parser')
        unsched = soup.select('div.bg-red-50 tbody tr')
        print('Unscheduled count:', len(unsched))
    else:
        print('Empty conflict_ids string')
else:
    print('No conflict_ids input found in HTML')

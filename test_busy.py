import sys
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from system.database import open_db, get_available_resources
res = get_available_resources(0, '2026-10-05T08:00', 60)
print('Rooms count:', len(res['rooms']))
print('Instructors count:', len(res['instructors']))

import urllib.request, urllib.parse, http.cookiejar, re

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login
data = urllib.parse.urlencode({'email': 'superadmin@cca.edu.ph', 'password': 'admin'}).encode('utf-8')
try:
    r = opener.open('http://127.0.0.1:9999/login', data=data)
    
    r2 = opener.open('http://127.0.0.1:9999/schedule')
    html = r2.read().decode('utf-8')
    m = re.search(r'name=\"conflict_ids\" value=\"([^\"]*)\"', html)
    if m:
        c_ids = m.group(1)
        print('Found conflict_ids:', c_ids)
        if c_ids:
            post_data = urllib.parse.urlencode({'conflict_ids': c_ids}).encode('utf-8')
            r3 = opener.open('http://127.0.0.1:9999/resolve_conflicts', data=post_data)
            html3 = r3.read().decode('utf-8')
            print('Flash message in response:', '? All conflicts have been successfully auto-resolved!' in html3)
            print('Warning message:', 'could still not be scheduled' in html3)
            m2 = re.search(r'name=\"conflict_ids\" value=\"([^\"]*)\"', html3)
            print('Remaining conflict_ids:', m2.group(1) if m2 else 'None')
        else:
            print('Empty conflict_ids string')
    else:
        print('No conflict_ids input found in HTML')
except Exception as e:
    print(e)

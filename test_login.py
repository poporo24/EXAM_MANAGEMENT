import urllib.request, urllib.parse, http.cookiejar, re
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
data = urllib.parse.urlencode({'email': 'admin@cca.edu.ph', 'password': 'admin'}).encode('utf-8')
r = opener.open('http://127.0.0.1:9999/login', data=data)
print(r.url)

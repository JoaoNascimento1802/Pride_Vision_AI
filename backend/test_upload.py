import urllib.request
import json

try:
    token_req = urllib.request.Request('http://127.0.0.1:8001/api/auth/login', data=b'username=admin%40pride.com&password=admin')
    token_req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(token_req) as f:
        token = json.loads(f.read().decode())['access_token']
    
    url = 'http://127.0.0.1:8001/api/aplicacoes/1/uploads/semgrep'
    req = urllib.request.Request(url, method='POST')
    req.add_header('Authorization', 'Bearer ' + token)
    req.add_header('X-Tenant-ID', '2')
    req.add_header('Content-Type', 'multipart/form-data; boundary=----pride-demo')
    
    body = (
        '------pride-demo\r\n'
        'Content-Disposition: form-data; name="arquivo"; filename="semgrep.json"\r\n\r\n'
        '{ "results": [] }\r\n'
        '------pride-demo--\r\n'
    )
    with urllib.request.urlopen(req, data=body.encode('utf-8')) as f:
        print(f.read().decode())
except urllib.error.HTTPError as e:
    print('HTTP Error', e.code)
    print(e.read().decode())

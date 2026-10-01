with open('backend/app/routers/cspm.py', 'rb') as f:
    content = f.read()

if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
    with open('backend/app/routers/cspm.py', 'wb') as f:
        f.write(content)


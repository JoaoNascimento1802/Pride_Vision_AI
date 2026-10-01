with open('backend/app/routers/cspm.py', 'rb') as f:
    content = f.read()

content = content.replace(b'\xef\xbb\xbf', b'')

with open('backend/app/routers/cspm.py', 'wb') as f:
    f.write(content)


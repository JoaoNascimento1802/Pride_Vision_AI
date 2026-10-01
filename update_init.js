const fs = require('fs');
let code = fs.readFileSync('backend/app/models/__init__.py', 'utf-8');
code = code.replace('from app.models.container import ContainerImage', 'from app.models.container import ContainerImage, ContainerInstance');
fs.writeFileSync('backend/app/models/__init__.py', code, 'utf-8');

const fs = require('fs');
let sc = fs.readFileSync('backend/app/routers/supply_chain.py', 'utf-8');
const searchListar = `def list_verifications(
    image_name: str,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("application:read"))
):`;
const replaceListar = `def list_verifications(
    image_name: str,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("application:read"))
) -> list[dict[str, str | bool | int | None]]:`;
sc = sc.replace(searchListar, replaceListar);
fs.writeFileSync('backend/app/routers/supply_chain.py', sc, 'utf-8');

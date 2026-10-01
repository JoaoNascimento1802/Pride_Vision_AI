const fs = require('fs');
let code = fs.readFileSync('backend/app/services/dominio.py', 'utf-8');

const target = 'image_digest: str | None = None';
const injection = `image_digest: str | None = None

    # Presentes apenas no Runtime / eBPF (Falco, Tetragon)
    process_name: str | None = None
    pid: int | None = None
    syscall: str | None = None
    container_id: str | None = None
    hit_count: int = 1
    last_seen_at: str | None = None`;

code = code.replace(target, injection);
fs.writeFileSync('backend/app/services/dominio.py', code, 'utf-8');

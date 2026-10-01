const fs = require('fs');
let code = fs.readFileSync('backend/app/schemas/vulnerability.py', 'utf-8');

const target = 'base_image: str | None = None';
const injection = `base_image: str | None = None

    # Runtime / eBPF
    process_name: str | None = None
    pid: int | None = None
    syscall: str | None = None
    container_id: str | None = None
    hit_count: int | None = None
    last_seen_at: datetime | None = None`;

code = code.replace(target, injection);
fs.writeFileSync('backend/app/schemas/vulnerability.py', code, 'utf-8');

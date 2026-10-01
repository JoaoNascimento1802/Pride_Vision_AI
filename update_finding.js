const fs = require('fs');
let code = fs.readFileSync('backend/app/models/ingestion.py', 'utf-8');

const target = 'linha: Mapped[int | None] = mapped_column(Integer, default=None)';
const injection = `linha: Mapped[int | None] = mapped_column(Integer, default=None)

    # --- Somente Runtime (eBPF) ---
    process_name: Mapped[str | None] = mapped_column(String(255), default=None)
    pid: Mapped[int | None] = mapped_column(Integer, default=None)
    syscall: Mapped[str | None] = mapped_column(String(100), default=None)
    container_id: Mapped[str | None] = mapped_column(String(255), index=True, default=None)
    
    hit_count: Mapped[int] = mapped_column(Integer, default=1)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))`;

code = code.replace(target, injection);
fs.writeFileSync('backend/app/models/ingestion.py', code, 'utf-8');

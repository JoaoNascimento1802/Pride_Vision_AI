const fs = require('fs');
let code = fs.readFileSync('backend/app/models/ingestion.py', 'utf-8');

code = code.replace(
    'upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id", ondelete="CASCADE"), index=True)',
    'upload_id: Mapped[int | None] = mapped_column(ForeignKey("uploads.id", ondelete="CASCADE"), index=True, default=None)'
);

fs.writeFileSync('backend/app/models/ingestion.py', code, 'utf-8');

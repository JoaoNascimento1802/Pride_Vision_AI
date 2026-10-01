const fs = require('fs');
let code = fs.readFileSync('backend/app/models/container.py', 'utf-8');

const newCode = `

class ContainerInstance(Base):
    """
    Representa uma inst\u00E2ncia em execu\u00E7\u00E3o (Runtime) de um ContainerImage.
    Relaciona o 'container_id' do Docker/Kubernetes ao digest/imagem escaneada.
    """
    __tablename__ = "container_instances"

    id: Mapped[int] = mapped_column(primary_key=True)
    container_id: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    
    container_image_id: Mapped[int | None] = mapped_column(
        ForeignKey("container_images.id", ondelete="SET NULL"), index=True, default=None
    )

    namespace: Mapped[str | None] = mapped_column(String(100), default=None)
    pod_name: Mapped[str | None] = mapped_column(String(255), default=None)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    container_image: Mapped[ContainerImage | None] = relationship()

    def __repr__(self) -> str:
        return f"<ContainerInstance {self.container_id}>"
`;

code += newCode;
fs.writeFileSync('backend/app/models/container.py', code, 'utf-8');

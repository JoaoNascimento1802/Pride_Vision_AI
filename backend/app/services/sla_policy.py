from app.models.enums import Risco


class SlaPolicy:
    """
    Configuração centralizada das réguas de SLA por nível de risco.
    Define a duração em dias até o vencimento.
    """

    PRAZOS_EM_DIAS = {
        Risco.CRITICO: 5,
        Risco.ALTO: 15,
        Risco.MEDIO: 30,
        Risco.BAIXO: 90,
    }

    @classmethod
    def get_dias_para_risco(cls, risco: Risco) -> int:
        return cls.PRAZOS_EM_DIAS.get(risco, 0)

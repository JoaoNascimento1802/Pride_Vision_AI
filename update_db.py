import re

with open('backend/app/database.py', 'r', encoding='utf-8') as f:
    text = f.read()

injection = """
from contextvars import ContextVar
from sqlalchemy.orm import with_loader_criteria

current_tenant_id: ContextVar[int | None] = ContextVar("current_tenant_id", default=None)

@event.listens_for(Session, "do_orm_execute")
def _add_tenant_filter(execute_state):
    tenant_id = current_tenant_id.get()
    if tenant_id is not None:
        # Avoid infinite recursion when querying Tenant itself
        if execute_state.is_select and not execute_state.is_column_load and not execute_state.is_relationship_load:
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    Base,
                    lambda cls: cls.tenant_id == tenant_id if hasattr(cls, "tenant_id") else True,
                    include_aliases=True,
                )
            )
"""

text = text.replace('class Base(DeclarativeBase):', injection + '\nclass Base(DeclarativeBase):')

with open('backend/app/database.py', 'w', encoding='utf-8') as f:
    f.write(text)

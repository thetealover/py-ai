from typing import Sequence, Union

from alembic import op

revision: str = '70940d93491c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Applies the migration.
    Creates the conversation_metadata table.
    """
    op.execute("""
               create table if not exists conversation_metadata
               (
                   thread_id  text primary key,
                   title      text not null,
                   created_at timestamptz default current_timestamp,
                   updated_at timestamptz default current_timestamp
               );
               """)
    op.execute("""
               create or replace function update_updated_at_column()
                   returns trigger as
               $$
               BEGIN
                   new.updated_at = current_timestamp;
                   return new;
               END;
               $$ language 'plpgsql';
               """)
    op.execute("""
               create trigger update_conversation_metadata_updated_at
                   before update
                   on conversation_metadata
                   for each row
               execute function update_updated_at_column();
               """)


def downgrade() -> None:
    """
    Reverts the migration.
    Drops the conversation_metadata table and related trigger function.
    """
    op.execute("drop table if exists conversation_metadata;")
    op.execute("drop function if exists update_updated_at_column();")

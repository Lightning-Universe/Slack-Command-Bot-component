from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine


class Workspace(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: str = Field(unique=True, nullable=False)
    bot_token: str = Field(unique=True, nullable=False)
    created_at: datetime = datetime.now()


sqlite_file_name = "slack_command_bot.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

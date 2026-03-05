from sqlalchemy import Integer, String, DateTime
from sqlalchemy.sql import func 
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from db.database import Base


class StoryJob(Base):
    __tablename__ = "story_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index= True   )
    job_id: Mapped[str] = mapped_column(String, index = True, unique= True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    theme: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    story_id: Mapped[int | None] = mapped_column(Integer, nullable= True)
    error: Mapped[str | None] = mapped_column(String, nullable= True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default= func.now())
    completed_at : Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable= True)
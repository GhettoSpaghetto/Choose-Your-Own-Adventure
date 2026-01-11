from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.database import Base


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    nodes: Mapped[list["StoryNode"]] = relationship(
        back_populates="story",
        cascade="all, delete-orphan"
    )


class StoryNode(Base):
    __tablename__ = "story_nodes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))

    content: Mapped[str] = mapped_column(String)

    is_root: Mapped[bool] = mapped_column(Boolean, default=False)
    is_ending: Mapped[bool] = mapped_column(Boolean, default=False)
    is_winning_ending: Mapped[bool] = mapped_column(Boolean, default=False)

    options: Mapped[list[dict]] = mapped_column(JSON, default=list)

    story: Mapped["Story"] = relationship(back_populates="nodes")

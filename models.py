from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime

class Base(DeclarativeBase):
       pass

# Database Tables
class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine':'InnoDB'}

    user_id: Mapped[int] = mapped_column(
        unique = True, 
        primary_key=True, 
        nullable=False,
        autoincrement=True
        )
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now())
    profile_picture_media_id: Mapped[str] = mapped_column(String(255), nullable=True, default='')
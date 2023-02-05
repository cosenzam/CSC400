from sqlalchemy import MetaData, Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

# Database Tables
class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine':'InnoDB'}

    user_id = mapped_column(
        Integer, 
        unique = True, 
        primary_key=True, 
        nullable=False,
        autoincrement=True
        )
    user_name = mapped_column(String, nullable=False)
    email = mapped_column(String, nullable=False)
    password = mapped_column(String, nullable=False)
    date_created = mapped_column(DateTime, default=datetime.now())
    profile_picture_media_id = mapped_column(Integer)

def create_tables(engine):
    Base.metadata.create_all(engine)
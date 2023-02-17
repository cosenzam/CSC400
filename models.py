from sqlalchemy import Column, Text, String, ForeignKey, Boolean, DateTime, Null
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from datetime import datetime

class Base(DeclarativeBase):
       pass

# Database Tables
class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id: Mapped[int] = mapped_column(
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

    #relationships
    user_profile: Mapped["UserProfile"] = relationship(back_populates="user")

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id: Mapped[int] = mapped_column(
        unique = True, 
        primary_key=True,
        nullable=False,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    profile_picture_media_id: Mapped[str] = mapped_column(String(255), nullable=True, default='')
    first_name: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    middle_name: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    prefix: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    suffix: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    gender: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    pronouns: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    occupation: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    address: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    city: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    country: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    zip: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    date_of_birth: Mapped[datetime] = mapped_column(nullable=True, default=Null)
    bio: Mapped[str] = mapped_column(Text, nullable=True, default=Null)
    last_updated: Mapped[datetime] = mapped_column(default=datetime.now())

    #relationships
    user: Mapped["User"] = relationship(back_populates="user_profile") 

class Post(Base):

    __tablename__ = 'posts'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id: Mapped[int] = mapped_column(
        unique = True,
        primary_key = True,
        nullable = False,
        autoincrement = True
    )
    text: Mapped[str] = mapped_column(String(256), nullable = False)
    user_name: Mapped[str] = mapped_column(String(255), nullable = False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_posted: Mapped[datetime] = mapped_column(default = datetime.now())
    media: Mapped[str] = mapped_column(String(32), nullable = False)
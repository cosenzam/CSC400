from sqlalchemy import Column, Text, String, ForeignKey, Boolean, DateTime, Null
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime, date

class Base(DeclarativeBase):
    __table_args__ = {'mysql_engine':'InnoDB'}

# Database Tables
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        unique = True, 
        primary_key=True, 
        nullable=False,
        autoincrement=True
    )

    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_picture_media_id: Mapped[str] = mapped_column(String(255), nullable=True, default='')
    first_name: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    middle_name: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    pronouns: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    date_of_birth: Mapped[date] = mapped_column(nullable=True, default=None)
    bio: Mapped[str] = mapped_column(Text, nullable=True, default=Null)
    location: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    occupation: Mapped[str] = mapped_column(String(255), nullable=True, default=Null)
    date_created: Mapped[datetime] = mapped_column(default=datetime.now())
    last_updated: Mapped[datetime] = mapped_column(default=datetime.now())

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(
        unique = True,
        primary_key = True,
        nullable = False,
        autoincrement = True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    parent_id: Mapped[int] = mapped_column(nullable=True, default=None)
    text: Mapped[str] = mapped_column(Text, nullable = True)
    date_posted: Mapped[datetime] = mapped_column(default = datetime.now())

class MediaCollection(Base):
    __tablename__ = 'media_collections'

    id: Mapped[int] = mapped_column(
        unique = True, 
        primary_key=True, 
        nullable=False,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))
    collection_type: Mapped[str] =  mapped_column(String(255), nullable=False, default="gallery")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    photo_count: Mapped[int] = mapped_column(nullable=False, default=0)
    video_count: Mapped[int] = mapped_column(nullable=False, default=0)
    date_created: Mapped[datetime] =  mapped_column(default=datetime.now())

class Media(Base):
    __tablename__ = 'media'

    id: Mapped[int] = mapped_column(
        unique = True,
        primary_key = True,
        nullable = False,
        autoincrement = True
    )

    collection_id: Mapped[str] = mapped_column(ForeignKey("media_collections.id"))
    media_type: Mapped[str] = mapped_column(String(255), default='photo')
    file_path: Mapped[str] = mapped_column(String(255), default='')

class Interaction(Base):
    __tablename__ = 'interactions'

    id: Mapped[int] = mapped_column(
        unique = True,
        primary_key = True,
        nullable = False,
        autoincrement = True
    )

    interaction_type: Mapped[str] = mapped_column(String(255), default="reply")
    collection_id: Mapped[str] = mapped_column(ForeignKey("media_collections.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    parent_id: Mapped[int] = mapped_column(nullable=True, default=Null)
    from_user_id: Mapped[int] = mapped_column(nullable=True, default=Null)
    to_user_id: Mapped[int] = mapped_column(nullable=True, default=Null) 
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now())

class FollowLookup(Base):

    __tablename__ = 'follow_lookup'

    id: Mapped[int] = mapped_column(
        unique = True,
        primary_key = True,
        nullable = False,
        autoincrement = True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    interaction_id: Mapped[int] = mapped_column(ForeignKey("interactions.id"))
    following_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_mutual: Mapped[bool] = mapped_column(default=False)
    date_followed: Mapped[datetime] = mapped_column(default=datetime.now())
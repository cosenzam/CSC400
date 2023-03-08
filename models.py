from sqlalchemy import Column, Text, String, ForeignKey, Boolean, DateTime, Null, select
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, date
from connect import db_connect #connect.py method that handles all connections, returns engine.

global engine
global session

def insert_user(user_name, email, password):
    user = User(
        user_name=user_name, 
        email=email, 
        password=password
    )

    session.add(user)
    session.commit()
    return user

def get_user(id=None, user_name=None, email=None):

    if id is not None:
        stmt = select(User).where(User.id == id)
    elif user_name is not None:
        stmt = select(User).where(User.user_name == user_name)
    elif email is not None:
        stmt = select(User).where(User.email == email)
    else:
        print("input a user id, email or user_name.")
        return None

    print(stmt)

    try:
        user = session.scalars(stmt).one()
        return user
    except NoResultFound:
        print("No User found.")
        return None

def insert_post(user, text):
    post = Post(
        user_id = user.id,
        text = text
    )

    session.add(post)
    session.commit()

    return post

def insert_interaction(to_user, from_user, post=None, interaction_type="reply"):
    
    if interaction_type == "reply":
        post_id = post.id
        parent_id = post.parent_id
    else:
        post_id = None
        parent_id = None

    interaction = Interaction(
        interaction_type = interaction_type,
        post_id = post_id,
        parent_id = parent_id,
        from_user_id = from_user.id,
        to_user_id = to_user.id,
        timestamp = post.timestamp
    )
    
    session.add(interaction)
    session.commit()

    return interaction

class Base(DeclarativeBase):
    __table_args__ = {'mysql_engine':'InnoDB'}
    
class Interaction(Base):
    __tablename__ = 'interactions'

    id: Mapped[int] = mapped_column(
        unique = True,
        primary_key = True,
        nullable = False,
        autoincrement = True
    )

    interaction_type: Mapped[str] = mapped_column(String(255), default="reply")
    # collection_id: Mapped[str] = mapped_column(ForeignKey("media_collections.id"))
    post_id: Mapped[int] = mapped_column(nullable=True, default=Null)
    parent_id: Mapped[int] = mapped_column(nullable=True, default=Null)
    from_user_id: Mapped[int] = mapped_column(nullable=True, default=Null)
    to_user_id: Mapped[int] = mapped_column(nullable=True, default=Null) 
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now())
    
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
    
    posts = relationship("Post", back_populates="user")

    def get_username(self):
        return self.user_name
    
    def update(self, **kwargs):
        fields = self.__table__.c.keys()[1:]
        for key, value in kwargs.items():
            if key in fields:
                print("setting column: " + key + "to value: " + value)
                setattr(self, key, value)
                
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
    timestamp: Mapped[datetime] = mapped_column(default = datetime.now())
    
    user = relationship("User", back_populates="posts")

    def insert_reply(self, user, reply_text):
        parent_id = self.id
        reply = Post(
            user_id = user.id,
            parent_id = parent_id,
            text = reply_text)
        session.add(reply)
        session.commit()

        insert_interaction(self.user, user, reply)
        return reply

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
    interaction_id: Mapped[int] = mapped_column(nullable=True, default=Null)
    collection_type: Mapped[str] =  mapped_column(String(255), nullable=False, default="gallery")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    photo_count: Mapped[int] = mapped_column(nullable=False, default=0)
    video_count: Mapped[int] = mapped_column(nullable=False, default=0)
    date_created: Mapped[datetime] =  mapped_column(default=datetime.now())

    media = relationship("Media", back_populates="media_collection")

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

    media_collection = relationship("MediaCollection", back_populates="media")


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
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now())
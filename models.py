from sqlalchemy import Column, Text, String, ForeignKey, Boolean, DateTime, Null, select, delete
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from typing import Optional, List
from datetime import datetime, date
from connect import db_connect #connect.py method that handles all connections, returns engine.

global engine
global session

#takes in user_name, email, and password strings to create a User object.
def insert_user(user_name, email, password):

    exists = exists_user(user_name=user_name)

    if not exists:
        print(f"Creating new user with user_name: {user_name}.")
        user = User(
            user_name=user_name, 
            email=email, 
            password=password
        )

        session.add(user)
        session.commit()
        return user
    else:
        print(f"User {user_name} already exists.")
        return exists


#gets a User object based on id, user_name, or email
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

    # print(stmt)

    try:
        user = session.scalars(stmt).one()
        return user
    except NoResultFound:
        print("No User found.")
        return None

#uses get_user to check if a user exists
def exists_user(id=None, user_name=None, email=None):
    user = get_user(id, user_name, email)
    if user is not None:
        return user
    else:
        return False
    
def exists_post():
    return False

#inserts a post, requires a User object and string for text
def insert_post(user, text):
    post = Post(
        user_id = user.id,
        text = text,
        media_collection_id = None,
        timestamp = datetime.now()
    )

    session.add(post)
    session.commit()

    return post

#post getter
def get_post(id):

    stmt = select(Post).where(Post.id==id)

    try:
        post = session.scalars(stmt).one()
        return post
    except NoResultFound:
        print("No Post found.")
        return None

def get_latest_post(User, n=0, replies=False):
    posts = User.posts

    if not replies:
        posts = [p for p in posts if p.parent_id is None]

    return posts[n]

def get_latest_posts(User, start=0, end=1, replies=False):
    posts = User.posts

    if not replies:
        posts = [p for p in posts if p.parent_id is None]

    return posts[start:end]

def follow(to_user, from_user):
    insert_interaction(to_user, from_user, interaction_type="follow")

def unfollow(to_user, from_user):
    delete_interaction(to_user, from_user, interaction_type="follow")

def delete_interaction(to_user, from_user, post=None, interaction_type=None):

    interaction_types = [
        "like",
        "follow",
        "share",
        "reply",
        "message"
    ]

    if interaction_type not in interaction_types:
        print("Not a supported interaciton.")
        return None

    if interaction_type in ["reply", "like", "share"]:
            post_id = post.id
            parent_id = post.parent_id
    else:
        post_id = None
        parent_id = None
    
    stmt = delete(Interaction).where(
        Interaction.interaction_type == interaction_type,
        Interaction.post_id == post_id,
        Interaction.parent_id == parent_id,
        Interaction.from_user_id == from_user.id,
        Interaction.to_user_id == to_user.id
    )

    if stmt == 0:
        print("No interactions fonund")
    else:
        session.execute(stmt)
        session.commit()
    
#probably only gonna be used internally, but logs an interaction
def insert_interaction(to_user, from_user, post=None, interaction_type="reply"):

    interaction_types = [
        "like",
        "follow",
        "share",
        "reply",
        "message"
    ]

    if interaction_type not in interaction_types:
        print("Not a supported interaciton.")
        return None

    if interaction_type in ["reply", "like", "share"]:
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
        timestamp = datetime.now()
    )
    
    session.add(interaction)
    session.commit()

    return interaction

def insert_media(user, file_name, post=None, collection=None):
    
    media = Media(file_path = file_name)
    session.add(media)
    session.commit()
    return media

def upload_collection(user, post, file_paths, collection=None):

    for file_path in file_paths:
        media = insert_media(user, file_path, post)
        if collection is None:
            collection = media.add_to_collection(user=user, post=post)
        else:
            media.add_to_collection(user=user, post=post, collection=collection)
    
    return collection

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
    post_id: Mapped[int] = mapped_column(nullable=True, default=None)
    parent_id: Mapped[int] = mapped_column(nullable=True, default=None)
    from_user_id: Mapped[int] = mapped_column(nullable=True, default=None)
    to_user_id: Mapped[int] = mapped_column(nullable=True, default=None) 
    timestamp: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default=datetime.now())

# class Following(Base):

#     __tablename__ = 'following'

#     id: Mapped[int] = mapped_column(
#         unique = True,
#         primary_key = True,
#         nullable = False,
#         autoincrement = True
#     )

#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
#     interaction_id: Mapped[int] = mapped_column(ForeignKey("interactions.id"))
#     following_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     is_mutual: Mapped[bool] = mapped_column(default=False)
#     timestamp: Mapped[datetime] = mapped_column(default=datetime.now())

class Follows(Base):

    __tablename__ = 'follows'

    id: Mapped[int] = mapped_column(
        unique = True,
        primary_key = True,
        nullable = False,
        autoincrement = True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    interaction_id: Mapped[int] = mapped_column(ForeignKey("interactions.id"))
    follows_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_mutual: Mapped[bool] = mapped_column(default=False)
    timestamp: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default=datetime.now())

    users = relationship("User", foreign_keys=[user_id])
    followers = relationship("User", foreign_keys=[follows_user_id])
    
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
    first_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    middle_name: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    pronouns: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date_of_birth: Mapped[date] = mapped_column(nullable=True, default=None)
    bio: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    occupation: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date_created: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default=datetime.now())
    last_updated: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default=datetime.now())
    
    posts = relationship("Post", back_populates="user", order_by="Post.timestamp.desc()")
    media_collections: Mapped[List["MediaCollection"]] = relationship(back_populates="user")

    #returns username
    def get_username(self):
        return self.user_name
    
    #updates any or all fields in a user object
    def update(self, **kwargs):

        update_time = datetime.now()

        fields = self.__table__.c.keys()[1:]
        for key, value in kwargs.items():
            if key in fields:
                print("setting column: " + str(key) + " to value: " + str(value))
                setattr(self, key, value)

        self.last_updated = update_time
        session.commit()

    #inserts a post by that user.
    def post(self, text):
        post = insert_post(self, text)
        return post

    def is_following(self, to_user):
        stmt = select(Interaction).where(
            Interaction.interaction_type == "follow", 
            Interaction.from_user_id == self.id, 
            Interaction.to_user_id == to_user.id)

        try:
            following = session.execute(stmt).one()
            return following
        except NoResultFound:
            return False
                
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
    media_collection_id: Mapped[Optional[int]] = mapped_column(ForeignKey("media_collection.id"), default=None)
    text: Mapped[str] = mapped_column(Text, nullable = True)
    timestamp: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default = datetime.now())
    like_count: Mapped[int] = mapped_column(default=0)
    
    media_collection: Mapped[Optional["MediaCollection"]] = relationship(back_populates="post")
    user = relationship("User", back_populates="posts")

    #from a Post object, inserts a nother Post object as a reply.
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
    
    def get_replies(self):
        stmt = select(Post).where(
            Post.parent_id == self.id
            )
        
        replies = session.scalars(stmt).all()

        return replies

    #increments like count of a post.
    #takes in the user object that is liking the post.
    #maps interaction as a "like" interaction FROM the user liking TO the author of the post.
    def like(self, user):
        self.like_count = self.like_count + 1
        session.commit()
        insert_interaction(user, self.user, post=self, interaction_type="like")
    
    def unlike(self, user):
        delete_interaction(user, self.user, post=self, interaction_type="like")

    def is_liked(self, user):

        stmt = select(Interaction).where(
            Interaction.interaction_type == "like", 
            Interaction.post_id == self.id, 
            Interaction.from_user_id == user.id)

        try:
            liked = session.execute(stmt).one()
            return liked
        except NoResultFound:
            return None

class MediaCollection(Base):
    __tablename__ = 'media_collection'

    id: Mapped[int] = mapped_column(
        unique = True, 
        primary_key=True, 
        nullable=False,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    interaction_id: Mapped[int] = mapped_column(nullable=True, default=None)
    collection_type: Mapped[str] =  mapped_column(String(255), nullable=False, default="gallery")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    photo_count: Mapped[int] = mapped_column(nullable=False, default=0)
    video_count: Mapped[int] = mapped_column(nullable=False, default=0)
    date_created: Mapped[datetime] = mapped_column(DATETIME(fsp=6), default=datetime.now())

    user: Mapped["User"] = relationship(back_populates="media_collections")
    media: Mapped[List["Media"]] = relationship(back_populates="media_collection")
    post: Mapped["Post"] = relationship(back_populates="media_collection")

    def add_media(self, media):
        media.collection_id = self.id
        self.media.append(media)
        session.commit()
        return media

class Media(Base):
    __tablename__ = 'media'

    id: Mapped[int] = mapped_column(
        unique = True,
        primary_key = True,
        nullable = False,
        autoincrement = True
    )

    collection_id: Mapped[Optional[int]] = mapped_column(ForeignKey("media_collection.id"))
    media_type: Mapped[str] = mapped_column(String(255), default='photo')
    file_path: Mapped[str] = mapped_column(String(255), default='\\')

    #adds current media to collection.
    def add_to_collection(self, user=None, post=None, collection=None):

        if collection is not None:
            self.collection_id = collection.id
            session.commit()
        else:
            collection = MediaCollection(
                user_id = user.id,
                post = post
            )
            session.add(collection)
            session.commit()

            self.add_to_collection(user, post, collection)
        return collection

    media_collection = relationship("MediaCollection", back_populates="media")
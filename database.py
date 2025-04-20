from asgiref.sync import sync_to_async
from flask import session
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, ChatMessage, CheckReferral, TetxStory, Advertise
from datetime import datetime, timedelta
from sqlalchemy import  func

@sync_to_async
def get_user(user_id: int, session: AsyncSession):
    result =  session.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one()

@sync_to_async
def user_exists(user_id: int, session: AsyncSession):
    result =  session.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one_or_none() is not None

@sync_to_async
def register_user(user_id: int, session: AsyncSession):
    user = User(user_id=user_id)
    session.add(user)
    session.commit()
    return user

@sync_to_async
def update_user_username(user, username: str, session: AsyncSession):
    user.username = username
    session.commit()
    return user

@sync_to_async
def update_user_usage(user ,session: AsyncSession):
    user.usage += 1
    session.commit()
    return user

@sync_to_async
def last_message(user_id: int, message_id: str, session: AsyncSession):
    result =  session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one()
    user.last_message_id = message_id
    session.commit()

@sync_to_async
def check_activity(user_id: int, session: AsyncSession):
    result =  session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False
    return datetime.utcnow() - user.lastActive > timedelta(hours=24)

@sync_to_async
def get_last_messages(user: User, session: AsyncSession):
    result =  session.execute(
        select(ChatMessage).where(ChatMessage.user_id == user.user_id).order_by(ChatMessage.timestamp.desc()).limit(18)
    )
    messages = result.scalars().all()
    return messages[::-1]

@sync_to_async
def save_message(user: User, text_message: str, mode: str, session: AsyncSession):
    is_user = mode == "is_user"
    message = ChatMessage(user_id=user.user_id, content=text_message, is_user=is_user)
    session.add(message)
    session.commit()


@sync_to_async
def get_text_story(story_id: int, session: AsyncSession):
    result =  session.execute(select(TetxStory).where(TetxStory.story_id == story_id))
    story = result.scalar_one_or_none()
    return story or False


@sync_to_async
def add_text_story(story_id: int, text: str, session: AsyncSession):
    story = TetxStory(story_id=story_id, text=text)
    session.add(story)
    session.commit()
    return story


@sync_to_async
def update_text_custom(user , text , session: AsyncSession):
    user.text_custom = text
    session.commit()






@sync_to_async
def add_advertise(user , username , title , description ,session: AsyncSession):
    ad = Advertise(user_id = user.user_id , username= username ,title= title ,description= description)
    session.add(ad)
    session.commit()


@sync_to_async
def advertise_exist(user , session :AsyncSession):
    result = session.execute(select(Advertise).where(user_id=user.user_id))
    return result.scalar_one_or_none() is not None


@sync_to_async
def status_advertise(username , session :AsyncSession):
    result = session.execute(select(Advertise).where(username=username))
    return result.scalar_one()

@sync_to_async
def acceppt_advertise(status , session: AsyncSession):
    status.status = True
    session.commit()


@sync_to_async
def get_user_message_count(user: User, session: AsyncSession):
    result = session.execute(
        select(func.count(ChatMessage.id)).where(
            ChatMessage.user_id == user.user_id,
            ChatMessage.is_user == True
        )
    )
    count = result.scalar_one()
    return count




@sync_to_async
def get_advertise(ad_name , session: AsyncSession):
    result = session.execute(select(Advertise).where(
        title = ad_name ,
        status = True,
        show = True,
    ))
    ad = result.scalar_one_or_none()
    return ad or False













# async def set_advertise_timestamp(advertise_id: int, session: AsyncSession):
#     result = await session.execute(
#         select(Advertise).where(Advertise.id == advertise_id)
#     )
#     ad = result.scalar_one_or_none()
#     if ad:
#         ad.created_at = datetime.utcnow()
#         await session.commit()
#         return True
#     return False
#
#







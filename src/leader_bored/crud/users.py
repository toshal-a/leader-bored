from ..models.users import User
from ..schemas.users import UserCreate


async def get_user_by_id(user_id: int):
    user = await User.get_or_404(user_id)
    return user.to_dict()


async def get_all_users():
    all_users = await User.query.order_by(User.overall_score.desc()).gino.all()
    return all_users


async def get_user_score(user_id: int):
    score = await User.select('overall_score').where(User.id == user_id).gino.scalar()
    return dict(overall_score=score)


async def get_all_handles():
    handles = await User.select('codeforces_handle').gino.all()
    return handles


async def create_user(user: UserCreate):
    rv = await User.create(
        full_name=user.full_name,
        email=user.email,
        hashed_password=user.password,
        codeforces_handle=user.codeforces_handle,
        current_class=user.current_class,
        overall_score=user.overall_score,
    )
    return rv.to_dict()


async def delete_user_by_id(user_id: int):
    user = await User.get_or_404(user_id)
    await user.delete()
    return dict(id=user_id)


async def update_user_score(user_id: int, score: int):
    user = await User.get_or_404(user_id)
    await user.update(overall_score=user.overall_score+score).apply()
    return user.to_dict()

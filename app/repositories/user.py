from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def find_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def create(self, username: str, password: str, salt: str) -> User:
        user = User(
            username=username,
            password=password,
            salt=salt
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def delete(self, user: User) -> None:
        await self.session.delete(user)

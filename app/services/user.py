from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.models.user import User
from app.schemas.user import UserRegisterRequest
from app.core.security import generate_salt, hash_password, verify_password
from app.core.jwt import create_access_token


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
    
    async def register(self, data: UserRegisterRequest) -> User:
        existing_user = await self.repository.find_by_username(data.username)
        if existing_user:
            raise ValueError("用户名已存在")
        
        salt = generate_salt()
        hashed_password = hash_password(data.password, salt)
        
        user = await self.repository.create(
            username=data.username,
            password=hashed_password,
            salt=salt
        )
        return user
    
    async def login(self, username: str, password: str) -> tuple[User, str]:
        user = await self.repository.find_by_username(username)
        if not user:
            raise ValueError("用户名或密码错误")
        
        if not verify_password(password, user.salt, user.password):
            raise ValueError("用户名或密码错误")
        
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        return user, access_token
    
    async def get_by_id(self, user_id: int) -> User | None:
        return await self.repository.find_by_id(user_id)
    
    async def get_by_username(self, username: str) -> User | None:
        return await self.repository.find_by_username(username)

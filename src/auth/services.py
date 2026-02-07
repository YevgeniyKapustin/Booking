from src.auth.repositories import UserRepository
from src.auth.schemas import Token, UserCreate, UserLogin
from src.core.errors import BusinessError, UnauthorizedError
from src.core.logging_decorators import log_service
from src.core.security import create_access_token, hash_password, verify_password
from src.tasks.tasks import send_welcome_email


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    @log_service
    async def register(self, data: UserCreate) -> Token:
        await self.validate_email(data.email)
        user_id = await self.users.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone_number=data.phone_number,
        )
        send_welcome_email.delay(data.email, data.full_name)
        return Token(access_token=create_access_token(user_id))

    @log_service
    async def login(self, data: UserLogin) -> Token:
        user = await self.users.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        return Token(access_token=create_access_token(user.id))

    @log_service
    async def validate_email(self, email: str) -> None:
        existing = await self.users.get_by_email(email)
        if existing:
            raise BusinessError("Email already registered")

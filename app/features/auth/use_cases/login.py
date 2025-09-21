from .ports import PasswordHasher, TokenService, UserRepo


class Login:
    def __init__(self, repo: UserRepo, hasher: PasswordHasher, token_service: TokenService):
        self.repo = repo
        self.hasher = hasher
        self.token_service = token_service

    async def execute(self, username: str, password: str) -> str:
        user = await self.repo.by_username(username)
        if not user:
            raise ValueError("User not found")

        if self.hasher.needs_rehash(user.password_hash):
            user.password_hash = self.hasher.hash(password)
            await self.repo.update(user)

        access_token = self.token_service.issue_access(user, ["me:read"])
        return {"access_token": access_token, "token_type": "Bearer"}

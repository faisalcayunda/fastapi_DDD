from app.features.auth.api.schemas import TokenOut


class AuthPresenter:
    def present(self, access_token: str) -> dict:
        return TokenOut(access_token=access_token, token_type="bearer").model_dump()

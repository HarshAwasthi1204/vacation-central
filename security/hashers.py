from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def get_hashed_password(plain_password: str) -> str:
    return password_context.hash(plain_password)

# def get_hashed_password(password : str) -> str:
#     return password+"lol"
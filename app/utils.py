from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(content: str):
    return context.hash(content)


def verify(plain, hashed):
    return context.verify(plain, hashed)

import datetime

import jwt

from data.userds import UserDataSource

userds = UserDataSource("./mockdata/users.csv")

SECRET = "my_super_secret_secret"

def check_password(user: str, password: str) -> bool:
    """
    Verifica se o nome de usuário e a senha fornecidos estão corretos
    """
    return userds.checkpass(user, password)

def emit_jwt(user: str, password: str) -> str:
    """
    Emite um token JWT para o usuário autenticado.
    """
    if not userds.checkpass(user, password):
        raise Exception("Invalid user or password")

    payload = {
        "now": str(datetime.datetime.now()),
        "user": user,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    }

    return jwt.encode(payload, SECRET, algorithm="HS256")


def check_jwt(token: str) -> bool:
    """
    Verifica se o token JWT é válido e não expirou.
    """
    try:
        _ = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print(f"Invalid token: {token}")
        return False
    except Exception as e:
        print(e)
        return False

    return True

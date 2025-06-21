import jwt
import datetime
from data.userds import UserDataSource

userds = UserDataSource("./mockdata/users.csv")

secret = "my_super_secret_secret"

def check_password(user: str, password: str) -> bool:
    return userds.checkpass(user, password)

def emit_jwt(user: str, password: str) -> str:
    if not userds.checkpass(user, password):
        raise Exception("Invalid user or password")

    payload = {
        "now": str(datetime.datetime.now()),
        "user": user,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    }

    return jwt.encode(payload, secret, algorithm="HS256")


def check_jwt(token: str) -> bool:
    print(token)

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print("Invalid token: {}".format(token))
        return False
    except Exception as e:
        print(e)
        return False

    return True
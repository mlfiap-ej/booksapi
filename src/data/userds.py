import csv


class UserDataSource:

    def __init__(self, path: str):
        self.__userpool = []

        with open(path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            _ = next(csv_reader)
            for row in csv_reader:
                self.__userpool.append({'user': row[0], 'password': row[1]})

    def checkpass(self, user: str, password: str) -> bool:
        users = list(filter(lambda u: u['user'] == user, self.__userpool))
        if not users:
            return False
        user = users[0]
        if user['password'] != password:
            return False
        return True
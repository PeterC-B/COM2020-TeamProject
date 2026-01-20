

class RegisterUser:
    def __init__(self, uow, user_repo):
        self.uow = uow
        self.user_repo = user_repo

    def execute(self):
        print("Implement create user here")
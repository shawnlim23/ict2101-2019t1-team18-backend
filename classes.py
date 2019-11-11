class User:
    def __init__(
        self, email, password, salt="", name="", age=-1, sex=0, commute_method=0
    ):
        self.email = email
        self.password = password
        self.salt = salt
        self.name = name
        self.age = age
        # ISO/IEC 5218: 0 = "Not Known", 1 = "male", 2 = "female", 9 = "N.A."
        self.sex = sex
        self.commute_method = commute_method

class User:
    def __init__(
        self,
        email,
        password,
        salt="",
        name="",
        birthdate="",
        sex="Not Known",
        commute_method="",
        userID=None,
        active=True,
    ):
        self.email = email
        self.password = password
        self.salt = salt
        self.name = name
        self.birthdate = birthdate
        # ISO/IEC 5218: 0 = "Not Known", 1 = "male", 2 = "female", 9 = "N.A."
        self.sex = sex
        self.commute_method = commute_method
        self.userID = userID
        self.active = active


class Landmark:
    def __init__(self, placeID, name="", description="", active=True):
        self.placeID = placeID
        self.name = name
        self.description = description
        self.active = active


class Canvas:
    def __init__(
        self,
        userID,
        placeID,
        title="",
        description="",
        editable=True,
        active=True,
        canvasID=None,
    ):
        self.canvasID = canvasID
        self.userID = userID
        self.placeID = placeID
        self.title = title
        self.description = description
        self.editable = editable
        self.active = active


class Comment:
    def __init__(
        self, userID, canvasID, commentID=None, text="", timestamp="", active=True
    ):
        self.userID = userID
        self.canvasID = canvasID
        self.commentID = commentID
        self.text = text
        self.timestamp = timestamp
        self.active = active

import jam.session

class TestSession(jam.session.Session):

    def __init__(self):
        pass

    def build(self):
        return True

    def my_method(self):
        return 1


class TestAnotherClass(object):
    pass

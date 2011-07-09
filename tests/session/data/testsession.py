import jam.session

class TestSession(jam.session.Session):

    version = "1.0"
    name = "test"

    def build(self):
        return True

    def configure(self):
        pass

    def my_method(self):
        return 1


class TestAnotherClass(object):
    pass

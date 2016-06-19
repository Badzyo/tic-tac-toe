from flask_login import AnonymousUserMixin


class GuestUserMixin(AnonymousUserMixin):
    def __init__(self):
        super().__init__()
        self.username = 'Guest'

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


class AppTokenGenerator(PasswordResetTokenGenerator):
    def __make_hash_value(self, user, timestamp):
        return text_type(user.is_active) + text_type(user) + text_type(timestamp)
        # return super()._make_hash_value(user, timestamp)
token_generator = AppTokenGenerator()


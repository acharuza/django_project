from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


class TokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator for email confirmation.

    This token generator is used to generate unique tokens for email confirmation
    when a user registers or updates their email address.

    Methods:
        - _make_hash_value(user, timestamp): Generates a hash value using user-related information.

    Example Usage:
    account_activation_token = TokenGenerator()
    token = account_activation_token.make_token(user)

    Note:
        - The generated token includes the user's primary key, timestamp, and email verification status.
    """

    def _make_hash_value(self, user, timestamp):
        return (
                text_type(user.pk) + text_type(timestamp) +
                text_type(user.email_is_verified)
        )


account_activation_token = TokenGenerator()

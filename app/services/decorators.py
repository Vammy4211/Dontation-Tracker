# Simple validation decorator for user models

def validate_email(func):
    """Check if email looks valid"""
    def wrapper(self, *args, **kwargs):
        if hasattr(self, 'email') and self.email:
            if '@' not in self.email:
                raise ValueError("Email must contain @")
        return func(self, *args, **kwargs)
    return wrapper

def validate_password(func):
    """Check password strength"""
    def wrapper(self, *args, **kwargs):
        if hasattr(self, 'password_hash') and self.password_hash:
            if len(self.password_hash) < 8:
                raise ValueError("Password too short")
        return func(self, *args, **kwargs)
    return wrapper
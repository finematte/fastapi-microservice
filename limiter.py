from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize and configure Limiter
limiter = Limiter(key_func=get_remote_address)

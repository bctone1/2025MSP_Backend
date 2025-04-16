import random

def generate_verification_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

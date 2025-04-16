import random

def generate_verification_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

code = generate_verification_code()
print(f"인증 코드: {code}")
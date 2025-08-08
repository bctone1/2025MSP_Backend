import requests
import os
import datetime
import random
from core.config import UPLOAD_FOLDER

# 예시용 무작위 단어 리스트
WORDS = [
    "sunflower", "moonlight", "cascade", "ember", "glimmer",
    "echo", "breeze", "starlight", "willow", "nova"
]

def generate_filename() -> str:
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    word = random.choice(WORDS)
    return f"{date_str}_{word}.png"


def save_image_from_url(image_url: str, user_email: str):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    user_folder = os.path.join(UPLOAD_FOLDER, user_email, "image")
    os.makedirs(user_folder, exist_ok=True)

    filename = generate_filename()
    file_path = os.path.join(user_folder, filename)

    save_name = f"{user_email}\\image\\{filename}"

    try:
        response = requests.get(image_url)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"이미지를 성공적으로 저장했습니다: {file_path}")
        return save_name

    except Exception as e:
        raise Exception(f"이미지 저장 실패: {e}")
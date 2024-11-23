# Import libraries
import os
import sys
import jwt  # ใช้สำหรับจัดการ JWT (สร้างและตรวจสอบ)
import time  # ใช้สำหรับสร้าง timestamp (เวลาปัจจุบัน)
import json  # ใช้สำหรับจัดการไฟล์และข้อมูล JSON

outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.yaml_env import load_yaml_to_env
load_yaml_to_env("scripts/line_secret.yml")
# Read private key from a file
with open("private_key.json", "r") as f:  # เปิดไฟล์ private_key.json ในโหมดอ่าน
    private_key_string = f.read()  # อ่านข้อมูลในไฟล์ทั้งหมดและเก็บไว้ในตัวแปร
private_key = json.loads(private_key_string)  # ดึงข้อมูล JSON มาไว้ในตัวแปร private_key

# Define JWT headers
headers = {
    "alg": "RS256",  # ระบุอัลกอริทึมที่ใช้สำหรับเซ็นชื่อ (ในที่นี้คือ RSA-SHA256)
    "typ": "JWT",  # ระบุว่า token ที่สร้างคือ JWT
    "kid": os.getenv("KID"),  # ใส่ Key ID ที่เชื่อมโยงกับ public key ที่เราไปผูกไว้ในหน้า LINE Developer Console
}


# Define JWT payload
payload = {
    "iss": os.getenv("CHANNEL_ID"),  # Issuer: ระบุ Channel ID ของผู้สร้าง token
    "sub": os.getenv("CHANNEL_ID"),  # Subject: ระบุ Channel ID ของผู้ใช้ token
    "aud": "https://api.line.me/",  # Audience: ระบุปลายทาง (API endpoint) ที่ใช้สร้าง Channel Access Token ใช้ได้
    "exp": int(time.time())
    + (60 * 30),  # Expiration: เวลาหมดอายุของ token (ปัจจุบัน + 30 นาที)
    "token_exp": 60 * 60 * 24 * 30,  # อายุ token (30 วัน)
}

# Generate JWT
key = jwt.algorithms.RSAAlgorithm.from_jwk(
    private_key
)  # แปลง JWK ที่อ่านจากไฟล์ให้เป็น RSA key object
JWT = jwt.encode(payload, key, algorithm="HS256", headers=headers, json_encoder=None)

# Display the generated token
print(f"Generated JWT: {JWT}")

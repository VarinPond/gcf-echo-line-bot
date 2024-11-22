from jwcrypto import jwk
import json

# สร้างคู่คีย์ RSA (Private และ Public Key)
key = jwk.JWK.generate(
    kty="RSA",  # ชนิดของคีย์: RSA (เป็นการเข้ารหัสแบบอสมมาตร)
    alg="RS256",  # อัลกอริทึม: RSA กับ SHA-256 (ใช้สำหรับการเซ็นดิจิทัล)
    use="sig",  # การใช้งาน: ใช้สำหรับการเซ็นดิจิทัล (Signature)
    size=2048,  # ขนาดคีย์: 2048 บิต (ปลอดภัยและเป็นมาตรฐาน)
)
private_key = key.export_private()
public_key = key.export_public()

print("=== private key ===\n" + json.dumps(json.loads(private_key), indent=2))
print("=== public key ===\n" + json.dumps(json.loads(public_key), indent=2))

# บันทึก Private Key ลงในไฟล์ private_key.json
with open("private_key.json", "w") as f:
    f.write(private_key)

# บันทึก Public Key ลงในไฟล์ public_key.json
with open("public_key.json", "w") as f:
    f.write(public_key)

from cryptography.fernet import Fernet

# Generate and save key
key = Fernet.generate_key()
with open("secret.key", "wb") as f:
    f.write(key)

print("✅ Secret key generated and saved in secret.key")

from werkzeug.security import generate_password_hash

password = "pauricard"
hashed_password = generate_password_hash(password)

print(f"Contrasenya: {password}")
print(f"Hash per a la base de dades:\n{hashed_password}")
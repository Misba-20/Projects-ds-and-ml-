from werkzeug.security import generate_password_hash

# Generate password hash for admin
password = "admin123"
hashed = generate_password_hash(password)
print(f"Password: {password}")
print(f"Hash: {hashed}")

# SQL to update admin password
print(f"\nUPDATE admins SET password='{hashed}' WHERE email='admin@nutrismart.com';")
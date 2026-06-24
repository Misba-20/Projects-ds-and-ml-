import pymysql

def get_connection():
    """Get database connection with proper settings"""
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="nutrismart_ai",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

# Test connection
if __name__ == '__main__':
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
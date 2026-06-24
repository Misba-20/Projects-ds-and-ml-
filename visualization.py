import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import os
from decimal import Decimal
import pymysql

os.makedirs('static/images', exist_ok=True)

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="nutrismart_ai",
        cursorclass=pymysql.cursors.DictCursor
    )

def convert_to_float(value):
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0

# ============================================================
# 👤 USER PANEL - Personal Analytics
# ============================================================

def generate_user_bmi_progress(user_id):
    """User's BMI progress over time"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT created_at, bmi 
        FROM health_profiles 
        WHERE user_id = %s AND bmi IS NOT NULL
        ORDER BY created_at
    """, (user_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data or len(data) < 2:
        return None
    
    df = pd.DataFrame(data)
    df['bmi'] = df['bmi'].apply(convert_to_float)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at')
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['created_at'], df['bmi'], marker='o', color='#38BDF8', linewidth=2)
    plt.fill_between(df['created_at'], df['bmi'], alpha=0.2, color='#38BDF8')
    plt.xlabel('Date', color='white')
    plt.ylabel('BMI', color='white')
    plt.title('My BMI Progress', color='white', fontsize=16)
    plt.tick_params(colors='white')
    plt.grid(alpha=0.3)
    plt.xticks(rotation=45)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1E293B', transparent=False, bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

def generate_user_calorie_breakdown(user_id):
    """User's calorie breakdown"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT calorie_requirement 
        FROM health_profiles 
        WHERE user_id = %s 
        ORDER BY id DESC 
        LIMIT 1
    """, (user_id,))
    
    data = cursor.fetchone()
    conn.close()
    
    if not data:
        return None
    
    calories = convert_to_float(data.get('calorie_requirement'))
    
    # Create calorie breakdown
    categories = ['Protein', 'Carbs', 'Fat']
    protein = calories * 0.30 / 4  # 30% from protein (4 cal/g)
    carbs = calories * 0.40 / 4    # 40% from carbs (4 cal/g)
    fat = calories * 0.30 / 9      # 30% from fat (9 cal/g)
    
    values = [protein, carbs, fat]
    
    plt.figure(figsize=(8, 6))
    colors = ['#38BDF8', '#22C55E', '#F59E0B']
    
    plt.pie(values, labels=categories, autopct='%1.1f%%', 
            colors=colors, startangle=90, textprops={'color': 'white'})
    plt.title(f'My Calorie Breakdown ({int(calories)} kcal/day)', color='white', fontsize=16)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1E293B', transparent=False, bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

def generate_user_nutrition_summary(user_id):
    """User's nutrition summary"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT AVG(protein) as protein, AVG(carbs) as carbs, 
               AVG(fat) as fat, AVG(fiber) as fiber
        FROM nutrition_logs 
        WHERE user_id = %s
    """, (user_id,))
    
    data = cursor.fetchone()
    conn.close()
    
    if not data or not data.get('protein'):
        # If no logs, use default values
        nutrition_data = {
            'Protein': 50.0,
            'Carbs': 200.0,
            'Fat': 60.0,
            'Fiber': 25.0
        }
    else:
        nutrition_data = {
            'Protein': convert_to_float(data.get('protein', 0)),
            'Carbs': convert_to_float(data.get('carbs', 0)),
            'Fat': convert_to_float(data.get('fat', 0)),
            'Fiber': convert_to_float(data.get('fiber', 0))
        }
    
    plt.figure(figsize=(8, 6))
    colors = ['#38BDF8', '#22C55E', '#F59E0B', '#A855F7']
    
    bars = plt.bar(nutrition_data.keys(), nutrition_data.values(), color=colors)
    plt.ylabel('Grams (g)', color='white')
    plt.title('My Average Nutrition', color='white', fontsize=16)
    plt.tick_params(colors='white')
    plt.grid(alpha=0.3)
    
    for i, (key, value) in enumerate(nutrition_data.items()):
        plt.text(i, value + 0.5, f'{value:.1f}g', 
                 ha='center', color='white', fontsize=12)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1E293B', transparent=False, bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

# ============================================================
# 👨‍💼 ADMIN PANEL - Overall Analytics
# ============================================================

def generate_admin_user_growth():
    """User growth over time"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM users
        GROUP BY DATE(created_at)
        ORDER BY date
    """)
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Cumulative sum
    df['cumulative'] = df['count'].cumsum()
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['cumulative'], marker='o', color='#8B5CF6', linewidth=2)
    plt.fill_between(df['date'], df['cumulative'], alpha=0.2, color='#8B5CF6')
    plt.xlabel('Date', color='white')
    plt.ylabel('Total Users', color='white')
    plt.title('User Growth Over Time', color='white', fontsize=16)
    plt.tick_params(colors='white')
    plt.grid(alpha=0.3)
    plt.xticks(rotation=45)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1E293B', transparent=False, bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

def generate_admin_platform_stats():
    """Platform statistics charts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total users
    cursor.execute("SELECT COUNT(*) as total FROM users")
    total_users = cursor.fetchone()
    
    # Total health profiles
    cursor.execute("SELECT COUNT(*) as total FROM health_profiles")
    total_profiles = cursor.fetchone()
    
    # Total foods
    cursor.execute("SELECT COUNT(*) as total FROM foods")
    total_foods = cursor.fetchone()
    
    # Today's users
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE DATE(created_at) = CURDATE()")
    today_users = cursor.fetchone()
    
    conn.close()
    
    stats = {
        'Total Users': convert_to_float(total_users.get('total', 0)),
        'Health Profiles': convert_to_float(total_profiles.get('total', 0)),
        'Food Items': convert_to_float(total_foods.get('total', 0)),
        'New Today': convert_to_float(today_users.get('total', 0))
    }
    
    plt.figure(figsize=(10, 6))
    colors = ['#38BDF8', '#22C55E', '#F59E0B', '#8B5CF6']
    
    bars = plt.bar(stats.keys(), stats.values(), color=colors)
    plt.ylabel('Count', color='white')
    plt.title('Platform Statistics', color='white', fontsize=16)
    plt.tick_params(colors='white')
    plt.grid(alpha=0.3)
    
    for i, (key, value) in enumerate(stats.items()):
        plt.text(i, value + 0.5, f'{int(value)}', 
                 ha='center', color='white', fontsize=14, fontweight='bold')
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1E293B', transparent=False, bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

def generate_admin_disease_distribution():
    """Disease distribution among all users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT diseases, COUNT(*) as count 
        FROM health_profiles 
        WHERE diseases IS NOT NULL AND diseases != ''
        GROUP BY diseases
        ORDER BY count DESC
        LIMIT 8
    """)
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    plt.figure(figsize=(10, 6))
    colors = ['#EF4444', '#F59E0B', '#22C55E', '#38BDF8', '#8B5CF6', '#06B6D4', '#A855F7', '#14B8A6']
    
    plt.pie(df['count'], labels=df['diseases'], 
            autopct='%1.1f%%', colors=colors[:len(df)],
            startangle=90, textprops={'color': 'white'})
    plt.title('Disease Distribution (All Users)', color='white', fontsize=16)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1E293B', transparent=False, bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

def generate_admin_goal_distribution():
    """Goal distribution among all users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT goal, COUNT(*) as count 
        FROM health_profiles 
        WHERE goal IS NOT NULL
        GROUP BY goal
        ORDER BY count DESC
    """)
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    plt.figure(figsize=(10, 6))
    colors = ['#38BDF8', '#22C55E', '#F59E0B', '#8B5CF6', '#EF4444']
    
    plt.bar(df['goal'], df['count'], color=colors[:len(df)])
    plt.xlabel('Goal', color='white')
    plt.ylabel('Number of Users', color='white')
    plt.title('User Goals Distribution', color='white', fontsize=16)
    plt.tick_params(colors='white')
    plt.xticks(rotation=15)
    plt.grid(alpha=0.3)
    
    for i, row in df.iterrows():
        plt.text(i, row['count'] + 0.5, str(row['count']), 
                 ha='center', color='white', fontsize=12)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1E293B', transparent=False, bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

def generate_admin_activity_distribution():
    """Activity level distribution among all users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT activity_level, COUNT(*) as count 
        FROM health_profiles 
        WHERE activity_level IS NOT NULL
        GROUP BY activity_level
        ORDER BY count DESC
    """)
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    plt.figure(figsize=(10, 6))
    colors = ['#22C55E', '#38BDF8', '#F59E0B', '#8B5CF6', '#EF4444']
    
    plt.pie(df['count'], labels=df['activity_level'], 
            autopct='%1.1f%%', colors=colors[:len(df)],
            startangle=90, textprops={'color': 'white'})
    plt.title('Activity Level Distribution', color='white', fontsize=16)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1E293B', transparent=False, bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()
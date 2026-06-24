from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import random
import joblib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "nutrismart_secret_key_2024"

# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    """Create and return a database connection"""
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="nutrismart_ai",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

# =========================================================
# ML MODEL LOADING WITH ERROR HANDLING
# =========================================================

def load_ml_models():
    """Load ML models with proper error handling"""
    try:
        model = joblib.load('ml/diet_model.pkl')
        le_disease = joblib.load('ml/le_disease.pkl')
        le_goal = joblib.load('ml/le_goal.pkl')
        le_diet = joblib.load('ml/le_diet.pkl')
        return model, le_disease, le_goal, le_diet
    except Exception as e:
        print(f"Error loading ML models: {e}")
        return None, None, None, None

# Load models
model, le_disease, le_goal, le_diet = load_ml_models()

# =========================================================
# DECORATORS
# =========================================================

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin login required', 'warning')
            return redirect('/admin-login')
        return f(*args, **kwargs)
    return decorated_function

# =========================================================
# HOME PAGE
# =========================================================

@app.route('/')
def home():
    return render_template('index.html')

# =========================================================
# USER REGISTRATION
# =========================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')

        if not all([fullname, email, password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                flash('Email already registered', 'danger')
                return render_template('register.html')

            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users(fullname, email, phone, password) VALUES(%s,%s,%s,%s)",
                (fullname, email, phone, hashed_password)
            )
            flash('Registration successful! Please login.', 'success')
            return redirect('/login')

        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')
            return render_template('register.html')
        finally:
            conn.close()

    return render_template('register.html')

# =========================================================
# USER LOGIN
# =========================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['name'] = user['fullname']
                flash(f'Welcome back, {user["fullname"]}!', 'success')
                return redirect('/dashboard')
            else:
                flash('Invalid email or password', 'danger')
                return render_template('login.html')

        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
            return render_template('login.html')
        finally:
            conn.close()

    return render_template('login.html')

# =========================================================
# USER DASHBOARD
# =========================================================

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user profile data
    cursor.execute(
        """SELECT * FROM user_profile 
           WHERE user_id=%s ORDER BY id DESC LIMIT 1""",
        (session['user_id'],)
    )
    profile = cursor.fetchone()
    
    # Get health profile data
    cursor.execute(
        """SELECT * FROM health_profiles 
           WHERE user_id=%s ORDER BY id DESC LIMIT 1""",
        (session['user_id'],)
    )
    health = cursor.fetchone()
    
    conn.close()
    
    return render_template(
        'dashboard.html', 
        name=session.get('name', 'User'),
        profile=profile,
        health=health
    )


# =========================================================
# USER PROFILE
# =========================================================
@app.route('/user-profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current profile
    cursor.execute(
        "SELECT * FROM user_profile WHERE user_id=%s ORDER BY id DESC LIMIT 1",
        (session['user_id'],)
    )
    profile = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        age = request.form.get('age')
        gender = request.form.get('gender')
        height = request.form.get('height')
        weight = request.form.get('weight')

        if not all([age, gender, height, weight]):
            flash('All fields are required', 'danger')
            return render_template('user_profile.html', profile=profile)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            if profile:
                cursor.execute(
                    """UPDATE user_profile 
                       SET age=%s, gender=%s, height=%s, weight=%s 
                       WHERE user_id=%s""",
                    (age, gender, height, weight, session['user_id'])
                )
            else:
                cursor.execute(
                    """INSERT INTO user_profile (user_id, age, gender, height, weight) 
                       VALUES (%s,%s,%s,%s,%s)""",
                    (session['user_id'], age, gender, height, weight)
                )

            flash('Profile updated successfully!', 'success')
            return redirect('/dashboard')

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return render_template('user_profile.html', profile=profile)
        finally:
            conn.close()

    return render_template('user_profile.html', profile=profile)
# =========================================================
# HEALTH PROFILE
# =========================================================

@app.route('/health-profile', methods=['GET', 'POST'])
@login_required
def health_profile():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get user profile
    cursor.execute(
        """SELECT * FROM user_profile 
           WHERE user_id=%s ORDER BY id DESC LIMIT 1""",
        (session['user_id'],)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        flash('Please create your basic profile first', 'warning')
        return redirect('/user-profile')

    if request.method == 'POST':
        # Get basic info from user profile
        age = user['age']
        gender = user['gender']
        height = float(user['height'])
        weight = float(user['weight'])

        # Get form data
        diseases = ",".join(request.form.getlist('diseases')) or "None"
        allergies = ",".join(request.form.getlist('allergies')) or "None"
        goal = request.form.get('goal')
        lifestyle = request.form.get('lifestyle')
        food_preference = request.form.get('food_preference')
        activity_level = request.form.get('activity_level', 'Sedentary')
        redirect_to = request.form.get('redirect_to', 'recommendations')

        if not all([goal, lifestyle, food_preference]):
            flash('Please fill all required fields', 'danger')
            return render_template('health_profile.html', user=user)

        # Calculate BMI
        bmi = round(weight / ((height/100) ** 2), 2)

        # Determine risk level
        if bmi < 18.5:
            risk_level = "Underweight"
        elif bmi < 25:
            risk_level = "Normal"
        elif bmi < 30:
            risk_level = "Overweight"
        else:
            risk_level = "Obese"

        # Calculate calories
        if gender.lower() == 'male':
            calories = int(10 * weight + 6.25 * height - 5 * age + 5)
        else:
            calories = int(10 * weight + 6.25 * height - 5 * age - 161)

        activity_multipliers = {
            'Sedentary': 1.2,
            'Lightly Active': 1.375,
            'Moderately Active': 1.55,
            'Very Active': 1.725,
            'Extremely Active': 1.9
        }
        calories = int(calories * activity_multipliers.get(activity_level, 1.2))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO health_profiles 
                   (user_id, age, gender, height, weight, bmi, 
                    diseases, allergies, goal, lifestyle, 
                    food_preference, activity_level, 
                    calorie_requirement, risk_level)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (session['user_id'], age, gender, height, weight, bmi,
                 diseases, allergies, goal, lifestyle,
                 food_preference, activity_level, calories, risk_level)
            )
            
            flash('✅ Health profile updated successfully!', 'success')
            
            if redirect_to == 'meal_plan':
                return redirect('/dynamic-meal-plan')
            else:
                return redirect('/recommendations')

        except Exception as e:
            flash(f'Error saving health profile: {str(e)}', 'danger')
            return render_template('health_profile.html', user=user)
        finally:
            conn.close()

    return render_template('health_profile.html', user=user)
# =========================================================
# FOOD RECOMMENDATIONS
# =========================================================

@app.route('/recommendations')
@login_required
def recommendations():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get latest health profile
    cursor.execute(
        """SELECT * FROM health_profiles 
           WHERE user_id=%s ORDER BY id DESC LIMIT 1""",
        (session['user_id'],)
    )
    profile = cursor.fetchone()

    if not profile:
        flash('Please complete your health profile first', 'warning')
        conn.close()
        return redirect('/health-profile')

    disease = profile.get('diseases', 'None') or 'None'
    allergies = profile.get('allergies', '') or ''
    food_preference = profile.get('food_preference', '') or ''
    region = profile.get('main_region', '') or ''

    # ✅ FIX: Filter foods based on disease, allergy, preference, region
    sql = """SELECT * FROM foods WHERE 1=1"""
    params = []

    if disease and disease != 'None':
        sql += " AND (suitable_disease=%s OR suitable_disease='All' OR suitable_disease='None')"
        params.append(disease)
    
    if food_preference:
        sql += " AND (food_preference=%s OR food_preference='All' OR food_preference='')"
        params.append(food_preference)
    
    if region:
        sql += " AND (region=%s OR region='All' OR region='')"
        params.append(region)

    sql += " ORDER BY food_name"

    cursor.execute(sql, params)
    foods = cursor.fetchall()

    # ✅ FIX: Remove foods that contain allergies
    if allergies:
        allergy_list = [a.strip() for a in allergies.split(',') if a.strip()]
        filtered_foods = []
        for food in foods:
            # Check if food contains any allergy
            food_name = food.get('food_name', '').lower()
            has_allergy = False
            for allergy in allergy_list:
                if allergy.lower() in food_name:
                    has_allergy = True
                    break
            if not has_allergy:
                filtered_foods.append(food)
        foods = filtered_foods

    conn.close()
    return render_template('recommendations.html', foods=foods, profile=profile)
# =========================================================
# MEAL PLANNER
# =========================================================
@app.route('/meal-planner')
@login_required
def meal_planner():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT * FROM health_profiles 
           WHERE user_id=%s ORDER BY id DESC LIMIT 1""",
        (session['user_id'],)
    )
    profile = cursor.fetchone()
    conn.close()

    if not profile:
        flash('Please complete your health profile first', 'warning')
        return redirect('/health-profile')

    disease = profile.get('diseases', '').lower()
    goal = profile.get('goal', '').lower()
    lifestyle = profile.get('lifestyle', '')
    food_preference = profile.get('food_preference', '')
    activity_level = profile.get('activity_level', 'Sedentary')

    # ✅ FIX: Customize based on lifestyle
    lifestyle_meals = {
        'College Student': {
            'breakfast': 'Quick oats with fruits (5 min prep)',
            'lunch': 'Sandwich with salad',
            'snacks': 'Energy bars or fruits',
            'dinner': 'Simple dal rice or pasta',
            'exercise': 'Walk to college + 20 min workout'
        },
        'Working Professional': {
            'breakfast': 'Smoothie or eggs with toast',
            'lunch': 'Meal prep rice/chicken/veggies',
            'snacks': 'Nuts and green tea',
            'dinner': 'Light dinner - soup or salad',
            'exercise': '30 min gym or yoga'
        },
        'Night Shift Employee': {
            'breakfast': 'Heavy breakfast - oats/eggs',
            'lunch': 'Light lunch - salad/fruits',
            'snacks': 'Protein shake',
            'dinner': 'Main meal - rice/chapati with veg',
            'exercise': '10 min stretching'
        },
        'Traveler': {
            'breakfast': 'Fruits and nuts',
            'lunch': 'Local healthy options',
            'snacks': 'Trail mix',
            'dinner': 'Light dinner - soup/salad',
            'exercise': 'Walking'
        },
        'Homemaker': {
            'breakfast': 'Traditional breakfast - idli/dosa',
            'lunch': 'Full meal - rice with veg/chicken',
            'snacks': 'Fruits or sprouts',
            'dinner': 'Light dinner - chapati with dal',
            'exercise': '30 min walking'
        },
        'Senior Citizen': {
            'breakfast': 'Soft foods - porridge/upma',
            'lunch': 'Easy to digest - rice with dal',
            'snacks': 'Fruits',
            'dinner': 'Light - soup or khichdi',
            'exercise': 'Walking + light stretching'
        }
    }

    # ✅ FIX: Customize based on food preference
    preference_meals = {
        'Vegetarian': {
            'protein': 'Paneer, Tofu, Lentils, Beans',
            'avoid': 'None - Vegetarian'
        },
        'Vegan': {
            'protein': 'Tofu, Lentils, Chickpeas, Nuts',
            'avoid': 'Dairy, Eggs, Meat'
        },
        'Non Vegetarian': {
            'protein': 'Chicken, Fish, Eggs, Meat',
            'avoid': 'None'
        },
        'Keto': {
            'protein': 'Meat, Eggs, Cheese',
            'avoid': 'Carbs, Sugar, Grains'
        },
        'Low Carb': {
            'protein': 'Meat, Fish, Eggs, Tofu',
            'avoid': 'Rice, Bread, Sugar'
        },
        'High Protein': {
            'protein': 'Chicken, Eggs, Paneer, Protein Shake',
            'avoid': 'Junk food, Sugar'
        }
    }

    # ✅ FIX: Customize based on activity level
    activity_calories = {
        'Sedentary': '2000-2200 kcal',
        'Lightly Active': '2200-2400 kcal',
        'Moderately Active': '2400-2600 kcal',
        'Very Active': '2600-2800 kcal',
        'Extremely Active': '2800-3000 kcal'
    }

    # Get lifestyle meal plan
    lifestyle_plan = lifestyle_meals.get(lifestyle, lifestyle_meals['Working Professional'])
    
    # Get preference info
    preference_info = preference_meals.get(food_preference, preference_meals['Vegetarian'])

    # Default meal plan
    meal_plan = {
        'breakfast': 'Oats with fruits and nuts',
        'lunch': 'Brown rice with vegetables and dal',
        'snacks': 'Handful of almonds and green tea',
        'dinner': 'Whole wheat chapati with vegetable curry',
        'water': '2.5-3 Litres',
        'exercise': '30 minutes walking or light exercise',
        'foods_to_avoid': 'Sugar, processed foods, soft drinks',
        'protein_sources': 'Lentils, Paneer, Eggs',
        'calories': '2200-2400 kcal'
    }

    # Apply lifestyle plan
    if lifestyle_plan:
        meal_plan['breakfast'] = lifestyle_plan.get('breakfast', meal_plan['breakfast'])
        meal_plan['lunch'] = lifestyle_plan.get('lunch', meal_plan['lunch'])
        meal_plan['snacks'] = lifestyle_plan.get('snacks', meal_plan['snacks'])
        meal_plan['dinner'] = lifestyle_plan.get('dinner', meal_plan['dinner'])
        meal_plan['exercise'] = lifestyle_plan.get('exercise', meal_plan['exercise'])

    # Apply preference
    meal_plan['protein_sources'] = preference_info.get('protein', meal_plan['protein_sources'])
    if preference_info.get('avoid'):
        meal_plan['foods_to_avoid'] = preference_info.get('avoid')

    # Apply activity level calories
    meal_plan['calories'] = activity_calories.get(activity_level, '2200-2400 kcal')

    # Customize based on disease
    if 'diabetes' in disease:
        meal_plan.update({
            'breakfast': 'Ragi dosa with chutney or millet porridge',
            'lunch': 'Brown rice with salads and grilled vegetables',
            'snacks': 'Sprouts with lemon juice',
            'dinner': 'Millet chapati with vegetable curry',
            'foods_to_avoid': 'Sugar, sweets, white rice, processed carbs'
        })
    elif 'heart' in disease:
        meal_plan.update({
            'breakfast': 'Oats with berries and flaxseeds',
            'lunch': 'Quinoa with steamed vegetables',
            'snacks': 'Walnuts and green tea',
            'dinner': 'Fish or paneer with grilled vegetables',
            'foods_to_avoid': 'Fried foods, red meat, excess salt'
        })

    # Customize based on goal
    if 'weight loss' in goal:
        meal_plan.update({
            'breakfast': 'Low-calorie smoothie or egg whites',
            'lunch': 'Large salad with grilled protein',
            'snacks': 'Celery sticks with hummus',
            'dinner': 'Light soup or grilled fish with vegetables'
        })
    elif 'weight gain' in goal or 'muscle gain' in goal:
        meal_plan.update({
            'breakfast': 'Banana shake with peanut butter and oats',
            'lunch': 'Brown rice with chicken or paneer',
            'snacks': 'Peanut butter sandwich or trail mix',
            'dinner': 'Paneer or chicken with whole wheat chapati'
        })

    return render_template(
        'meal_planner.html',
        breakfast=meal_plan['breakfast'],
        lunch=meal_plan['lunch'],
        snacks=meal_plan['snacks'],
        dinner=meal_plan['dinner'],
        water=meal_plan['water'],
        exercise=meal_plan['exercise'],
        foods_to_avoid=meal_plan['foods_to_avoid'],
        protein_sources=meal_plan['protein_sources'],
        calories=meal_plan['calories'],
        lifestyle=lifestyle,
        food_preference=food_preference,
        activity_level=activity_level
    )
# =========================================================
# AI DYNAMIC MEAL PLAN
# =========================================================
# Add this to app.py - replace the existing dynamic_meal_plan function

import datetime
import random

@app.route('/dynamic-meal-plan')
@login_required
def dynamic_meal_plan():
    if model is None:
        flash('ML model not loaded properly', 'danger')
        return redirect('/dashboard')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get LATEST health profile
    cursor.execute(
        """SELECT * FROM health_profiles 
           WHERE user_id=%s ORDER BY id DESC LIMIT 1""",
        (session['user_id'],)
    )
    profile = cursor.fetchone()
    
    cursor.execute(
        """SELECT created_at FROM health_profiles 
           WHERE user_id=%s ORDER BY id DESC LIMIT 1""",
        (session['user_id'],)
    )
    last_updated = cursor.fetchone()
    conn.close()

    if not profile:
        flash('Please complete your health profile first', 'warning')
        return redirect('/health-profile')

    try:
        import datetime
        import random
        
        age = int(profile['age'])
        bmi = float(profile['bmi'])
        disease = profile.get('diseases', 'None') or 'None'
        goal = profile.get('goal', 'Fitness Maintenance') or 'Fitness Maintenance'

        # Split if multiple diseases (take first one)
        if ',' in disease:
            disease = disease.split(',')[0].strip()

        # ✅ DIRECT MAPPING - This is the FIX!
        disease_diet_map = {
            'Diabetes': 'Diabetes Diet',
            'Heart Disease': 'Heart Healthy Diet',
            'PCOS': 'PCOS Diet',
            'Thyroid': 'Thyroid Diet',
            'BP': 'Heart Healthy Diet',
            'Cholesterol': 'Heart Healthy Diet',
            'Kidney Disease': 'Kidney Diet',
            'Anemia': 'High Protein Diet',
            'Gastric/Ulcer': 'Balanced Diet',
        }
        
        goal_diet_map = {
            'Weight Loss': 'Low Calorie Diet',
            'Weight Gain': 'High Protein Diet',
            'Muscle Gain': 'High Protein Diet',
            'Fitness Maintenance': 'Balanced Diet',
            'Athlete Training': 'High Protein Diet'
        }

        # Determine diet type
        if disease in disease_diet_map:
            diet_type = disease_diet_map[disease]
        elif disease == 'None':
            diet_type = goal_diet_map.get(goal, 'Balanced Diet')
        else:
            diet_type = goal_diet_map.get(goal, 'Balanced Diet')

        print(f"📊 User: Disease={disease}, Goal={goal} → Diet={diet_type}")

        # Get foods for the diet type
        conn = get_db_connection()
        cursor = conn.cursor()

        meals = {}
        for meal_type in ['Breakfast', 'Lunch', 'Snacks', 'Dinner']:
            cursor.execute(
                """SELECT * FROM foods 
                   WHERE diet_type=%s AND meal_type=%s""",
                (diet_type, meal_type)
            )
            foods = cursor.fetchall()
            
            if foods:
                today_seed = int(datetime.date.today().strftime("%Y%m%d"))
                shuffle_seed = today_seed + session['user_id']
                shuffled = foods.copy()
                random.Random(shuffle_seed).shuffle(shuffled)
                meals[meal_type.lower()] = shuffled[0]
            else:
                meals[meal_type.lower()] = None

        conn.close()

        return render_template(
            'dynamic_meal_plan.html',
            diet_type=diet_type,
            breakfast=meals.get('breakfast'),
            lunch=meals.get('lunch'),
            snack=meals.get('snacks'),
            dinner=meals.get('dinner'),
            age=age,
            bmi=bmi,
            disease=disease,
            goal=goal,
            last_updated=last_updated['created_at'] if last_updated else None,
            today=datetime.date.today().strftime("%A, %B %d, %Y")
        )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        flash(f'Error generating meal plan: {str(e)}', 'danger')
        return redirect('/dashboard')
# =========================================================
# SMART FOODS (ML Based)
# =========================================================

@app.route('/smart-foods')
@login_required
def smart_foods():
    if model is None:
        flash('ML model not loaded properly', 'danger')
        return redirect('/dashboard')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT * FROM health_profiles 
           WHERE user_id=%s ORDER BY id DESC LIMIT 1""",
        (session['user_id'],)
    )
    profile = cursor.fetchone()
    conn.close()

    if not profile:
        flash('Please complete your health profile first', 'warning')
        return redirect('/health-profile')

    try:
        age = int(profile['age'])
        bmi = float(profile['bmi'])
        disease = profile.get('diseases', 'None') or 'None'
        goal = profile.get('goal', 'Fitness Maintenance') or 'Fitness Maintenance'

        disease_encoded = le_disease.transform([disease])[0] if disease in le_disease.classes_ else 0
        goal_encoded = le_goal.transform([goal])[0] if goal in le_goal.classes_ else 0

        prediction = model.predict([[age, bmi, disease_encoded, goal_encoded]])
        diet_type = le_diet.inverse_transform(prediction)[0]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM foods WHERE diet_type=%s OR suitable_disease=%s",
            (diet_type, disease)
        )
        foods = cursor.fetchall()
        conn.close()

        return render_template('smart_foods.html', foods=foods, diet_type=diet_type)

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect('/dashboard')

# =========================================================
# NUTRITION CHATBOT
# =========================================================

@app.route('/nutrition-chatbot')
@login_required
def nutrition_chatbot():
    return render_template('nutrition_chatbot.html', answer=None)

@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    question = request.form.get('question', '').strip()
    if not question:
        flash('Please enter a question', 'warning')
        return redirect('/nutrition-chatbot')

    q = question.lower()

    # Intelligent response system
    if any(word in q for word in ['diabetes', 'blood sugar', 'sugar level']):
        answer = """📋 **Dietary Tips for Diabetes:**
• Choose low glycemic index foods like ragi, millet, and oats
• Eat small, frequent meals to maintain blood sugar levels
• Include plenty of fiber-rich vegetables
• Avoid refined sugar, white rice, and processed foods
• Stay hydrated with at least 8 glasses of water daily
• Monitor portion sizes carefully"""

    elif any(word in q for word in ['weight loss', 'lose weight', 'fat loss']):
        answer = """📋 **Weight Loss Tips:**
• Create a calorie deficit of 300-500 calories daily
• Choose protein-rich foods to stay full longer
• Include fruits and vegetables in every meal
• Avoid sugary drinks and processed foods
• Exercise 30-45 minutes daily
• Stay consistent with your routine"""

    elif any(word in q for word in ['protein', 'protein rich', 'high protein']):
        answer = """📋 **High Protein Foods:**
• Lean meats: Chicken, turkey, fish
• Plant-based: Lentils, chickpeas, tofu, soy
• Dairy: Paneer, Greek yogurt, cheese
• Eggs and egg whites
• Nuts and seeds: Almonds, walnuts, pumpkin seeds
• Protein shakes and supplements"""

    elif any(word in q for word in ['thyroid', 'hypothyroid', 'hyperthyroid']):
        answer = """📋 **Thyroid Management Tips:**
• Consume iodine-rich foods like seaweed and fish
• Include selenium-rich foods like Brazil nuts
• Avoid goitrogens like raw cabbage, broccoli in excess
• Eat regular, balanced meals
• Limit processed and sugary foods
• Stay consistent with medication if prescribed"""

    elif any(word in q for word in ['heart', 'cardiac', 'cholesterol']):
        answer = """📋 **Heart Health Diet:**
• Choose healthy fats from nuts, avocados, olive oil
• Eat fish rich in omega-3 (salmon, mackerel)
• Include plenty of leafy green vegetables
• Choose whole grains over refined
• Limit sodium and processed foods
• Avoid trans fats and fried foods"""

    elif any(word in q for word in ['pcos', 'pcod', 'hormonal']):
        answer = """📋 **PCOS Management Tips:**
• Choose low glycemic index foods
• Include anti-inflammatory foods like turmeric
• Eat regular meals to balance blood sugar
• Choose healthy fats and proteins
• Limit dairy and sugar intake
• Stay physically active"""

    elif any(word in q for word in ['water', 'hydrate', 'hydration']):
        answer = """📋 **Hydration Guidelines:**
• Drink 8-10 glasses of water daily
• Increase water intake during exercise
• Include hydrating foods like watermelon, cucumber
• Avoid sugary drinks and sodas
• Drink water 30 minutes before meals"""

    else:
        answer = """📋 **General Nutrition Advice:**
• Eat a balanced diet with all food groups
• Include plenty of fruits and vegetables
• Stay hydrated with adequate water
• Exercise regularly for overall health
• Get 7-8 hours of quality sleep
• Consult a nutritionist for personalized advice"""

    # Save to history
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chatbot_history (user_id, question, answer) VALUES (%s,%s,%s)",
        (session['user_id'], question, answer)
    )
    conn.close()

    return render_template('nutrition_chatbot.html', answer=answer, question=question)

# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE email=%s", (email,))
        admin = cursor.fetchone()
        conn.close()

        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['fullname']
            flash('Admin login successful', 'success')
            return redirect('/admin-dashboard')
        else:
            flash('Invalid admin credentials', 'danger')
            return render_template('admin_login.html')

    return render_template('admin_login.html')

# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route('/admin-dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM diseases ORDER BY disease_name")
    diseases = cursor.fetchall()

    cursor.execute("SELECT * FROM allergies ORDER BY allergy_name")
    allergies = cursor.fetchall()

    cursor.execute("SELECT * FROM regions ORDER BY main_region, sub_region")
    regions = cursor.fetchall()

    cursor.execute("SELECT * FROM foods ORDER BY food_name")
    foods = cursor.fetchall()

    cursor.execute("SELECT * FROM meal_plans ORDER BY meal_name")
    mealplans = cursor.fetchall()

    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()

    conn.close()

    return render_template(
        'admin_dashboard.html',
        diseases=diseases,
        allergies=allergies,
        regions=regions,
        foods=foods,
        mealplans=mealplans,
        users=users
    )

# =========================================================
# ADMIN CRUD OPERATIONS
# =========================================================

@app.route('/add-disease', methods=['POST'])
@admin_required
def add_disease():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO diseases (disease_name, description, foods_to_eat, foods_to_avoid) VALUES (%s,%s,%s,%s)",
        (request.form['disease_name'], request.form['description'], 
         request.form['foods_to_eat'], request.form['foods_to_avoid'])
    )
    conn.close()
    flash('Disease added successfully', 'success')
    return redirect('/admin-dashboard')

@app.route('/delete-disease/<int:id>')
@admin_required
def delete_disease(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diseases WHERE id=%s", (id,))
    conn.close()
    flash('Disease deleted', 'success')
    return redirect('/admin-dashboard')

@app.route('/add-allergy', methods=['POST'])
@admin_required
def add_allergy():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO allergies (allergy_name, description) VALUES (%s,%s)",
        (request.form['allergy_name'], request.form['description'])
    )
    conn.close()
    flash('Allergy added successfully', 'success')
    return redirect('/admin-dashboard')

@app.route('/delete-allergy/<int:id>')
@admin_required
def delete_allergy(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM allergies WHERE id=%s", (id,))
    conn.close()
    flash('Allergy deleted', 'success')
    return redirect('/admin-dashboard')

@app.route('/add-region', methods=['POST'])
@admin_required
def add_region():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO regions (main_region, sub_region) VALUES (%s,%s)",
        (request.form['main_region'], request.form['sub_region'])
    )
    conn.close()
    flash('Region added successfully', 'success')
    return redirect('/admin-dashboard')

@app.route('/delete-region/<int:id>')
@admin_required
def delete_region(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM regions WHERE id=%s", (id,))
    conn.close()
    flash('Region deleted', 'success')
    return redirect('/admin-dashboard')

@app.route('/add-food', methods=['POST'])
@admin_required
def add_food():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO foods 
           (food_name, calories, protein, carbs, fat, fiber, 
            food_category, suitable_disease, region, image, diet_type, meal_type)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (request.form['food_name'], request.form['calories'], 
         request.form['protein'], request.form['carbs'], 
         request.form['fat'], request.form['fiber'],
         request.form['food_category'], request.form['suitable_disease'],
         request.form['region'], request.form.get('image', ''),
         request.form.get('diet_type', ''), request.form.get('meal_type', ''))
    )
    conn.close()
    flash('Food added successfully', 'success')
    return redirect('/admin-dashboard')

@app.route('/delete-food/<int:id>')
@admin_required
def delete_food(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM foods WHERE id=%s", (id,))
    conn.close()
    flash('Food deleted', 'success')
    return redirect('/admin-dashboard')

@app.route('/add-mealplan', methods=['POST'])
@admin_required
def add_mealplan():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO meal_plans 
           (meal_name, breakfast, lunch, dinner, snacks, target_goal, disease)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (request.form['meal_name'], request.form['breakfast'],
         request.form['lunch'], request.form['dinner'],
         request.form['snacks'], request.form['target_goal'],
         request.form['disease'])
    )
    conn.close()
    flash('Meal plan added successfully', 'success')
    return redirect('/admin-dashboard')

@app.route('/delete-mealplan/<int:id>')
@admin_required
def delete_mealplan(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meal_plans WHERE id=%s", (id,))
    conn.close()
    flash('Meal plan deleted', 'success')
    return redirect('/admin-dashboard')


# =========================================================
#visualization
#==========================================================
from visualization import *

# ============================================================
# 👤 USER ANALYTICS
# ============================================================

@app.route('/user-analytics')
@login_required
def user_analytics():
    """User's personal analytics dashboard"""
    user_id = session['user_id']
    
    bmi_chart = generate_user_bmi_progress(user_id)
    calorie_chart = generate_user_calorie_breakdown(user_id)
    nutrition_chart = generate_user_nutrition_summary(user_id)
    
    return render_template(
        'user_analytics.html',
        bmi_chart=bmi_chart,
        calorie_chart=calorie_chart,
        nutrition_chart=nutrition_chart
    )

# ============================================================
# 👨‍💼 ADMIN ANALYTICS
# ============================================================

@app.route('/admin-analytics')
@admin_required
def admin_analytics():
    """Admin analytics dashboard"""
    growth_chart = generate_admin_user_growth()
    stats_chart = generate_admin_platform_stats()
    disease_chart = generate_admin_disease_distribution()
    goal_chart = generate_admin_goal_distribution()
    activity_chart = generate_admin_activity_distribution()
    
    return render_template(
        'admin_analytics.html',
        growth_chart=growth_chart,
        stats_chart=stats_chart,
        disease_chart=disease_chart,
        goal_chart=goal_chart,
        activity_chart=activity_chart
    )
# =========================================================
# LOGOUT
# =========================================================

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect('/login')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Admin logged out', 'success')
    return redirect('/admin-login')

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == '__main__':
    # Ensure ML directory exists
    os.makedirs('ml', exist_ok=True)
    
    # Check if models exist, if not train them
    if not os.path.exists('ml/diet_model.pkl'):
        print("ML models not found. Please run train_model.py first!")
        print("Run: python train_model.py")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta
import os
import time
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# MongoDB connection
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv://vammy:admin@cluster0.ga34sgo.mongodb.net/donordb')
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    db = client.donordb
    print("MongoDB connection successful!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    print("Falling back to local MongoDB or check your connection...")
    # Fallback to local MongoDB if available
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.donordb
        print("Connected to local MongoDB!")
    except Exception as local_e:
        print(f"Local MongoDB also failed: {local_e}")
        print("Please check your MongoDB connection or start local MongoDB service")
        exit(1)

print("MP")
#print("abc")
# Collections
users = db.users
campaigns = db.campaigns
donations = db.donations

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

# Don't set the JSON encoder for now as it might be causing issues
# app.json_encoder = JSONEncoder

# Helper functions
def create_user(username, email, password, is_admin=False):
    user_doc = {
        'username': username,
        'email': email,
        'password_hash': generate_password_hash(password),
        'is_admin': is_admin,
        'created_at': datetime.utcnow()
    }
    result = users.insert_one(user_doc)
    return result.inserted_id

def get_user_by_username(username):
    return users.find_one({'username': username})

def get_user_by_id(user_id):
    return users.find_one({'_id': ObjectId(user_id)})

def check_password(password_hash, password):
    return check_password_hash(password_hash, password)

def create_campaign(title, description, goal_amount, creator_id, end_date=None):
    campaign_doc = {
        'title': title,
        'description': description,
        'goal_amount': float(goal_amount),
        'current_amount': 0.0,
        'is_active': True,
        'created_at': datetime.utcnow(),
        'end_date': end_date,
        'creator_id': ObjectId(creator_id)
    }
    result = campaigns.insert_one(campaign_doc)
    return result.inserted_id

def get_campaigns(is_active=None):
    query = {}
    if is_active is not None:
        query['is_active'] = is_active
    return list(campaigns.find(query).sort('created_at', -1))

def get_campaign_by_id(campaign_id):
    try:
        # Try to find by ObjectId first (for real campaigns)
        if isinstance(campaign_id, str) and len(campaign_id) == 24:
            return campaigns.find_one({'_id': ObjectId(campaign_id)})
        else:
            # For sample campaigns or invalid IDs, return None
            return None
    except Exception as e:
        print(f"Error getting campaign by ID {campaign_id}: {e}")
        return None

def create_donation(amount, message, is_anonymous, donor_id, campaign_id):
    donation_doc = {
        'amount': float(amount),
        'message': message,
        'is_anonymous': is_anonymous,
        'created_at': datetime.utcnow(),
        'donor_id': ObjectId(donor_id),
        'campaign_id': ObjectId(campaign_id)
    }
    
    # Insert donation
    result = donations.insert_one(donation_doc)
    
    # Update campaign total
    campaigns.update_one(
        {'_id': ObjectId(campaign_id)},
        {'$inc': {'current_amount': float(amount)}}
    )
    
    return result.inserted_id

def get_donations_by_campaign(campaign_id, limit=None):
    query = {'campaign_id': ObjectId(campaign_id)}
    cursor = donations.find(query).sort('created_at', -1)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)

def get_donations_by_user(user_id):
    return list(donations.find({'donor_id': ObjectId(user_id)}).sort('created_at', -1))

def get_campaigns_by_user(user_id):
    return list(campaigns.find({'creator_id': ObjectId(user_id)}).sort('created_at', -1))

def calculate_progress_percentage(current_amount, goal_amount):
    if goal_amount > 0:
        return min(100, (current_amount / goal_amount) * 100)
    return 0

# Routes
@app.route('/test')
def test():
    return "Flask app is working!"

@app.route('/')
def home():
    """Home page with featured campaigns"""
    try:
        print("Attempting to get campaigns...")
        featured_campaigns = get_campaigns(is_active=True)[:3]
        print(f"Found {len(featured_campaigns)} campaigns from database")
        
        # Add creator info and progress to each campaign
        for i, campaign in enumerate(featured_campaigns):
            print(f"Processing campaign {i}: {campaign.get('title', 'Unknown')}")
            creator = get_user_by_id(campaign['creator_id'])
            campaign['creator'] = creator if creator else {'username': 'Unknown'}
            campaign['progress_percentage'] = calculate_progress_percentage(
                campaign['current_amount'], campaign['goal_amount']
            )
            print(f"Campaign {i} processed successfully")
        
        print("Rendering template...")
        return render_template('home.html', campaigns=featured_campaigns)
    except Exception as e:
        print(f"Error in home route: {e}")
        # Create sample campaigns for testing when database is unavailable
        sample_campaigns = [
            {
                '_id': '1',
                'title': 'Help Build Clean Water Wells',
                'description': 'Providing clean water access to rural communities.',
                'goal_amount': 10000.0,
                'current_amount': 6500.0,
                'creator': {'username': 'WaterForAll'},
                'progress_percentage': 65,
                'is_active': True
            },
            {
                '_id': '2', 
                'title': 'Education for Underprivileged Children',
                'description': 'Supporting education initiatives for children in need.',
                'goal_amount': 5000.0,
                'current_amount': 2300.0,
                'creator': {'username': 'EduCare'},
                'progress_percentage': 46,
                'is_active': True
            },
            {
                '_id': '3',
                'title': 'Medical Equipment for Rural Clinic',
                'description': 'Funding essential medical equipment for a remote clinic.',
                'goal_amount': 15000.0,
                'current_amount': 8900.0,
                'creator': {'username': 'HealthFirst'},
                'progress_percentage': 59,
                'is_active': True
            }
        ]
        print("Using sample campaigns for demo")
        return render_template('home.html', campaigns=sample_campaigns)

@app.route('/campaigns')
def campaigns_page():
    """Browse all active campaigns"""
    try:
        print("Accessing campaigns route...")
        all_campaigns = get_campaigns(is_active=True)
        print(f"Found {len(all_campaigns)} campaigns")
        
        # Add creator info and progress to each campaign
        for i, campaign in enumerate(all_campaigns):
            print(f"Processing campaign {i+1}: {campaign.get('title', 'No title')}")
            try:
                creator = get_user_by_id(campaign['creator_id'])
                campaign['creator'] = creator
                campaign['progress_percentage'] = calculate_progress_percentage(
                    campaign['current_amount'], campaign['goal_amount']
                )
                campaign['donations'] = get_donations_by_campaign(campaign['_id'])
            except Exception as ce:
                print(f"Error processing campaign {i+1}: {ce}")
                # Set defaults to prevent template errors
                campaign['creator'] = {'name': 'Unknown'}
                campaign['progress_percentage'] = 0
                campaign['donations'] = []
        
        print("Rendering campaigns template...")
        return render_template('campaigns.html', campaigns=all_campaigns)
    except Exception as e:
        print(f"Error in campaigns route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500
        # Return sample campaigns for demo
        sample_campaigns = [
            {
                '_id': '1',
                'title': 'Help Build Clean Water Wells',
                'description': 'Providing clean water access to rural communities in remote areas where people have to walk miles to get drinking water.',
                'goal_amount': 10000.0,
                'current_amount': 6500.0,
                'creator': {'username': 'WaterForAll'},
                'progress_percentage': 65,
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                '_id': '2', 
                'title': 'Education for Underprivileged Children',
                'description': 'Supporting education initiatives for children in need by providing school supplies, books, and learning materials.',
                'goal_amount': 5000.0,
                'current_amount': 2300.0,
                'creator': {'username': 'EduCare'},
                'progress_percentage': 46,
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                '_id': '3',
                'title': 'Medical Equipment for Rural Clinic',
                'description': 'Funding essential medical equipment for a remote clinic that serves thousands of patients in underserved communities.',
                'goal_amount': 15000.0,
                'current_amount': 8900.0,
                'creator': {'username': 'HealthFirst'},
                'progress_percentage': 59,
                'is_active': True,
                'created_at': datetime.utcnow()
            }
        ]
        return render_template('campaigns.html', campaigns=sample_campaigns)

@app.route('/campaign/<campaign_id>')
def campaign_detail(campaign_id):
    """Campaign detail page with donation form"""
    try:
        campaign = get_campaign_by_id(campaign_id)
        
        # If no campaign found and it's a sample ID, provide sample data
        if not campaign and campaign_id in ['1', '2', '3']:
            sample_campaigns = {
                '1': {
                    '_id': '1',
                    'title': 'Help Build Clean Water Wells',
                    'description': 'Join us in our mission to provide clean, safe drinking water to rural communities. Your donation will help us build wells, install water purification systems, and train local communities in water maintenance. Every dollar makes a difference in transforming lives.',
                    'goal_amount': 10000.0,
                    'current_amount': 6500.0,
                    'creator_id': 'sample_user',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                '2': {
                    '_id': '2',
                    'title': 'Education for Underprivileged Children',
                    'description': 'Help us provide quality education to children who need it most. Your support will fund school supplies, teacher training, and educational programs that give these children a brighter future.',
                    'goal_amount': 5000.0,
                    'current_amount': 2300.0,
                    'creator_id': 'sample_user',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                },
                '3': {
                    '_id': '3',
                    'title': 'Emergency Medical Relief Fund',
                    'description': 'Support emergency medical care for families in crisis. Your donation provides life-saving medical treatments, hospital care, and emergency surgery for those who cannot afford it.',
                    'goal_amount': 15000.0,
                    'current_amount': 8200.0,
                    'creator_id': 'sample_user',
                    'is_active': True,
                    'created_at': datetime.utcnow()
                }
            }
            campaign = sample_campaigns.get(campaign_id)
            
        if not campaign:
            return "Campaign not found", 404
        
        # Handle creator info for both real and sample campaigns
        if campaign.get('creator_id') == 'sample_user':
            campaign['creator'] = {'username': 'DonationTracker', 'email': 'demo@donationtracker.com'}
        else:
            creator = get_user_by_id(campaign['creator_id'])
            campaign['creator'] = creator if creator else {'username': 'Unknown'}
            
        campaign['progress_percentage'] = calculate_progress_percentage(
            campaign['current_amount'], campaign['goal_amount']
        )
        
        # Handle donations for both real and sample campaigns
        if campaign_id in ['1', '2', '3']:
            # Sample donations for demo campaigns
            recent_donations = [
                {
                    'amount': 100.0,
                    'message': 'Great cause! Happy to help.',
                    'is_anonymous': False,
                    'created_at': datetime.utcnow(),
                    'donor': {'username': 'GenerousHelper'}
                },
                {
                    'amount': 50.0,
                    'message': 'Every bit counts!',
                    'is_anonymous': True,
                    'created_at': datetime.utcnow()
                }
            ]
            campaign['donations'] = recent_donations
        else:
            recent_donations = get_donations_by_campaign(campaign_id, limit=5)
            
            # Add donor info to donations
            for donation in recent_donations:
                if not donation['is_anonymous']:
                    donor = get_user_by_id(donation['donor_id'])
                    donation['donor'] = donor
            
            campaign['donations'] = get_donations_by_campaign(campaign_id)
        
        return render_template('campaign_detail.html', campaign=campaign, donations=campaign['donations'])
    except Exception as e:
        return "Invalid campaign ID", 400

@app.route('/dashboard')
def dashboard():
    """User dashboard to view their donations and campaigns"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    user_donations = get_donations_by_user(session['user_id'])
    user_campaigns = get_campaigns_by_user(session['user_id'])
    
    # Add campaign info to donations
    for donation in user_donations:
        campaign = get_campaign_by_id(donation['campaign_id'])
        donation['campaign'] = campaign
    
    # Add progress info to campaigns
    for campaign in user_campaigns:
        campaign['progress_percentage'] = calculate_progress_percentage(
            campaign['current_amount'], campaign['goal_amount']
        )
        campaign['donations'] = get_donations_by_campaign(campaign['_id'])
    
    return render_template('dashboard.html', user=user, donations=user_donations, campaigns=user_campaigns)

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard to manage all campaigns"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user or not user.get('is_admin'):
        return redirect(url_for('home'))
    
    all_campaigns = list(campaigns.find().sort('created_at', -1))
    all_donations = list(donations.find().sort('created_at', -1).limit(10))
    
    # Add creator and progress info to campaigns
    for campaign in all_campaigns:
        creator = get_user_by_id(campaign['creator_id'])
        campaign['creator'] = creator
        campaign['progress_percentage'] = calculate_progress_percentage(
            campaign['current_amount'], campaign['goal_amount']
        )
        campaign['donations'] = get_donations_by_campaign(campaign['_id'])
    
    # Add donor and campaign info to donations
    for donation in all_donations:
        donor = get_user_by_id(donation['donor_id'])
        campaign = get_campaign_by_id(donation['campaign_id'])
        donation['donor'] = donor
        donation['campaign'] = campaign
    
    return render_template('admin_dashboard.html', campaigns=all_campaigns, donations=all_donations)

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if get_user_by_username(username):
            return jsonify({'error': 'Username already exists'}), 400
        
        if users.find_one({'email': email}):
            return jsonify({'error': 'Email already exists'}), 400
        
        user_id = create_user(username, email, password)
        
        if request.is_json:
            return jsonify({'message': 'User created successfully'}), 201
        else:
            session['user_id'] = str(user_id)
            return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        
        user = get_user_by_username(username)
        
        if user and check_password(user['password_hash'], password):
            session['user_id'] = str(user['_id'])
            
            if request.is_json:
                access_token = create_access_token(identity=str(user['_id']))
                return jsonify({
                    'access_token': access_token,
                    'user': {
                        'id': str(user['_id']),
                        'username': user['username'],
                        'email': user['email'],
                        'is_admin': user.get('is_admin', False)
                    }
                }), 200
            else:
                return redirect(url_for('dashboard'))
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

# API routes for donations
@app.route('/api/donate', methods=['POST'])
def make_donation():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    campaign_id = data.get('campaign_id')
    amount = data.get('amount')
    message = data.get('message', '')
    is_anonymous = data.get('is_anonymous', False)
    
    # Handle sample campaigns differently
    if campaign_id in ['1', '2', '3']:
        # For demo campaigns, just return success without database storage
        return jsonify({
            'message': 'Donation successful',
            'donation_id': f'demo_{campaign_id}_{int(time.time())}',
            'note': 'This is a demo donation to a sample campaign'
        }), 201
    
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    donation_id = create_donation(
        amount=amount,
        message=message,
        is_anonymous=is_anonymous,
        donor_id=session['user_id'],
        campaign_id=campaign_id
    )
    
    return jsonify({
        'message': 'Donation successful',
        'donation_id': str(donation_id)
    }), 201

@app.route('/api/campaigns', methods=['POST'])
def create_campaign_route():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    
    end_date = None
    if data.get('end_date'):
        try:
            end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        except ValueError:
            pass
    
    campaign_id = create_campaign(
        title=data.get('title'),
        description=data.get('description'),
        goal_amount=data.get('goal_amount'),
        creator_id=session['user_id'],
        end_date=end_date
    )
    
    return jsonify({
        'message': 'Campaign created successfully',
        'campaign_id': str(campaign_id)
    }), 201

# Initialize database
def initialize_database():
    """Initialize database with admin user"""
    try:
        # Test MongoDB connection first
        client.admin.command('ping')
        print("Database connection verified!")
        
        # Check if admin user exists
        admin = get_user_by_username('admin')
        if not admin:
            admin_id = create_user('admin', 'admin@donation-tracker.com', 'admin123', is_admin=True)
            print(f"Admin user created with ID: {admin_id}")
        else:
            print("Admin user already exists")
            
        # Create indexes for better performance (handle duplicate key errors)
        try:
            users.create_index("username", unique=True)
            users.create_index("email", unique=True)
        except Exception:
            pass  # Index might already exist
            
        try:
            campaigns.create_index("creator_id")
            campaigns.create_index("is_active")
            donations.create_index("donor_id")
            donations.create_index("campaign_id")
        except Exception:
            pass  # Indexes might already exist
        
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Please check your MongoDB connection")

if __name__ == '__main__':
    initialize_database()
    app.run(host='127.0.0.1', port=5005, debug=False)
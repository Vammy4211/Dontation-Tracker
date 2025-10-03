# 🎯 Donation Tracker - Design Patterns Implementation

A comprehensive donation management system built with Flask that demonstrates **8+ design patterns** in a real-world application. This project showcases modern web development practices, clean architecture, and object-oriented programming principles.

## 🌟 Features

### Core Functionality
- **User Management**: Registration, authentication, and profile management
- **Campaign Management**: Create, update, and manage fundraising campaigns
- **Donation Processing**: Multiple payment methods with secure transaction handling
- **Administrative Dashboard**: System analytics and user management
- **Real-time Notifications**: Event-driven updates and notifications

### Technical Excellence
- **8+ Design Patterns**: Factory, Singleton, Repository, Strategy, Observer, Facade, Proxy, Chain of Responsibility
- **Modern UI/UX**: Bootstrap 5.3.0 with accessibility features and responsive design
- **Comprehensive API**: RESTful endpoints with Postman collection and documentation
- **Robust Testing**: pytest framework with pattern-specific test suites
- **Clean Architecture**: Modular code organization with Flask Blueprints

## 🏗️ Design Patterns Implemented

### 1. Factory Pattern 🏭
**Location**: `app/services/user_factory.py`
```python
class UserFactory:
    @staticmethod
    def create_user(user_type: str, user_data: dict) -> User:
        if user_type == 'donor':
            return Donor(**user_data)
        elif user_type == 'admin':
            return Admin(**user_data)
        else:
            raise ValueError(f"Unknown user type: {user_type}")
```
**Benefits**: Centralized user creation, easy extension, follows Open/Closed Principle

### 2. Singleton Pattern 🔒
**Location**: `app/services/database_manager.py`
```python
class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```
**Benefits**: Single database connection, thread-safe, resource management

### 3. Repository Pattern 📊
**Location**: `app/services/repositories.py`
```python
class CampaignRepository(BaseRepository):
    def find_all(self, filters=None, sort_by=None, limit=None):
        # Implementation with MongoDB operations
        pass
```
**Benefits**: Data access abstraction, testability, database independence

### 4. Strategy Pattern 🎯
**Location**: `app/services/strategy.py`
```python
class SortByAmountStrategy(SortingStrategy):
    def sort(self, campaigns: List[Campaign], reverse: bool = False) -> List[Campaign]:
        return sorted(campaigns, key=lambda c: c.current_amount, reverse=reverse)
```
**Benefits**: Interchangeable algorithms, runtime strategy selection, extensible

### 5. Observer Pattern 👁️
**Location**: `app/services/observer.py`
- Event notifications for campaign updates
- Real-time donation tracking
- User activity monitoring

### 6. Facade Pattern 🎭
**Location**: `app/services/facade.py`
- Simplified API interfaces
- Complex operation orchestration
- Clean client interactions

### 7. Proxy Pattern 🛡️
**Location**: `app/services/proxy.py`
- Authentication and authorization
- Caching layer implementation
- Access control management

### 8. Chain of Responsibility Pattern ⛓️
**Location**: `app/services/chain_of_responsibility.py`
- Request processing pipeline
- Validation chain
- Authorization workflows

## 🏛️ Project Architecture

```
donation-tracker/
├── app/
│   ├── blueprints/          # Flask Blueprints for modular routing
│   │   ├── auth.py          # Authentication routes
│   │   └── main.py          # Main application routes
│   ├── models/              # Data models with OOP hierarchy
│   │   ├── user.py          # Abstract User base class
│   │   ├── donor.py         # Donor user implementation
│   │   ├── admin.py         # Admin user implementation
│   │   ├── campaign.py      # Campaign model
│   │   └── donation.py      # Donation model
│   └── services/            # Design pattern implementations
│       ├── user_factory.py  # Factory Pattern
│       ├── database_manager.py # Singleton Pattern
│       ├── repositories.py  # Repository Pattern
│       ├── strategy.py      # Strategy Pattern
│       ├── observer.py      # Observer Pattern
│       ├── facade.py        # Facade Pattern
│       ├── proxy.py         # Proxy Pattern
│       └── chain_of_responsibility.py # Chain of Responsibility
├── static/                  # CSS, JavaScript, images
├── templates/               # Jinja2 HTML templates
├── tests/                   # Comprehensive test suite
├── postman/                 # API collection and documentation
└── instance/                # Configuration files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Node.js (for frontend dependencies)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd donation-tracker
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up MongoDB**
```bash
# Make sure MongoDB is running
mongod
```

6. **Initialize the database**
```bash
python app.py
# The application will create the database and collections automatically
```

7. **Start the application**
```bash
python app.py
```

The application will be available at `http://localhost:5005`

### Environment Configuration

Create a `.env` file with the following variables:

```bash
# Database Configuration
MONGO_URI=mongodb://localhost:27017/donation_tracker
DB_NAME=donation_tracker

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRES=86400

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

## 🖥️ User Interface

### Modern Design Features
- **Bootstrap 5.3.0**: Latest responsive framework
- **Accessibility**: ARIA labels, semantic HTML, keyboard navigation
- **Dark/Light Mode**: Theme switching capability
- **Mobile-First**: Responsive design for all devices
- **Performance**: Optimized loading and smooth interactions

### Key Pages
- **Home**: Hero section with featured campaigns and statistics
- **Campaigns**: Interactive campaign browser with search and filters
- **Donation**: Multi-step donation process with payment options
- **Profile**: User dashboard with donation history
- **Admin**: Administrative panel for system management

## 🔧 API Documentation

### RESTful Endpoints

| Method | Endpoint | Description | Design Pattern |
|--------|----------|-------------|----------------|
| POST | `/api/auth/register` | User registration | Factory Pattern |
| POST | `/api/auth/login` | User authentication | Singleton Pattern |
| GET | `/api/campaigns` | List campaigns | Repository + Strategy |
| POST | `/api/campaigns` | Create campaign | Repository Pattern |
| POST | `/api/donations` | Process donation | Strategy Pattern |
| GET | `/api/admin/stats` | System statistics | Facade Pattern |

### Postman Collection

Complete API testing suite available in `postman/` directory:
- **25+ endpoints** with request/response examples
- **Automated testing** scripts for validation
- **Environment variables** for different deployment stages
- **Design pattern testing** endpoints for validation

```bash
# Import into Postman
postman/Donation_Tracker_API.postman_collection.json
postman/Donation_Tracker.postman_environment.json
```

## 🧪 Testing

### Test Structure
```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_factory_pattern.py     # Factory pattern validation
├── test_singleton_pattern.py   # Singleton pattern testing
├── test_repository_pattern.py  # Repository pattern verification
├── test_strategy_pattern.py    # Strategy pattern validation
└── run_tests.py                # Test runner with multiple options
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock coverage

# Run all tests
python run_tests.py

# Run specific pattern tests
python run_tests.py --patterns

# Run with coverage
python run_tests.py --coverage

# Run linting
python run_tests.py --lint
```

### Test Features
- **Pattern Validation**: Verify each design pattern implementation
- **Integration Testing**: End-to-end workflow validation
- **Performance Testing**: Load and stress testing capabilities
- **Mock Testing**: Isolated unit testing with mocks

## 📊 Design Pattern Benefits

### Code Quality Improvements
- **Modularity**: Each pattern encapsulates specific responsibilities
- **Maintainability**: Clean separation of concerns
- **Extensibility**: Easy to add new features without breaking existing code
- **Testability**: Patterns enable effective unit testing
- **Reusability**: Pattern implementations can be reused across projects

### Real-World Applications
- **Factory Pattern**: User type management, payment method creation
- **Singleton Pattern**: Database connections, configuration management
- **Repository Pattern**: Data access layer, database abstraction
- **Strategy Pattern**: Sorting algorithms, payment processing
- **Observer Pattern**: Event notifications, real-time updates

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure stateless authentication
- **Password Hashing**: bcrypt with salt rounds
- **Role-Based Access**: Different permissions for donors and admins
- **Session Management**: Token expiration and refresh

### Data Protection
- **Input Validation**: Comprehensive request validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Output sanitization
- **CSRF Protection**: Token-based CSRF prevention

### API Security
- **Rate Limiting**: Prevents API abuse
- **CORS Configuration**: Controlled cross-origin requests
- **Secure Headers**: Security-related HTTP headers
- **Request Logging**: Audit trail for security monitoring

## 🚀 Deployment

### Development Deployment
```bash
# Local development server
python app.py
```

### Production Deployment

#### Using Docker
```bash
# Build image
docker build -t donation-tracker .

# Run container
docker run -p 5005:5005 donation-tracker
```

#### Using Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5005 app:app
```

#### Environment-Specific Configuration
- **Development**: Debug mode, detailed logging
- **Staging**: Production-like with test data
- **Production**: Optimized performance, security hardened

## 📈 Performance Optimization

### Database Optimization
- **Indexing**: Strategic indexes on frequently queried fields
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Efficient MongoDB queries with projections

### Caching Strategy
- **Application Caching**: In-memory caching for frequently accessed data
- **Database Caching**: MongoDB query result caching
- **Static Asset Caching**: Browser caching for CSS/JS files

### Frontend Optimization
- **Asset Minification**: Compressed CSS and JavaScript
- **Image Optimization**: Responsive images with WebP format
- **Lazy Loading**: Progressive content loading

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow design patterns**: Implement using established patterns
4. **Add tests**: Include pattern-specific tests
5. **Update documentation**: Keep README and API docs current
6. **Submit pull request**: With detailed description

### Code Standards
- **PEP 8**: Python code style guidelines
- **Type Hints**: Use type annotations for better code documentation
- **Docstrings**: Comprehensive function and class documentation
- **Design Patterns**: Follow established pattern implementations

### Testing Requirements
- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **Pattern Tests**: Validate design pattern implementations
- **Performance Tests**: Ensure acceptable performance

## 📚 Learning Resources

### Design Patterns
- **Gang of Four**: Original design patterns book
- **Python Patterns**: Python-specific pattern implementations
- **Real-World Examples**: This project as practical reference

### Flask Development
- **Flask Documentation**: Official Flask guides and tutorials
- **Flask Patterns**: Best practices for Flask applications
- **Testing Flask**: Comprehensive testing strategies

### MongoDB
- **MongoDB University**: Free online courses
- **PyMongo Documentation**: Python MongoDB driver
- **Database Design**: NoSQL schema design principles

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Design Patterns**: Inspired by Gang of Four patterns
- **Flask Community**: For excellent documentation and examples
- **Bootstrap Team**: For the responsive CSS framework
- **MongoDB**: For the flexible NoSQL database
- **Open Source Community**: For tools and libraries that made this possible

## 📞 Support

For questions, issues, or contributions:

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides in `docs/` directory
- **API Reference**: Detailed API documentation in `postman/`
- **Design Patterns**: Implementation details in `DESIGN_PATTERNS_SUMMARY.md`

---

**Built with ❤️ to demonstrate design patterns in real-world applications**
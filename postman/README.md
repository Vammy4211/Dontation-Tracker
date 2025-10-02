# Postman Collection for Donation Tracker API

This directory contains a comprehensive Postman collection for testing the Donation Tracker API, which demonstrates multiple design patterns in a real-world application.

## Files Included

- `Donation_Tracker_API.postman_collection.json` - Complete API collection with all endpoints
- `Donation_Tracker.postman_environment.json` - Environment variables for different deployment stages
- `API_Documentation.md` - Comprehensive API documentation
- `README.md` - This file with setup and usage instructions

## Quick Setup

### 1. Import Collection and Environment

1. Open Postman
2. Click "Import" button
3. Select both JSON files:
   - `Donation_Tracker_API.postman_collection.json`
   - `Donation_Tracker.postman_environment.json`
4. Select the "Donation Tracker Environment" from the environment dropdown

### 2. Configure Environment Variables

Update the following variables in your environment:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `base_url` | API base URL | `http://127.0.0.1:5005` |
| `test_user_email` | Test user email | `testuser@example.com` |
| `test_user_password` | Test user password | `testPassword123` |
| `admin_email` | Admin user email | `admin@donationtracker.com` |
| `admin_password` | Admin user password | `adminPassword123` |

### 3. Start the API Server

Make sure your Donation Tracker API server is running:

```bash
cd donation-tracker
python app.py
```

The server should start on `http://127.0.0.1:5005`

## Collection Structure

### 📁 Authentication
- **Register User** - Create new user accounts (demonstrates Factory pattern)
- **Login User** - Authenticate and receive JWT token
- **Get User Profile** - Retrieve current user information
- **Logout User** - Invalidate authentication token

### 📁 Campaigns
- **Get All Campaigns** - List campaigns with sorting (Strategy pattern)
- **Get Campaign by ID** - Retrieve specific campaign details
- **Create Campaign** - Create new fundraising campaign
- **Update Campaign** - Modify existing campaign
- **Delete Campaign** - Remove campaign (admin only)
- **Search Campaigns** - Search with filters and criteria

### 📁 Donations
- **Make Donation - Credit Card** - Process credit card payments (Strategy pattern)
- **Make Donation - PayPal** - Process PayPal payments (Strategy pattern)
- **Make Donation - Bank Transfer** - Process bank transfers (Strategy pattern)
- **Get User Donations** - List current user's donations
- **Get Campaign Donations** - List donations for specific campaign

### 📁 Admin
- **Get All Users** - Administrative user management
- **Get System Statistics** - Analytics and reporting
- **Update User Status** - Manage user account status

### 📁 Design Patterns Testing
- **Test Factory Pattern** - Verify UserFactory implementation
- **Test Singleton Pattern** - Check DatabaseManager singleton
- **Test Strategy Pattern - Sorting** - Test sorting algorithms
- **Test Repository Pattern** - Validate data access layer

## Automated Features

### Pre-request Scripts
The collection includes pre-request scripts that:
- Set up base URL if not configured
- Generate dynamic test data (timestamps, random emails)
- Prepare authentication headers

### Test Scripts
Automated tests validate:
- Response status codes (200, 201, etc.)
- Response time (< 2000ms)
- Response structure and data types
- Authentication token extraction
- Error handling

### Environment Variables Auto-Update
The collection automatically extracts and stores:
- Authentication tokens from login responses
- User IDs from registration responses  
- Campaign IDs from creation responses
- Donation IDs from transaction responses

## Usage Workflows

### Basic Testing Workflow

1. **Setup**: Import collection and configure environment
2. **Register**: Create a test user account
3. **Login**: Authenticate and get JWT token
4. **Test Endpoints**: Run campaign and donation operations
5. **Admin Functions**: Test administrative features

### Design Pattern Testing Workflow

1. **Factory Pattern**: Use registration endpoint with different user types
2. **Singleton Pattern**: Call singleton test endpoint multiple times
3. **Strategy Pattern**: Test different sorting and payment strategies
4. **Repository Pattern**: Perform CRUD operations through repository endpoints

### Performance Testing

Use Postman's Collection Runner to:
- Run entire collection for load testing
- Execute specific folders for focused testing
- Generate performance reports
- Test with different data sets

## Advanced Configuration

### Multiple Environments

Create additional environments for:
- **Development**: `http://localhost:5005`
- **Staging**: `https://staging.donationtracker.com`
- **Production**: `https://api.donationtracker.com`

### Custom Test Data

Modify environment variables to use custom test data:

```javascript
// In pre-request script
pm.environment.set('custom_campaign_title', 'My Test Campaign');
pm.environment.set('custom_donation_amount', 150.00);
```

### Batch Testing

Use Collection Runner with CSV data files for:
- Multiple user registrations
- Bulk campaign creation
- Various donation scenarios

## Troubleshooting

### Common Issues

**Authentication Errors (401)**
- Verify JWT token is valid and not expired
- Check Authorization header format: `Bearer <token>`
- Ensure login was successful

**Connection Errors**
- Verify API server is running
- Check base_url environment variable
- Confirm port number (default: 5005)

**Validation Errors (422)**
- Check request body format
- Verify required fields are included
- Validate data types and constraints

### Debug Mode

Enable Postman console to view:
- Request/response details
- Script execution logs
- Environment variable changes
- Error messages and stack traces

## Testing Best Practices

### 1. Test Data Management
- Use dynamic data generation for unique values
- Clean up test data after testing
- Use separate test database for development

### 2. Authentication Testing
- Test token expiration scenarios
- Verify refresh token functionality
- Check unauthorized access attempts

### 3. Error Handling Testing
- Test invalid input scenarios
- Verify error response formats
- Check HTTP status codes

### 4. Design Pattern Validation
- Verify singleton instance uniqueness
- Test factory pattern with all user types
- Validate strategy pattern implementations
- Check repository pattern CRUD operations

## Integration with CI/CD

### Newman CLI

Run collection from command line:

```bash
# Install Newman
npm install -g newman

# Run collection
newman run Donation_Tracker_API.postman_collection.json \
  -e Donation_Tracker.postman_environment.json \
  --reporters cli,junit \
  --reporter-junit-export results.xml
```

### GitHub Actions

```yaml
name: API Testing
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run API Tests
        run: |
          npm install -g newman
          newman run postman/Donation_Tracker_API.postman_collection.json \
            -e postman/Donation_Tracker.postman_environment.json
```

## Support and Documentation

- **API Documentation**: See `API_Documentation.md` for detailed endpoint documentation
- **Design Patterns**: Refer to `DESIGN_PATTERNS_SUMMARY.md` in the main project directory
- **Issues**: Report issues in the main project repository
- **Updates**: Collection is updated with new API features and endpoints

## License

This Postman collection is part of the Donation Tracker project and follows the same license terms.
# Solarate

Solarate is a Django-React application that helps users analyze utility rates based on their location and annual energy consumption. The application integrates with OpenEI's Utility Rate Database to provide accurate utility tariff information and cost projections.

## Features

- Address-based utility rate lookup using OpenEI API
- Customizable energy consumption analysis (1,000 - 10,000 kWh)
- Utility cost escalator settings (4% - 10%)
- 20-year utility cost projections
- Detailed utility tariff information display
- User authentication system
- Webhook integration for project updates
- REST API endpoints for project management

## Prerequisites

- Python 3.x
- Node.js and npm
- OpenEI API key (obtain from [OpenEI Services](https://openei.org/services/))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ayoubbif/solarate.git
cd solarate
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Node.js dependencies:
```bash
cd app/client && npm install
```

5. Set up environment variables:
   Create a `.env` file in the root directory and add:
```
OPENEI_API_KEY=your_api_key_here
SECRET_KEY=your_django_secret_key
WEBHOOK_URL=your_webhook_url
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

## Development

Run the development server:
```bash
python manage.py runserver
```

For frontend development with hot reloading:
```bash
npm run dev
```

## API Usage

### Create a New Project
```bash
POST /api/projects/

{
    "address": "1234 Elm Street Springfield, IL 62701",
    "consumption": 3000,
    "escalator": 7.0,
    "name": "Project ABC",
    "description": "A sample project description",
    "selected_rate": "standard_rate"
}
```

## Models

### Project
- User (ForeignKey to Django User)
- Description
- Name
- Address
- Consumption
- Escalator Percentage
- Selected Rate

### ProposalUtility
- Project (OneToOneField)
- OpenEI ID
- Rate Name
- Pricing Matrix
- Average Rate
- First Year Cost

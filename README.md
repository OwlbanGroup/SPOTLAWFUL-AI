# SPOTLAWFUL AI Project

## Overview

SPOTLAWFUL AI is an advanced legal AI platform that provides legal text analysis, document analysis, revenue optimization, and multi-channel communication with users. The system supports continuous learning, performance monitoring, scalability, and community engagement.

## Features

- Legal text and document analysis with AI insights
- User subscription management
- Multi-channel communication: email, SMS, phone calls, social media
- Performance monitoring and load balancing for scalability
- User feedback collection and continuous learning updates
- Comprehensive user education and legal compliance support
- Community engagement platform

## Setup and Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment tool (venv)
- Node.js and npm (optional, for frontend development)

### Backend Setup

1. Clone the repository
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run tests:

   ```bash
   pytest spotlawful_ai/test_api_server.py
   ```

5. Start the API server:

   ```bash
   waitress-serve --host=0.0.0.0 --port=5000 spotlawful_ai.api_server:app
   ```

### Frontend Setup

Open `frontend/index.html` in a modern web browser. The frontend interacts with the backend API server.

## Usage

- Use the frontend interface to subscribe/unsubscribe users, analyze legal texts, and send feedback.
- API endpoints are available for integration with other systems.

## Deployment

Use the provided `deploy.sh` (Linux/macOS) or `deploy.bat` (Windows) scripts to automate setup and deployment.

## Contribution

Contributions are welcome. Please fork the repository and submit pull requests.

## License

Specify your license here.

## Contact

For questions or support, contact the project maintainers.

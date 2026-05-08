# ELD Route Application

## Overview
The ELD Route Application is a full-stack web application designed to assist users in managing trip details and generating route instructions and ELD logs in compliance with Hours of Service (HOS) regulations. The application is built using Django for the backend and React for the frontend.

## Features
- Input trip details such as start location, destination, and trip duration.
- Generate route instructions based on the provided trip details.
- Create ELD logs that adhere to HOS regulations.
- User-friendly interface for entering trip information and viewing results.

## Technologies Used
- **Backend**: Django, Django REST Framework
- **Frontend**: React, TypeScript
- **Database**: SQLite (default for Django, can be configured)
- **Containerization**: Docker

## Project Structure
```
eld-route-app
├── backend                # Django backend
│   ├── manage.py         # Command-line utility for managing the Django project
│   ├── requirements.txt   # Python packages required for the backend
│   ├── .env.example       # Example environment variables
│   ├── eld_route          # Main Django application
│   ├── trips              # App for handling trip details
│   └── eld                # App for handling ELD logs
├── frontend               # React frontend
│   ├── package.json       # npm configuration file
│   ├── tsconfig.json      # TypeScript configuration file
│   ├── public             # Public assets
│   └── src                # Source code for the React application
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Instructions for building the Docker image
├── .gitignore             # Files to ignore in Git
└── README.md              # Project documentation
```

## Setup Instructions

### Backend
1. Navigate to the `backend` directory.
2. Create a virtual environment and activate it.
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Set up the database:
   ```
   python manage.py migrate
   ```
5. Run the development server:
   ```
   python manage.py runserver
   ```

### Frontend
1. Navigate to the `frontend` directory.
2. Install the dependencies:
   ```
   npm install
   ```
3. Start the React application:
   ```
   npm start
   ```

## Usage
- Access the application in your web browser at `http://localhost:3000`.
- Enter trip details in the form provided and submit to receive route instructions and ELD logs.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
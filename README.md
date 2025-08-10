DEEP_SCRIPT
A full-stack web application for movie script generation and emotion detection. The backend is built with Django and Python, leveraging fine-tuned Hugging Face models for natural language processing tasks. The frontend is a React application built with Tailwind CSS.

Project Structure
frontend/: The React application.

backend/: The Django project and API.

models/: Container for the fine-tuned GPT-2 and DistilBERT models.

Getting Started
Prerequisites
Python 3.10+

Node.js & npm (for the frontend)

Backend Setup
Navigate to the backend/ directory.

Install Python dependencies: pip install -r requirements.txt

Run database migrations: python manage.py makemigrations and then python manage.py migrate

Run the development server: python manage.py runserver

Frontend Setup
Navigate to the frontend/ directory.

Install Node.js dependencies: npm install

Start the development server: npm start

 App should now be running, with the frontend on a different port (e.g., http://localhost:3000) and the backend API on http://localhost:8000.

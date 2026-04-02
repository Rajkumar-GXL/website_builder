# Application Setup Instructions:

STEP1: git clone: https://github.com/Rajkumar-GXL/website_builder.git

STEP2: Create Virtual Environment

    command: python -m venv venv

   command to activate virtual Environment: ./venv/Scripts/activate

STEP3: Install Dependencies
      command: pip install -r requirements.txt

STEP3: MySQL Setup
    1. connect mysql workbench local instance
    2. update the credentials in config.py file and .env file
    3. import the attached master database in workbench.

STEP4: Environment Variables - .env

command to run the application: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Application Overview & Testing Instructions:

Step 1: Open Website Builder
    http://localhost:8000/

Step 2: Enter:

    Website Title

    Category

    Subcategory

Step 3: Click "Create Website"

    System Automatically:

        Creates new MySQL tenant database

        Creates tables

        Seeds products

        Generates AI theme JSON

        Stores website entry in master_db

        Website becomes live

<!-- gemini-3-flash-preview -->
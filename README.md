Sign Language Recognition Web Application

Welcome to the Sign Language Recognition Web Application! This application allows users to communicate using American Sign Language (ASL) by recognizing hand gestures captured through their webcam in real-time. Users can register, login, and manage their subscription plans to access the sign recognition feature. Additionally, the application provides options for password reset and account deletion.

Features
User Authentication and Authorization: Secure registration, login, and session management.
Sign Recognition: Real-time processing of live video feed to recognize ASL signs.
Subscription Management: Offer three subscription plans with daily sign recognition limits.
Payment Processing: Support for multiple payment methods and transaction history.
User Interface: Intuitive and visually appealing UI with clear navigation paths.
Password Reset: Allow users to reset their passwords via email.
Account Deletion: Provide options for users to delete their accounts.

Setup

Clone the Repository:
`git clone https://github.com/yourusername/sign-language-recognition.git`

run `app.py`

open 'http://127.0.0.1:5000' in your browser 
(change port number if youre using different port than 5000)

Usage
Registration: Create a new account by providing a unique username, valid email, and password.
Login: Access your account using your registered credentials.
Sign Recognition: Grant webcam access to capture live video and translate ASL signs into text.
Subscription Management: View and manage your subscription plan, including upgrading or downgrading options.
Payment: Choose from multiple payment methods to purchase or renew your subscription.
Password Reset: Forgot your password? Use the password reset functionality to regain access to your account.
Account Deletion: If you wish to delete your account, navigate to the account settings and follow the prompts.

.
├── app.py
├── app
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── routes.py
│   ├── static
│   │   ├── css
│   │   ├── img
│   │   ├── js
│   │   └── sass
│   └── templates
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── pricing.html
│       ├── purchase.html
│       ├── register.html
│       ├── reset_password.html
│       ├── sli.html
│       └── userprofile.html
├── models
│   ├── FINAL_MODEL
│   │   └── final_model.h5
│   ├── CHECKPOINT_MODEL
│   │   └── checkpoint_model.h5
│   └── SLI_MODEL
│       └── sign_language_interpreter.h5
├── tests
│   ├── crash_test.py
│   └── crash1_test.py
├── readme.md
└── requirements.txt
# Step 1: username / email page
LOGIN_EMAIL = (
    "input#email, input[name='email'], input[type='email'], "
    "input[autocomplete='username'], input[aria-label*='Email' i]"
)
CONTINUE_BUTTON = (
    "button:has-text('Continue'), button[data-testid='continue'], "
    "button[type='submit']:has-text('Continue')"
)

# Step 2: password page
LOGIN_PASSWORD = (
    "input#password, input[name='password'], input[type='password'], "
    "input[autocomplete='current-password'], input[aria-label*='Password' i]"
)
LOGIN_BUTTON = (
    "button[data-testid='sign-in-button'], "
    "form button[type='submit']:has-text('Sign In'), "
    "form button:has-text('Sign in'), "
    "form button:has-text('Log In'), "
    "form button:has-text('Login'), "
    "form input[type='submit']"
)

# Logged-in indicators
PROFILE_INDICATORS = (
    "[data-testid='user-avatar'], a[href*='profile'], a[aria-label*='Profile' i]"
)

# Job page
EASY_APPLY_BUTTON = "button:has-text('Easy Apply')"
APPLY_SUBMIT_BUTTON = (
    "button:has-text('Submit Application'), button:has-text('Submit'), "
    "button[aria-label*='Submit' i]"
)

from flask import Flask, redirect, request, session, url_for
import requests
import secrets

app = Flask(__name__)

# Secret key for session management (you can change this)
app.secret_key = secrets.token_urlsafe(16)

# LinkedIn app credentials
CLIENT_ID = "8600kyqzq8melc"
CLIENT_SECRET = "WPL_AP1.Lk3dk1bVdMfM8zAp.yuuqUQ=="
REDIRECT_URI = "https://testing.dpdp-privcy.in.net/callback"  # Ensure this matches the registered URI

# OAuth scope (permissions requested from the user)
SCOPE = "r_liteprofile r_emailaddress w_member_social"

# Step 1: Redirect to LinkedIn for authorization
@app.route('/')
def index():
    state = secrets.token_urlsafe(16)  # Generate a random state string for security
    session['state'] = state  # Store the state in the session to verify on callback

    # LinkedIn authorization URL
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&state={state}"
    return redirect(auth_url)


# Step 2: Callback route to handle LinkedIn's redirect
@app.route('/callback')
def callback():
    # Step 2a: Get the authorization code and state from the request
    auth_code = request.args.get('code')
    state = request.args.get('state')

    # Step 2b: Verify the state matches the session value
    if state != session.get('state'):
        return "Error: Invalid state", 400  # Security issue if states don't match

    # Step 3: Exchange the authorization code for an access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=token_data)

    if response.status_code == 200:
        # Successfully received the access token
        access_token = response.json().get('access_token')
        return f"Access Token: {access_token}"
    else:
        # Handle error from LinkedIn
        return f"Error: {response.json().get('error_description')}", 400


if __name__ == '__main__':
    app.run(debug=True)

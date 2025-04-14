from flask import Flask, redirect, request, session
import requests
import secrets
from urllib.parse import quote

app = Flask(__name__)

# Secret key for session management
app.secret_key = secrets.token_urlsafe(16)

# LinkedIn app credentials
CLIENT_ID = "8600kyqzq8melc"
CLIENT_SECRET = "WPL_AP1.Lk3dk1bVdMfM8zAp.yuuqUQ=="
REDIRECT_URI = "https://testing.dpdp-privcy.in.net/callback"  # Must exactly match LinkedIn app config

# OAuth scope (permissions requested)
SCOPE = "r_liteprofile r_emailaddress w_member_social"

# Step 1: Redirect to LinkedIn for user authorization
@app.route('/')
def index():
    state = secrets.token_urlsafe(16)
    session['state'] = state

    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={quote(REDIRECT_URI)}"
        f"&scope={quote(SCOPE)}"
        f"&state={state}"
    )

    print("Redirecting to LinkedIn:", auth_url)
    return redirect(auth_url)

# Step 2: Callback route to handle LinkedIn redirect with the auth code
@app.route('/callback')
def callback():
    print("Request args:", request.args)  # Log incoming GET params

    auth_code = request.args.get('code')
    state = request.args.get('state')

    # Validate presence of required query parameters
    if not auth_code:
        return "Error: Missing authorization code.", 400
    if not state or state != session.get('state'):
        return "Error: Invalid state parameter.", 400

    # Step 3: Exchange the authorization code for an access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_url, data=token_data, headers=token_headers)

    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return f"<h3>✅ Access Token:</h3><p>{access_token}</p>"
    else:
        error_data = response.json()
        return f"<h3>❌ Error:</h3><pre>{error_data}</pre>", 400

if __name__ == '__main__':
    app.run(debug=True)

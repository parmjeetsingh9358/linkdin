from flask import Flask, redirect, request, session
import requests
import secrets
from urllib.parse import quote
import json
import io

app = Flask(__name__)

# Set up session configuration for secure cookies and SameSite policy
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.secret_key = secrets.token_urlsafe(16)

# LinkedIn app credentials
CLIENT_ID = "86s0cexioiiox7"
CLIENT_SECRET = "WPL_AP1.flaMDksZJWvYDgxB.1KSB3A=="
REDIRECT_URI = "https://testing.dpdp-privcy.in.net/callback"  # Must match LinkedIn app settings

# Scope for posting (must be approved in LinkedIn dev portal)
SCOPE = "openid profile w_member_social email"

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

@app.route('/callback')
def callback():
    print("Request args:", request.args)

    if 'error' in request.args:
        error = request.args.get('error')
        error_desc = request.args.get('error_description')
        return f"<h3>❌ OAuth Error:</h3><p><b>{error}</b>: {error_desc}</p>", 400

    auth_code = request.args.get('code')
    state = request.args.get('state')

    if not auth_code:
        return "Error: Missing authorization code.", 400
    if not state or state != session.get('state'):
        return "Error: Invalid state parameter.", 400

    # Step 1: Exchange authorization code for access token
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

    token_response = requests.post(token_url, data=token_data, headers=token_headers)

    if token_response.status_code != 200:
        return f"<h3>❌ Error Fetching Token:</h3><pre>{token_response.json()}</pre>", 400

    access_token = token_response.json().get('access_token')
    print(access_token, "=========")

    # Step 2: Get actual user URN
    me_response = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(me_response, "==== me_response ====")
    print(me_response.json(), "==== json ====")

    if me_response.status_code != 200:
        return f"<h3>❌ Error Getting Profile:</h3><pre>{me_response.json()}</pre>", 400

    linkedin_id = me_response.json().get("sub")
    author_urn = f"urn:li:person:{linkedin_id}"
    print(linkedin_id, "==== linkedin_id ====")
    print(author_urn, "==== author_urn ====")


    # Step 3: Register image upload
    # author_urn = "urn:li:person:8675309"
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author_urn,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    print(register_body, "==== register_body ====")
    register_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    print(register_headers, "==== register_headers ====")
    register_res = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=register_headers,
        data=json.dumps(register_body)
    )
    print(register_res, "==== register_res ====")
    if register_res.status_code != 200:
        return f"<h3>❌ Error Registering Upload:</h3><pre>{register_res.json()}</pre>", 400

    upload_data = register_res.json()
    upload_url = upload_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = upload_data["value"]["asset"]

    # Step 4: Download image from remote URL
    image_url = "https://imgs.search.brave.com/OqAh4CD9t-8wCyru3oo5Douk-c2JYvZiynQ_BV1gKYU/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tYXJr/ZXRwbGFjZS5jYW52/YS5jb20vRUFHUEU3/SnEzaDgvOC8wLzE2/MDB3L2NhbnZhLWdy/ZWVuLWFwcHJlY2lh/dGlvbi1jZXJ0aWZp/Y2F0ZS1IWmxwdkhv/a1ZJcy5qcGc"
    image_response = requests.get(image_url)

    if image_response.status_code != 200:
        return f"<h3>❌ Failed to download image:</h3><pre>{image_response.text}</pre>", 400

    # Step 5: Upload image to LinkedIn
    upload_image_res = requests.put(
        upload_url,
        data=image_response.content,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream"
        }
    )

    if upload_image_res.status_code not in [200, 201]:
        return f"<h3>❌ Image Upload Failed:</h3><pre>{upload_image_res.text}</pre>", 400

    # Step 5: Create a post
    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "This post is made from my Flask app with an image! 😎"
                },
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "description": {"text": "Auto-posted image"},
                    "media": asset_urn,
                    "title": {"text": "Flask App Image Upload"}
                }]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    print(post_data, "=================")

    post_res = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=register_headers,
        data=json.dumps(post_data)
    )

    if post_res.status_code == 201:
        return "<h3>✅ Successfully posted to LinkedIn with image!</h3>"
    else:
        return f"<h3>❌ Failed to create post:</h3><pre>{post_res.json()}</pre>", 400

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, redirect, request, session, render_template_string
import secrets
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

# LinkedIn app credentials
CLIENT_ID = "86s0cexioiiox7"
CLIENT_SECRET = "WPL_AP1.flaMDksZJWvYDgxB.1KSB3A=="
REDIRECT_URI = "https://testing.dpdp-privcy.in.net/callback"
SCOPE = "r_liteprofile r_emailaddress"  # No post permission needed

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
    return redirect(auth_url)

@app.route('/callback')
def callback():
    error = request.args.get('error')
    if error:
        return f"<h3>❌ LinkedIn Error:</h3><p>{error}</p>", 400

    state = request.args.get('state')
    if state != session.get('state'):
        return "Error: State mismatch!", 400

    # Instead of auto-posting, redirect user to the LinkedIn Share Dialog
    certificate_url = "https://marketplace.canva.com/EAFtLMllF3s/1/0/1600w/canva-blue-and-gold-simple-certificate-zxaa6yB-uaU.jpg"

    share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={quote(certificate_url)}"

    # Show suggested text + copy button + LinkedIn post dialog link
    html = f"""
    <h2>🎉 Ready to share your certificate on LinkedIn?</h2>
    <p>1. Click the button below to open the LinkedIn post dialog.</p>
    <p>2. Paste the suggested text when prompted.</p>

    <textarea id="postText" rows="10" cols="80">
🎉 Excited to share that I’ve successfully completed the "Data Protection and Privacy Foundations" certification from Privacyium Tech! 🚀
This course helped me strengthen my understanding of data handling principles, GDPR compliance, and secure data practices.
Thanks to the instructors and mentors for the guidance and support!
📄 Here’s my certificate 👇
#DataPrivacy #GDPR #Cybersecurity #LearningNeverStops #LinkedIn #Achievement
    </textarea><br><br>

    <button onclick="copyText()">📋 Copy Text</button>
    <a href="{share_url}" target="_blank"><button>📢 Share on LinkedIn</button></a>

    <script>
    function copyText() {{
        const textArea = document.getElementById("postText");
        textArea.select();
        document.execCommand("copy");
        alert("Post text copied! You can now paste it into LinkedIn.");
    }}
    </script>
    """

    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)

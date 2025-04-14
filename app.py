from flask import Flask, redirect, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return '<a href="/share">Share on LinkedIn</a>'

@app.route('/share')
def share():
    # Redirect to LinkedIn share dialog with your preview page URL
    preview_url = "https://testing.dpdp-privcy.in.net/"  # Change this to your live domain
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={preview_url}"
    return redirect(linkedin_url)

@app.route('/preview')
def preview():
    return render_template('preview.html')

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, redirect, render_template, url_for

app = Flask(__name__)

# This route opens the LinkedIn share dialog
@app.route('/share')
def share():
    preview_url = "https://testing.dpdp-privcy.in.net/"  # Replace with your real domain
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={preview_url}"
    return redirect(linkedin_url)

# This is the preview page that LinkedIn scrapes (with OG tags)
@app.route('/preview')
def preview():
    return render_template('preview.html')

if __name__ == '__main__':
    app.run(debug=True)

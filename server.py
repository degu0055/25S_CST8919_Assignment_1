# Repo
# https://github.com/degu0055/25S_CST8919_Assignment_1

"""Python Flask WebApp Auth0 integration example"""

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# Configure OAuth
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",  # ✅ FIXED: use 'profile' not 'file'
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# Controllers API
@app.route("/")
def home():
    user = session.get("user", {})
    first_name = user.get("userinfo", {}).get("given_name")  # ✅ FIXED: nested lookup

    print("User session data:")
    print(json.dumps(user, indent=2))

    return render_template(
        "home.html",
        session=user,
        pretty=json.dumps(user, indent=4),
        first_name=first_name,
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token  # Contains access_token, id_token, userinfo, etc.
    redirect_to = session.pop("redirect_after_login", "/")
    return redirect(redirect_to)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/protected")
def protected():
    user = session.get("user")
    if user is None:
        session["redirect_after_login"] = request.path
        return redirect(url_for("login"))
    return render_template("protected.html", user=user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(env.get("PORT", 3000)))

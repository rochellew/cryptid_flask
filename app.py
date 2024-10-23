from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

FASTAPI_URL = "http://127.0.0.1:8000"

@app.route('/')
def index():
    response = requests.get(f"{FASTAPI_URL}/cryptids/")
    cryptids = response.json()
    return render_template("index.html", cryptids=cryptids)

@app.route('/cryptid/<int:cryptid_id>')
def cryptid_detail(cryptid_id):
    response = requests.get(f"{FASTAPI_URL}/cryptids/{cryptid_id}")
    cryptid = response.json()
    return render_template("cryptid.html", cryptid=cryptid)

@app.route('/add', methods=['GET','POST'])
def add_cryptid():
    if request.method == 'POST':
        name=request.form['name']
        description = request.form['description']
        image_url = request.form['image_url']

        new_cryptid = {
            "name":name,
            "description": description,
            "image_url":image_url
        }
        print(new_cryptid)
        
        response = requests.post(f"{FASTAPI_URL}/cryptids/", json=new_cryptid)

        if response.status_code == 201:
            flash("Cryptid added successfully!", "sucess")
            return redirect(url_for('index'))
        else:
            flash("An error has occured while adding the cryptid.", "error")
    return render_template("add_cryptid.html")


@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)

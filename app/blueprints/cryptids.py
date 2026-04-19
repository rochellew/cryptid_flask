import os
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.decorators import admin_required

cryptids_bp = Blueprint("cryptids", __name__)

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")


@cryptids_bp.route('/about')
def about():
    return render_template("cryptids/about.html")


@cryptids_bp.route('/')
@login_required
def index():
    response = requests.get(f"{FASTAPI_URL}/cryptids/")
    cryptids = response.json()
    return render_template("cryptids/index.html", cryptids=cryptids)


@cryptids_bp.route('/cryptid/<int:cryptid_id>')
@login_required
def cryptid_detail(cryptid_id):
    response = requests.get(f"{FASTAPI_URL}/cryptids/{cryptid_id}")
    cryptid = response.json()
    return render_template("cryptids/cryptid.html", cryptid=cryptid)


@cryptids_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_cryptid():
    if request.method == 'POST':
        new_cryptid = {
            "name": request.form['name'],
            "description": request.form['description'],
            "image_url": request.form['image_url']
        }
        response = requests.post(f"{FASTAPI_URL}/cryptids/", json=new_cryptid)

        if response.status_code == 201:
            flash("Cryptid added successfully!", 'success')
            return redirect(url_for('cryptids.index'))
        else:
            flash("An error has occurred while adding the cryptid.", 'error')

    return render_template("cryptids/add_cryptid.html")


@cryptids_bp.route('/cryptid/<int:cryptid_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cryptid(cryptid_id):
    if request.method == 'POST':
        updated_cryptid = {
            "name": request.form['name'],
            "description": request.form['description'],
            "image_url": request.form['image_url']
        }
        response = requests.put(f"{FASTAPI_URL}/cryptids/{cryptid_id}", json=updated_cryptid)

        if response.status_code == 201:
            flash("Cryptid updated successfully!", "success")
            return redirect(url_for('cryptids.index'))
        else:
            flash("Failed to update the cryptid. Please try again.", "error")
            return redirect(url_for('cryptids.edit_cryptid', cryptid_id=cryptid_id))

    response = requests.get(f"{FASTAPI_URL}/cryptids/{cryptid_id}")
    if response.status_code == 200:
        cryptid = response.json()
        return render_template('cryptids/edit_cryptid.html', cryptid=cryptid)
    else:
        flash("Cryptid not found.", "error")
        return redirect(url_for('cryptids.index'))


@cryptids_bp.route('/cryptid/<int:cryptid_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_cryptid(cryptid_id):
    response = requests.delete(f"{FASTAPI_URL}/cryptids/{cryptid_id}")

    if response.status_code == 204:
        flash("Cryptid deleted successfully!", "success")
    else:
        flash("Failed to delete the cryptid. Please try again.", "error")

    return redirect(url_for('cryptids.index'))
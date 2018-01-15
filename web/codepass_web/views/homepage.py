from flask import Blueprint, request, redirect, session, url_for, flash, render_template, jsonify, abort, Response


mod = Blueprint('homepage', __name__)


@mod.route('/')
def get_homepage():
    return render_template('homepage/homepage.html')

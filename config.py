from flask import Flask, render_template, url_for, redirect, session, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'gremio'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'pokebanco'
}
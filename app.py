import psycopg2, psycopg2.extras
import pymysql
import json
from flask import Flask, render_template, request
from collections import OrderedDict 
import os
from DataTable import DataTable

app = Flask(__name__)

db_uri = os.environ.get("DATABASE_URI")

@app.route('/', methods=["GET", "POST"])
def index():
	if request.method == "GET":
		x = DataTable(db_uri)
		sql = "SELECT customer_id, first_name FROM customer LIMIT 5;"
		headers = ['Customer ID', 'First Name']
		x.makeTable(sql, css_id="first_test_table", headers=headers, width=8)
		return render_template('base.html', table1=x)
	elif request.method == "POST":
		sql = request.form.get('sql')
		if request.form.get('headers') != '':
			headers = request.form.get('headers').split(", ")
		else:
			headers = None
		x = DataTable(db_uri)
		x.makeTable(sql, css_id="first_test_table", headers=headers, width=8)
		return render_template('base.html', table1=x)

if __name__ == "__main__":
	app.run(debug=True, )
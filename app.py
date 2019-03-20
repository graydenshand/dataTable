import psycopg2, psycopg2.extras
import pymysql
import json
from flask import Flask, render_template, request
from collections import OrderedDict 
import os
import urllib
from DataTable import DataTable

app = Flask(__name__)

db_uri = os.environ.get("DATABASE_URI")

@app.route('/', methods=["GET", "POST"])
def index():
	if request.method == "GET":
		if request.args.get('sql'):
			sql = request.args.get('sql')
			sql = urllib.unquote(sql)
			x = DataTable(db_uri)
			x.makeTable(sql, css_id="first_test_table", width=8)
			return render_template('base.html', table1=x)
		else:	
			x = DataTable(db_uri)
			sql = "SELECT customer_id, first_name FROM customer LIMIT 5;"
			headers = ['Customer ID', 'First Name']
			x.makeTable(sql, css_id="first_test_table", headers=headers, width=8)
			return render_template('base.html', table1=x)

if __name__ == "__main__":
	app.run(debug=True, port=3000)
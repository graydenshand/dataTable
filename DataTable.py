##Helper class for rendering data tables
import psycopg2, psycopg2.extras
import pymysql
import json
from flask import Flask, render_template, request
from collections import OrderedDict 
import os

app = Flask(__name__)


class DataTable():

	def __init__(self, uri=None, host=None, db=None, user=None, password=None, port=None):
		if uri == None:
			self.conn = psycopg2.connect(user=user, host=host, dbname=db, password=password, port=port)
		else:
			self.conn = psycopg2.connect(uri)
		self.cur = self.conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
		self.data = []
		self.css_id = ''
		self.headers = None
		self.sql = None
		self.errors = None
		self.width = 12


	def makeTable(self, sql, params=None, headers=None, css_id=None, width=12):
		self.cur.execute(sql, params)
		self.css_id = css_id
		self.sql = self.cur.mogrify(sql, params)
		self.width = width
		results = self.cur.fetchall()
		columns = sql.lower().split("select ")[1].split("from")[0].split(",")
		for i, column in enumerate(columns):
			columns[i] = column.strip()
		self.columns = columns
		self.headers=headers
		data = []
		for row in results:
			line = OrderedDict()
			if headers:
				if len(headers) != len(row.keys()):
					self.headers = None
			if '*' in columns:
				for k, v in row.items():
					line[k] = str(v).decode('utf-8')
			else:
				for i, k in enumerate(self.columns):
					line[k] = str(row.values()[i]).decode('utf-8')
			data.append(line)
		self.data = data


db_uri = os.environ.get("DATABASE_URI")


#Unit Tests

@app.route('/', methods=["GET", "POST"])
def index():
	if request.method == "GET":
		x = DataTable(db_uri)
		sql = "SELECT customer_id, first_name from customer LIMIT 5;"
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

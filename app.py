import psycopg2, psycopg2.extras
import pymysql
import json
from flask import Flask, render_template, request, url_for, redirect, send_file, session
from collections import OrderedDict 
import os
import urllib
from DataTable import DataTable
import csv
from datetime import timedelta


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')

app.permanent_session_lifetime = timedelta(days=365)

app.jinja_env.filters['urlencode'] = lambda u: urllib.quote(u)

db_uri = os.environ.get("DATABASE_URL")

@app.route('/', methods=["GET", "POST"])
def index():
	if request.method == 'GET':
		if 'Authenticated' in session.keys() and session['Authenticated'] == True:
			if request.args.get('sql'):
				sql = request.args.get('sql')
				sql = urllib.unquote(sql)
				x = DataTable(db_uri)
				x.makeTable(sql, css_id="first_test_table", width=8)
				return render_template('base.html', table1=x, sql=sql)
			else:	
				x = DataTable(db_uri)
				sql = "SELECT customer_id, first_name FROM customer LIMIT 5;"
				x.makeTable(sql, css_id="first_test_table", width=8)
				return render_template('base.html', table1=x, sql=sql)
		else:
			return render_template('login.html')
	if request.method == 'POST':
		passphrase = request.form.get('passphrase')
		if passphrase == 'lockpick':
			session['Authenticated'] = True
			session.permanent = True
			return redirect(url_for('index'))
		else:
			return render_template('login.html', error=True)

@app.route('/download_csv', methods=['GET'])
def download_csv():
	if request.args.get('sql'):
		sql = request.args.get('sql')
		sql = urllib.unquote(sql)
		x = DataTable(db_uri)
		results = x.makeTable(sql)
		headers = x.columns
		f = open('auto_increment.txt', 'r')
		auto_increment = int(f.read()) + 1
		print(auto_increment)
		f.close()
		f = open('auto_increment.txt', 'w')
		f.write(str(auto_increment))
		f.close()
		fn = 'static/output_{}.csv'.format(auto_increment)
		with open(fn, 'w') as f:
			writer = csv.writer(f)
			writer.writerow(headers)
			for i, row in enumerate(results):
				writer.writerow(row)
		return send_file(fn,
                     mimetype='text/csv',
                     attachment_filename='output.csv',
                     as_attachment=True)

if __name__ == "__main__":
	app.run(debug=True, port=3000)
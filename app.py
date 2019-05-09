import psycopg2, psycopg2.extras
import pymysql
import json
from flask import Flask, render_template, request, url_for, redirect, send_file
from collections import OrderedDict 
import os
import urllib
from DataTable import DataTable
import csv


app = Flask(__name__)

app.jinja_env.filters['urlencode'] = lambda u: urllib.quote(u)

db_uri = os.environ.get("DATABASE_URL")

@app.route('/', methods=["GET", 'POST'])
def index():
	if request.method == 'GET':
		if request.args.get('sql'):
			sql = request.args.get('sql')
			sql = urllib.unquote(sql)
			x = DataTable(db_uri)
			x.makeTable(sql, css_id="first_test_table", width=10)
			return render_template('base.html', table1=x, sql=sql)
		else:	
			x = DataTable(db_uri)
			sql = "SELECT customer_id, first_name FROM customer LIMIT 5;"
			x.makeTable(sql, css_id="first_test_table", width=10)
			return render_template('base.html', table1=x, sql=sql)
	elif request.method == 'POST':
		x = DataTable(db_uri)
		requested_tables = request.form.getlist('tables')
		#tables_string = ','.join(requested_tables)
		#MAKE JOINS
		#tables_string = requested_tables[0]
		#if len(requested_tables) > 1:
		#	tables_string += ' INNER JOIN {} ON ({} = {})'.format(new_table, table1.join_key, table2.join_key)
		tables_string = x.makeJoins(requested_tables)
		offset = request.form.get('offset')
		if offset !='':
			offset_string = "\nOFFSET {}".format(offset)
		else:
			offset_string = ''
		limit = request.form.get('limit')
		if limit != '':
			limit_string = "\nLIMIT {}".format(limit)
		else:
			limit_string = ''
		sql = 'SELECT * {}{}{};'.format(tables_string, offset_string, limit_string)
		url_sql = urllib.quote(sql)
		return redirect(url_for('index', sql=url_sql))

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
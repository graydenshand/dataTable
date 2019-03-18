##Helper class for rendering data tables
import psycopg2, psycopg2.extras
import pymysql
import json
from flask import Flask, render_template, request
from collections import OrderedDict 
import os

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
		self.columns = []


	def makeTable(self, sql, params=None, headers=None, css_id=None, width=12):
		self.cur.execute(sql, params)
		self.css_id = css_id
		self.sql = self.cur.query
		self.width = width
		self.columns = [desc.name for desc in self.cur.description]
		print(self.columns)
		results = self.cur.fetchall()
		self.headers=headers
		self.data = []
		if headers:
			if len(headers) != len(results[0].keys()):
				self.headers = None
		for row in results:
			line = OrderedDict()
			for i, k in enumerate(self.columns):
				line[k] = str(row.values()[i]).decode('utf-8')
			self.data.append(line)


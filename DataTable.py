 ##Helper class for rendering data tables
import psycopg2, psycopg2.extras
import pymysql
import json
from flask import Flask, render_template, request
from collections import OrderedDict 
import os
import re

class DataTable():

	def __init__(self, uri=None, host=None, db=None, user=None, password=None, port=None):
		if uri == None:
			self.conn = psycopg2.connect(user=user, host=host, dbname=db, password=password, port=port)
		else:
			self.conn = psycopg2.connect(uri)
		self.cur = self.conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
		self.data = []
		self.css_id = ''
		self.sql = None
		self.errors = None
		self.width = 12
		self.columns = []
		self.error = ""
		self.table_names = []
		self.foreign_keys = {}
		self.primary_keys = {}
		self.getAllTableNames()
		self.getAllForeignKeys()
		self.getAllPrimaryKeys()

	def getAllTableNames(self):
		sql = '''
			SELECT table_name
			FROM information_schema.tables
			WHERE table_type='BASE TABLE'
			AND table_schema='public';
		'''
		self.cur.execute(sql)
		for table in self.cur.fetchall():
			self.table_names.append(table['table_name'])
			self.foreign_keys[table['table_name']] = {}
			self.primary_keys[table['table_name']] = ''
		return self.table_names

	def getAllForeignKeys(self):
		sql = '''
			SELECT
			    tc.table_schema, 
			    tc.constraint_name, 
			    tc.table_name, 
			    kcu.column_name, 
			    ccu.table_schema AS foreign_table_schema,
			    ccu.table_name AS foreign_table_name,
			    ccu.column_name AS foreign_column_name 
			FROM 
			    information_schema.table_constraints AS tc 
			    JOIN information_schema.key_column_usage AS kcu
			      ON tc.constraint_name = kcu.constraint_name
			      AND tc.table_schema = kcu.table_schema
			    JOIN information_schema.constraint_column_usage AS ccu
			      ON ccu.constraint_name = tc.constraint_name
			      AND ccu.table_schema = tc.table_schema
			WHERE tc.constraint_type = 'FOREIGN KEY';
		'''
		self.cur.execute(sql)
		results = self.cur.fetchall()
		print(results)
		for key in results:
			self.foreign_keys[key['table_name']][key['column_name']] = [key['foreign_column_name'],key['foreign_table_name']]
		#print(self.foreign_keys)
		return self.foreign_keys

	def getAllPrimaryKeys(self):
		sql = '''
			SELECT
			    tc.table_schema, 
			    tc.constraint_name, 
			    tc.table_name, 
			    kcu.column_name
			FROM 
			    information_schema.table_constraints AS tc 
			    JOIN information_schema.key_column_usage AS kcu
			      ON tc.constraint_name = kcu.constraint_name
			      AND tc.table_schema = kcu.table_schema
			WHERE tc.constraint_type = 'PRIMARY KEY';
		'''
		self.cur.execute(sql)
		results = self.cur.fetchall()
		for key in results:
			self.primary_keys[key['table_name']] = key['column_name']
		return self.primary_keys

	def getUsedTableNames(self):
		self.table_names_used = set()
		regex_string = " " + " | ".join(self.table_names) + " "
		matches = re.findall(regex_string, self.sql)
		for match in matches:
			self.table_names_used.add(match.strip())
		return self.table_names_used

	def getUsedForeignKeys(self):
		self.getUsedTableNames()
		self.foreign_keys_in_table = {}
		if "*" in self.sql:
			for table in self.table_names_used:
				for key, value in self.foreign_keys[table].items():
					print(table, key, value)
					self.foreign_keys_in_table[key] = {'field': value[0], 'table': value[1]}
		else:
			for table in self.table_names_used:
				#print(self.foreign_keys[table])
				for key, value in self.foreign_keys[table].items():
					print(table, key, value)
					regex_string="({})( [as|AS]+ ([\w]+))*,".format(key)
					matches = re.findall(regex_string, self.sql)
					for match in matches:
						#print(match)
						if match[2] != '':
							self.foreign_keys_in_table[match[2].lower()] = {'field':value[0], 'table':value[1]}
						else:
							self.foreign_keys_in_table[match[0].lower()] = {'field':value[0], 'table':value[1]}
		return self.foreign_keys_in_table

	def getUsedPrimaryKeys(self):
		self.primary_keys_in_table = {}
		if "*" in self.sql:
			for table in self.table_names_used:
				self.primary_keys_in_table[self.primary_keys[table]] = {'field': self.primary_keys[table], 'table': table}
		else:
			for table in self.table_names_used:
				regex_string="({})( [as|AS]+ ([\w]+))*,".format(self.primary_keys[table])
				matches = re.findall(regex_string, self.sql)
				#print(matches)
				for match in matches:
					if match[2] != '':
						self.primary_keys_in_table[match[2].lower()] = {'field':match[0], 'table':table}
					else:
						self.primary_keys_in_table[match[0].lower()] = {'field':match[0], 'table':table}
		return self.primary_keys_in_table


	def makeTable(self, sql, params=None, css_id=None, width=12):
		try:
			self.cur.execute(sql, params)
		except psycopg2.Error as e:
			self.error = e.pgerror
			return self.error
		self.css_id = css_id
		self.sql = self.cur.query
		self.columns = [desc.name for desc in self.cur.description]
		self.getUsedForeignKeys()
		self.getUsedPrimaryKeys()
		self.width = width
		results = self.cur.fetchall()
		self.data = []
		for row in results:
			line = OrderedDict()
			for i, k in enumerate(self.columns):
				line[k] = str(row.values()[i]).decode('utf-8')
			self.data.append(line)
		return results


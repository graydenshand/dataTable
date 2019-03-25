# dataTable
A pluggable project to simplify table creation in Flask

This project consists of a python class and Jinja2 template to expedite the process of displaying data on the web.

## Getting Started
To include dataTable in your project, import the `DataTable` class from `DataTable.py`. 
```
from DataTable import DataTable
```
 
## class DataTable
DataTable consists of the following properties and methods:
### properties
```
self.conn
self.cur
self.data
self.css_id
self.headers
self.sql
self.errors
self.width
self.columns
```


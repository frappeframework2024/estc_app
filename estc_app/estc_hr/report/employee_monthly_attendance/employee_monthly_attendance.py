# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime,timedelta


def execute(filters=None):
	
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns=[]
	columns.append({'fieldname':"employee",'label':"Employee",'fieldtype':'Link','options':'Employee','align':'center','width':130})
	columns.append({'fieldname':"employee_name",'label':"Employee Name",'fieldtype':'Data','align':'left','width':130})
	
	columns_date = get_data_column(filters)
	columns.extend(columns_date['columns'])
	return columns

def get_data_column(filters):
	columns=[]
	col = []
	fiscal_year = frappe.db.get_value('Fiscal Year', filters.get('fiscal_year'),['start_date', 'end_date'], as_dict=1)
	current_date = fiscal_year.start_date
	while current_date <= fiscal_year.end_date:
		columns.append({'fieldname':current_date.strftime('%b-%y'),'label':current_date.strftime('%b-%y'),'fieldtype':'float','align':'center','query':f"IF(MONTH(attendance_date) = '{current_date.strftime('%m')}' AND YEAR(attendance_date) = '{current_date.strftime('%Y')}',sum(attendance_value),0) AS '{current_date.strftime('%b-%y')}'",'width':130})
		current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
	columns.append({'fieldname':"ending_balance",'label':"Ending Balance",'fieldtype':'float','align':'center','query':"(SELECT SUM(balance) from `tabEmployee Attendance Leave Count` where employee = a.employee and fiscal_year = %(fiscal_year)s) as ending_balance",'width':130})

	for c in columns:
		if c.get('query'):
			col.append(c['query'])
	data_field = ",".join(col)
	return {'data_field':data_field,'columns':columns}

def get_data(filters):
	data = []
	columns_date = get_data_column(filters)
	sql = """
			select 
				employee,
				employee_name,
				{1}
			from 
				`tabAttendance` a
			{0}
			group by
				employee,
				employee_name
	""".format(get_conditions(filters),columns_date['data_field'])
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data


def get_conditions(filters):
	select_filters = []
	default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1},['name'])
	select_filters.append("leave_request is not null")
	if default_fiscal_year:
		fiscal_year=frappe.get_last_doc('Fiscal Year')
		default_fiscal_year=fiscal_year.name
		select_filters.append("fiscal_year = %(fiscal_year)s")
	if len(filters.get('department')) > 0:
		select_filters.append("department in %(department)s")
	if len(filters.get('leave_type')) > 0:
		select_filters.append("leave_type in %(leave_type)s")
		
	if len(select_filters) > 0:
		return " WHERE " + " AND ".join(select_filters)
	else:
		return ''
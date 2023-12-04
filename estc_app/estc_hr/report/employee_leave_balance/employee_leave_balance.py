# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns=[]
	columns.append({'fieldname':"employee",'label':"Employee",'fieldtype':'Link','options':'Employee','align':'center','width':130})
	columns.append({'fieldname':"employee_name",'label':"Employee Name",'align':'left','width':130})
	columns.append({'fieldname':"max_leave",'label':"Max Leave",'fieldtype':'Float',"precision":2,'align':'center','width':130})
	columns.append({'fieldname':"use_leave",'label':"Used",'align':'center',"precision":2,'fieldtype':'Float','width':130})
	columns.append({'fieldname':"balance",'label':"Balance","precision":2,'align':'center','fieldtype':'Float','width':130})
	return columns

def get_data(filters):
	data = []
	sql = """
			select 
				employee,
				employee_name,
				COALESCE(sum(max_leave),0) as max_leave,
				COALESCE(SUM(use_leave),0) as use_leave,
				COALESCE(SUM(balance),0) as balance
			from 
				`tabEmployee Attendance Leave Count` 
			{}
			group by
				employee,
				employee_name
	""".format(get_conditions(filters))
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data


def get_conditions(filters):
	select_filters=[]
	if filters.get('fiscal_year'):
		select_filters.append("fiscal_year = %(fiscal_year)s")
	if len(filters.get('department')) > 0:
		select_filters.append("department in %(department)s")
	if len(filters.get('leave_type')) > 0:
		select_filters.append("leave_type in %(leave_type)s")
	if len(select_filters) > 0:
		return " WHERE " + " AND ".join(select_filters)
	else:
		return ''

		

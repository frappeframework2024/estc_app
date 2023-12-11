# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns=[]
	columns.append({'fieldname':"employee",'label':"Employee",'fieldtype':'Link','options':'Employee','align':'center','width':130})
	columns.append({'fieldname':"employee_name",'label':"Employee Name",'align':'left','width':200})
	columns.append({'fieldname':"attendance_date",'label':"Attendance Date",'fieldtype':'Date','align':'center','width':130})
	columns.append({'fieldname':"checkin_time",'label':"Check In Date",'fieldtype':'DateTime','align':'center','width':200})
	columns.append({'fieldname':"checkout_time",'label':"Check Out Date",'fieldtype':'DateTime','align':'center','width':200})
	columns.append({'fieldname':"working_duration",'label':"Working Duration",'fieldtype':'Time','align':'center','width':200})
	columns.append({'fieldname':"status",'label':"Status",'fieldtype':'Data','align':'center','width':60})
	
	return columns

def get_data(filters):
	data = []
	sql = """
			select 
				employee,
				employee_name,
				attendance_date,
				checkin_time,
				checkout_time,
				working_duration
				
			from 
				`tabAttendance` 
			{}
			group by
				employee,
				employee_name,
				status,
				log_type
			order by 
			employee_name,
			checkin_time
	""".format(get_conditions(filters))
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_conditions(filters):
	select_filters=[]
	select_filters.append("is_finger_print = 1")
	if filters.get('start_date') and filters.get('end_date'):
		select_filters.append("attendance_date between %(start_date)s and %(end_date)s")
	if filters.get('status') and filters.get('status') != "All":
		select_filters.append("status = %(status)s")
		
	if len(select_filters) > 0:
		return " WHERE " + " AND ".join(select_filters)
	else:
		return ''
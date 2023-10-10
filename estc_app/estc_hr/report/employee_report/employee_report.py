# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
import datetime
import uuid


def execute(filters=None):
	data = get_report_data(filters)
	return get_columns(filters),data


def get_columns(filters):
	columns = [
		{"fieldname":"name", "label":"Code",'align':'left', "fieldtype":"Link","options":"Employee","show_in_report":1,"width":130},
		{"fieldname":"employee_name", "label":"Name",'align':'left',"show_in_report":1,"width":130},
		{"fieldname":"gender", "label":"Gender",'align':'left',"show_in_report":1},
		{"fieldname":"date_of_birth", "label":"Date Of Birth","fieldtype":"Date",'align':'left',"show_in_report":1},
		{"fieldname":"blood_group", "label":"Blood Group",'align':'left',"show_in_report":1},
		{"fieldname":"marital_status", "label":"Marital Status",'align':'left',"show_in_report":1},
		{"fieldname":"position", "label":"Position",'align':'left',"show_in_report":1},
		{"fieldname":"department", "label":"Department",'align':'left',"show_in_report":1},
		{"fieldname":"employee_type", "label":"Employee Type",'align':'left',"show_in_report":1},
		{"fieldname":"phone_number", "label":"Phone Number",'align':'left',"show_in_report":1},
		{"fieldname":"nationality", "label":"Nationality",'align':'left',"show_in_report":1},
		{"fieldname":"personal_email", "label":"Personal Email",'align':'left',"show_in_report":1},
		{"fieldname":"company_email", "label":"Company Email",'align':'left',"show_in_report":1},
		{"fieldname":"date_of_joining", "label":"Joining Date","fieldtype":"Date",'align':'left',"show_in_report":1},
		{"fieldname":"contract_end_date", "label":"Contract End Date","fieldtype":"Date",'align':'left',"show_in_report":1},
		{"fieldname":"status", "label":"Status",'align':'left',"show_in_report":1},

	]
	return columns

def get_filters(filters):
	sql = ""
	if filters.gender:
		sql = " and emp.gender = %(gender)s"
	if filters.status:
		sql = " and emp.status = %(status)s"
	if filters.department:
		sql = " and emp.department = %(department)s"
	if filters.marital_status:
		sql = " and emp.marital_status = %(marital_status)s"
	if filters.position:
		sql = " and emp.position = %(position)s"
	
	if filters.order_by == "Last Update On" and filters.sort_order == "ASC":
		sql = " order by emp.modified asc"
	elif filters.order_by == "Last Update On" and filters.sort_order == "DESC":
		sql = " order by emp.modified desc"

	elif filters.order_by == "Created On" and filters.sort_order == "ASC":
		sql = " order by emp.creation asc"
	elif filters.order_by == "Created On" and filters.sort_order == "DESC":
		sql = " order by emp.creation desc"
	elif filters.order_by == "ID" and filters.sort_order == "ASC":
		sql = " order by emp.name asc"
	elif filters.order_by == "ID" and filters.sort_order == "DESC":
		sql = " order by emp.name desc"
	elif filters.order_by == "Employee Name" and filters.sort_order == "ASC":
		sql = " order by emp.employee_name asc"
	elif filters.order_by == "Employee Name" and filters.sort_order == "DESC":
		sql = " order by emp.employee_name desc"
	elif filters.order_by == "Employee Code" and filters.sort_order == "ASC":
		sql = " order by emp.name asc"
	elif filters.order_by == "Employee Code" and filters.sort_order == "DESC":
		sql = " order by emp.name desc"
	elif filters.order_by == "Gender" and filters.sort_order == "ASC":
		sql = " order by emp.gender asc"
	elif filters.order_by == "Gender" and filters.sort_order == "DESC":
		sql = " order by emp.gender desc"
	elif filters.order_by == "Status" and filters.sort_order == "ASC":
		sql = " order by emp.status asc"
	elif filters.order_by == "Status" and filters.sort_order == "DESC":
		sql = " order by emp.status desc"
	elif filters.order_by == "Department" and filters.sort_order == "ASC":
		sql = " order by emp.department asc"
	elif filters.order_by == "Department" and filters.sort_order == "DESC":
		sql = " order by emp.department desc"
	elif filters.order_by == "Position" and filters.sort_order == "ASC":
		sql = " order by emp.position asc"
	elif filters.order_by == "Position" and filters.sort_order == "DESC":
		sql = " order by emp.position desc"

	return sql

def get_report_data(filters):
	sql="""
		select 
			name,
			title,
			concat(title,'. ',employee_name) as employee_name,
			gender,
			employee_type,
			date_of_birth,
			blood_group,
			marital_status,
			position,
			department,
			phone_number,
			nationality,
			personal_email,
			company_email,
			date_of_joining,
			contract_end_date,
			status,
   			concat(approve_by_head_department,'-' , 'head department name') as approve_by_head_department
		from `tabEmployee` emp
		where
			1=1  
			{}
		
	""".format(get_filters(filters))

	data =   frappe.db.sql(sql,filters,as_dict=1)
	if filters.group_by:
		group_column = get_group_by_column(filters)
		group_data = sorted(set([d[group_column["data_field"]] for d  in data]))
		report_data = []
		for g in group_data:
			d = g
			report_data.append({
				"indent":0,
				"name": d,
				"is_group":1,
			})
			report_data = report_data +  [d.update({"indent":1}) or d for d in data if d[group_column["data_field"]]==g]
		return report_data
	else:
		return data

def get_group_by_column(filters):

	return  [d for d in group_by_columns() if d["label"] == filters.group_by][0]

def group_by_columns():
	
	return [
		{"fieldname":"group_by","data_field":"approve_by_head_department", "label":"Head Department","fieldtype":"Data"},
		{"fieldname":"group_by","data_field":"title", "label":"Title","fieldtype":"Data"},
		{"fieldname":"group_by","data_field":"marital_status", "label":"Marital Status" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"department", "label":"Department" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"position", "label":"Position" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"status", "label":"Status" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"gender", "label":"Gender" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"employee_type", "label":"Employee Type" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"nationality", "label":"Nationality" ,"fieldtype":"Data" },
		{"fieldname":"group_by","data_field":"blood_group", "label":"Blood Group" ,"fieldtype":"Data" }
	]
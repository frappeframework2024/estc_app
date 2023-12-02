import frappe
from datetime import datetime,timedelta


def execute(filters=None):
	
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns=[]
	columns.append({'fieldname':"name",'label':"Request No",'fieldtype':'Link','options':'Leave Request','align':'center','width':130})
	columns.append({'fieldname':"employee",'label':"Employee",'fieldtype':'Link','options':'Employee','align':'left','width':130})
	columns.append({'fieldname':"leave_type",'label':"Leave Type",'fieldtype':'Data','align':'left','width':130})
	columns.append({'fieldname':"posting_date",'label':" Posting Date",'fieldtype':'Date','align':'left','width':130})
	columns.append({'fieldname':"start_date",'label':"Start",'fieldtype':'Date','align':'center','width':130})
	columns.append({'fieldname':"to_date",'label':"To",'fieldtype':'Date','align':'center','width':130})
	columns.append({'fieldname':"total_leave_days",'label':"Total Leave",'fieldtype':'Data','css_class':'text-bold','align':'center','width':130})
	
	return columns

def get_data(filters):
	data = []
	sql = """
			select 
				name,
				employee,
				leave_type,
				posting_date,
				start_date,
				to_date,
				total_leave_days
			from 
				`tabLeave Request` a
			{0}
	""".format(get_conditions(filters))
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data


def get_conditions(filters):
	select_filters = []
	fiscal_year=frappe.get_last_doc('Fiscal Year')
	select_filters.append("fiscal_year = %(fiscal_year)s")
	select_filters.append("status = 'Approved'")
	select_filters.append("employee = %(employee)s")
		
	if len(select_filters) > 0:
		return " WHERE " + " AND ".join(select_filters)
	else:
		return ''
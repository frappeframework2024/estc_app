# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from estc_app.estc_hr.doctype.employee.employee import get_current_employee
import frappe


def execute(filters=None):
	employee = get_current_employee()["employee"]
	columns = [
		{"fieldname":"leave_type","label":"Leave Type"},
		{"fieldname":"total_leave","label":"Total Leave","fieldtype":"float"},
	]
	
	data = frappe.db.sql("select leave_type,sum(attendance_value) as total_leave  from `tabAttendance` where employee='{}' group by leave_type".format(employee.name if 'name' in employee else ''))

 
	return columns, data

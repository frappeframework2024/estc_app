# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeAttendanceLeaveCount(Document):
	def validate(self):
		self.use_leave = get_use_leave(self)
		self.balance = (self.max_leave or 0) - (self.use_leave or 0)

def get_use_leave(self):
	sql= "select sum(total_leave_days) as total from `tabLeave Request` where employee=%(employee)s and leave_type =%(leave_type)s and fiscal_year = %(fiscal_year)s and status in ('Approved','HR Approved')"
	data = frappe.db.sql(sql, {
		"employee":self.employee,
		"leave_type":self.leave_type,
		"fiscal_year": self.fiscal_year
		},as_dict=1)
	if data:
		return data[0]["total"]
	return 0

@frappe.whitelist()
def get_employee_leave_balance():
	default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1},['name'])
	if not default_fiscal_year:
		fiscal_year=frappe.get_last_doc('Fiscal Year')
		default_fiscal_year=fiscal_year.name
	leave_types = frappe.db.get_list("Leave Type",order_by='sort_order asc',filters={
        'show_in_profile': 1
    },)
	aggregate=''
	for leave_type in leave_types:
		aggregate = aggregate + f",Coalesce(sum(if(leave_type='{leave_type.name}',balance,0)),0) '{leave_type.name}'"
	sql = f"""select 
				CONCAT(employee_name) as employee,
				department
				{aggregate} 
			from `tabEmployee Attendance Leave Count` 
			where fiscal_year = '{default_fiscal_year}'
			group by 
				employee,
				employee_name,
				department
		"""
	data = frappe.db.sql(sql,as_dict=1)
	return tuple(data)
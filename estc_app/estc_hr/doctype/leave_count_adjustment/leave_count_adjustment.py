# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LeaveCountAdjustment(Document):
	def on_submit(self):
		frappe.enqueue(self.update_employee_leave_count)
	def update_employee_leave_count(self):
		for d in self.leave_count:
			if d.leave_count_reference:
				frappe.db.set_value("Employee Attendance Leave Count",d.leave_count_reference,{
					'employee': d.employee,
					'max_leave': d.max_leave,
					'use_leave': d.used,
					'balance': d.max_leave - d.used,
					'fiscal_year': self.fiscal_year,
					'leave_type': self.leave_type
				})
			else:
				doc = frappe.new_doc("Employee Attendance Leave Count")
				doc.employee=d.employee
				doc.max_leave=d.max_leave
				doc.use_leave=d.used
				doc.balance = d.max_leave - d.used
				doc.fiscal_year=self.fiscal_year
				doc.leave_type=self.leave_type
				doc.insert()
				

@frappe.whitelist()
def get_employee_leave_count(fiscal_year,leave_type,default_count):
	filters={"fiscal_year":fiscal_year,"leave_type":leave_type}
	sql = """
		select 
			a.name,
			a.employee_name,
			b.name as leave_count_ref,
			b.max_leave,
			b.balance,
			b.use_leave
		from `tabEmployee` a
		right join `tabEmployee Attendance Leave Count` b
		on a.name = b.employee
		where
			a.status = 'Active' and
			b.leave_type = if(coalesce(%(leave_type)s,'')='',b.leave_type,%(leave_type)s) and
			b.fiscal_year = if(coalesce(%(fiscal_year)s,'')='',b.fiscal_year,%(fiscal_year)s)
		
	"""
	result = frappe.db.sql(sql,filters,as_dict=1)
	
	filters['employees'] = [item["name"] for item in result]
	filters['default_count'] = default_count
	emp_sql = """
				select
					name,
					employee_name,
					NULL as leave_count_ref,
					%(default_count)s as max_leave,
					0 as balance,
					0 as use_leave
				from `tabEmployee`
				where status = 'Active'
				"""
	if len(filters['employees'])>0:
		emp_sql = emp_sql + " and name not in %(employees)s"
	employee_list = frappe.db.sql(emp_sql,filters,as_dict=1)
	return sorted(result+employee_list,key=lambda x:x['employee_name'])
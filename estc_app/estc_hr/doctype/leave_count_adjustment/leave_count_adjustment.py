# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LeaveCountAdjustment(Document):
	pass

@frappe.whitelist()
def get_employee_leave_count(fiscal_year,leave_type):
	filters = {'fiscal_year': fiscal_year, 'leave_type': leave_type}

	sql = """
		select 
			a.name,
			b.name as leave_count_ref,
			b.max_leave,
			b.balance,
			b.use_leave
		from `tabEmployee` a
		left join `tabEmployee Attendance Leave Count` b
		on a.name = b.employee 
		where 
			b.leave_type = if(coalesce('{0}','')='',b.leave_type,{0}) and
			b.fiscal_year = if(coalesce('{1}','')='',b.fiscal_year,{1}) 
	""".format(leave_type,fiscal_year)
	result = frappe.db.sql(sql,as_dict=1)
	return result
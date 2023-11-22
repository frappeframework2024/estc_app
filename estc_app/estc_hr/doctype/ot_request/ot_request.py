# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta

class OTRequest(Document):
	def before_save(self):
		head_department = frappe.db.get_value('Employee', self.employee, ['approve_by_supervisor', 'approve_by_head_department'], as_dict=1)
		supervisor = frappe.db.get_value('Employee', head_department.approve_by_supervisor, ['name', 'employee_name','company_email'], as_dict=1)
		head_department_approver = frappe.db.get_value('Employee', head_department.approve_by_head_department, ['name', 'employee_name','company_email'], as_dict=1)
		self.head_department_approver = head_department_approver.name
		self.head_department_approver_name = head_department_approver.employee_name
		self.head_department_approver_email = head_department_approver.company_email
		if supervisor:
			self.supervisor_approver = supervisor.name
			self.supervisor_approver_name = supervisor.employee_name
			self.supervisor_approver_email = supervisor.company_email
		start =  datetime.strptime(self.start_time, "%H:%M:%S")
		to = datetime.strptime(self.to_time, "%H:%M:%S")
		self.total_hours = to - start
		self.status = self.workflow_state
  
	def on_update_after_submit(self):
		ot_leave_type = frappe.db.get_single_value('HR Setting','ot_leave_type')
		if frappe.db.exists("Employee Attendance Leave Count", {"leave_type": ot_leave_type,"employee":self.employee,"fiscal_year":ot_leave_type}):
			doc = frappe.new_doc('Employee Attendance Leave Count')
			doc.fiscal_year = self.employee
			doc.max_leave = 0
			doc.leave_type=ot_leave_type or None
  

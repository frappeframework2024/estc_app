# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EmployeeAttendanceLeaveCount(Document):
	def validate(self):
		self.balance = (self.max_leave or 0) - (self.use_leave or 0)
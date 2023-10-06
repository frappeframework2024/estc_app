# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ShiftAssignment(Document):
	def validate(self):
		if self.is_new():
			exs = frappe.db.exists("Shift Assignment", {"employee": self.employee,"shift": self.shift})
			if exs:
				frappe.throw(f"Employee {frappe.db.get_value('Employee',self.employee,'employee_name')} could not add to {self.shift} aleady exist")


@frappe.whitelist()
def assign_employee_to_shift(shifts,employees):
	shifts=shifts.split(',')
	employees=employees.split(',')
	if len(shifts) > 0:
		for shift in shifts:
			for emp in employees:
				exs = frappe.db.exists("Shift Assignment", {"employee": emp,"shift": shift})
				if not exs: 
					doc = frappe.new_doc("Shift Assignment")
					doc.shift=shift
					doc.employee=emp
					doc.insert()
					doc.submit()
	return "Shift assignment Successfully"

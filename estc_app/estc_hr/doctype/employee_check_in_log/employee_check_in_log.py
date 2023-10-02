# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeCheckInLog(Document):
	def after_insert(self):
		employee = frappe.db.get_value("Employee",{"attendance_device_id":self.employee_device_id},"name")
		
		doc= frappe.get_doc({
			"doctype":"Attendance",
			"employee":employee,
			"Status":"Preset (AM)",
			"attendance_date":self.check_in_time,
			"checkin_log_id":self.name
		}).insert()
		

@frappe.whitelist()
def employee_checked_in(employee_device_id,
	timestamp,
	device_id=None,
	log_type=None):
    
	doc = frappe.get_doc({
		"employee_device_id":str(employee_device_id),
		"check_in_time":str(timestamp),
		"doctype":"Employee Check In Log",
  		"timestamp":timestamp,
		"device_id":device_id,
		"log_type":log_type
	})
	doc.insert()
	return doc
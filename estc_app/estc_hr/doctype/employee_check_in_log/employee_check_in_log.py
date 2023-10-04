# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeCheckInLog(Document):
	def before_insert(self):

		#frappe.enqueue('')
		employee = frappe.db.get_value("Employee",{"attendance_device_id":self.employee_device_id},["employee_name","employee_code","department","name","position","photo"],as_dict=1)
		if employee:
			self.employee_name = employee.employee_name
			self.title = employee.employee_name
			self.employee = employee.name
			self.department = employee.department
			self.position = employee.position
			self.employee_code = employee.employee_code
			self.photo = employee.photo
		# doc= frappe.get_doc({
		# 	"doctype":"Attendance",
		# 	"employee":employee,
		# 	"Status":"Preset (AM)",
		# 	"attendance_date":self.check_in_time,
		# 	"checkin_log_id":self.name
		# }).insert()
		

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


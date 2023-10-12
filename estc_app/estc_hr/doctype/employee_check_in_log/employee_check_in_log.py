# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta


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

	def after_insert(self):
		fiscal_year = frappe.db.get_value("Fiscal Year",{'is_default': 1})
		shift_assignment = frappe.db.get_value("Shift Assignment",{'employee': self.employee,'fiscal_year':fiscal_year},['shift','holiday'],as_dict=1)
		working_shift=frappe.db.get_value("Working Shift",shift_assignment.shift,['name','late_time','is_haft_working_day','on_duty_time','off_duty_time','beginning_in','ending_in','beginning_out','ending_out','leave_early_time'],as_dict=1)
		if self.log_type == "IN":
			on_duty_in_hour = working_shift.on_duty_time.total_seconds() // 3600 # will return on 8h
			on_duty_in_mins = (working_shift.on_duty_time.total_seconds() % 3600) // 60 + working_shift.late_time #will return 10mins
			check_in_time = datetime.strptime(self.check_in_time,'%Y-%m-%d %H:%M:%S').time()
			check_in_late=0
			attendance_status = "Present"
			if timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins) < timedelta(hours=check_in_time.hour,minutes=check_in_time.minute,seconds=check_in_time.second):	
				if working_shift.off_duty_time >=  timedelta(hours=check_in_time.hour,minutes=check_in_time.minute,seconds=check_in_time.second):
					check_in_late = timedelta(hours=check_in_time.hour,minutes=check_in_time.minute,seconds=check_in_time.second) - timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins)
				else:
					attendance_status='Absent'
			frappe.get_doc(
				{
					'doctype': 'Attendance',
					'employee': self.employee,
					'fiscal_year':fiscal_year,
					'status':attendance_status,
					'attendance_value':working_shift.is_haft_working_day == 1 if working_shift.is_haft_working_day == 0 else 0.5,
					'attendance_date':self.check_in_time,
					'department':self.department,
					'late':check_in_late,
					'photo':self.photo,
					'checkin_log_id':self.name
				}).insert()
		# if self.log_type == "OUT":
		# 	off_duty_in_hour = working_shift.iff_duty_time.total_seconds() // 3600 # will return on 8h
		# 	off_duty_in_mins = (working_shift.on_duty_time.total_seconds() % 3600) // 60 + working_shift.late_time #will return 10mins
		# 	check_in_time = datetime.strptime(self.check_in_time,'%Y-%m-%d %H:%M:%S').time()
		# 	check_in_late=0
		# 	attendance_status = "Present"
		# 	if timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins) < timedelta(hours=check_in_time.hour,minutes=check_in_time.minute,seconds=check_in_time.second):	
		# 		if working_shift.off_duty_time >=  timedelta(hours=check_in_time.hour,minutes=check_in_time.minute,seconds=check_in_time.second):
		# 			check_in_late = timedelta(hours=check_in_time.hour,minutes=check_in_time.minute,seconds=check_in_time.second) - timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins)
		# 		else:
		# 			attendance_status='Absent'
		# 		frappe.get_doc(
		# 			{
		# 				'doctype': 'Attendance',
		# 				'employee': self.employee,
		# 				'fiscal_year':fiscal_year,
		# 				'status':attendance_status,
		# 				'attendance_value':working_shift.is_haft_working_day == 1 if working_shift.is_haft_working_day == 0 else 0.5,
		# 				'attendance_date':self.check_in_time,
		# 				'department':self.department,
		# 				'late':check_in_late,
		# 				'photo':self.photo,
		# 				'checkin_log_id':self.name
		# 			}).insert()

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


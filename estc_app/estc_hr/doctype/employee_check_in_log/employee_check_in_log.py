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
			self.posting_date = datetime.now().date()

	def after_insert(self):
		self.insert_attendance()		

	def insert_attendance(self):
		fiscal_year = frappe.db.get_value("Fiscal Year",{'is_default': 1})
		shift_assignment = frappe.db.get_list("Shift Assignment",filters={'employee': self.employee,'fiscal_year':fiscal_year},fields=['shift'])
		check_date = datetime.strptime(self.check_in_time,'%Y-%m-%d %H:%M:%S')
		finger_print_time = check_date.time()
		shift=[d.shift for d in shift_assignment]
		working_shift=frappe.db.get_list("Working Shift",filters=[['name', 'in', shift]],fields=['name','late_time','is_haft_working_day','on_duty_time','off_duty_time','beginning_in','ending_in','beginning_out','ending_out','leave_early_time','holiday'])
		
		punch_direction = None
		check_in_shift={}
		for d in working_shift:
			timedelta_finger_print = timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second)
			if d.beginning_in <= timedelta_finger_print <= d.ending_in:
				punch_direction = "IN"
				check_in_shift=d
				break
			elif d.beginning_out <= timedelta_finger_print <= d.ending_out:
				punch_direction = "OUT"
				check_in_shift=d
				break
		
		working_shift=check_in_shift
		if punch_direction == "IN":
			if working_shift:
				on_duty_in_hour = working_shift.on_duty_time.total_seconds() // 3600 # will return on 8h
				on_duty_in_mins = (working_shift.on_duty_time.total_seconds() % 3600) // 60 + working_shift.late_time #will return 10mins		
				check_in_late=0
				holiday = frappe.db.sql(f"select date from `tabHoliday Schedule` where date = '{check_date.date()}' and parent = {working_shift.holiday}",as_dict=1)
				if len(holiday)>=1:
					return
				attendance_status = "Present"
				#check if employee check on duty time
				if timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins) < timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second):	
					#check if employee check in late
					if working_shift.off_duty_time >=  timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second):
						check_in_late = timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second) - timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins)

				get_existed_attendance = frappe.db.exists("Attendance", {"shift":working_shift.name,"log_type":"IN","attendance_date": datetime.strptime(self.check_in_time,'%Y-%m-%d %H:%M:%S').date(),'employee':self.employee,'shift':working_shift.name})

				if not get_existed_attendance:
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
							'leave_early':0,
							'shift':working_shift.name,
							'log_type':'IN',
							'photo':self.photo,
							'checkin_time':self.check_in_time,
							'checkin_log_id':self.name
						}).insert()
				else:
					if timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second) <= working_shift.ending_in : 
						#Check in After insert attendance Absent update status if check in before ending in
						attendance = frappe.get_doc("Attendance",get_existed_attendance)
						attendance.status = 'Present'
						attendance.checkin_log_id = self.name
						attendance.save()
		elif punch_direction == "OUT":
			check_out_early=0
			attendance_status = "Present"
			if working_shift:
				begin_out_hour = working_shift.off_duty_time.total_seconds() // 3600 # will return on 8h
				begin_out_mins = (working_shift.off_duty_time.total_seconds() % 3600*6) // 60 - working_shift.leave_early_time #will return 10mins
				#check if employee check on duty time
				if timedelta(hours=begin_out_hour,minutes=begin_out_mins) > timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second):	
					#check if employee check in late
					check_out_early = timedelta(hours=begin_out_hour,minutes=begin_out_mins) - timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second)
				holiday = frappe.db.sql(f"select date from `tabHoliday Schedule` where date = '{check_date.date()}' and parent = {working_shift.holiday}",as_dict=1)
				if len(holiday)>=1:
					return
				get_existed_attendance = frappe.db.exists("Attendance", {"shift":working_shift.name,"log_type":"OUT","attendance_date": datetime.strptime(self.check_in_time,'%Y-%m-%d %H:%M:%S').date(),'employee':self.employee})
				
				if not get_existed_attendance:
					frappe.get_doc(
						{
							'doctype': 'Attendance',
							'employee': self.employee,
							'fiscal_year':fiscal_year,
							'status':attendance_status,
							'attendance_value':working_shift.is_haft_working_day == 1 if working_shift.is_haft_working_day == 0 else 0.5,
							'attendance_date':self.check_in_time,
							'department':self.department,
							'late':0,
							'shift':working_shift.name,
							'log_type':'OUT',
							'leave_early':check_out_early,
							'checkin_time':self.check_in_time,
							'photo':self.photo,
							'checkin_log_id':self.name
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

def get_attendance_punch(check_time,working_shift):
	if working_shift:
		check_time = timedelta(hours=check_time.hour,minutes=check_time.minute,seconds=check_time.second)
		beginning_in = working_shift.beginning_in
		ending_in =working_shift.ending_in
		beginning_out = working_shift.beginning_out
		ending_out =working_shift.ending_out
		if beginning_in <= check_time <= ending_in:
			return "IN"
		if beginning_out <= check_time <= ending_out:
			return 'OUT'
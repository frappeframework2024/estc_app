# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta


class EmployeeCheckInLog(Document):
	def before_insert(self):
		
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
		
		frappe.enqueue("estc_app.estc_hr.doctype.employee_check_in_log.employee_check_in_log.insert_attendance",self=self)
		# insert_attendance(self)

def insert_attendance(self):
	
	fiscal_year = frappe.db.get_value("Fiscal Year",{'is_default': 1})
	shift_assignment = frappe.db.get_list("Shift Assignment",filters={'employee': self.employee,'fiscal_year':fiscal_year},fields=['shift'])
	check_date = datetime.strptime(self.check_in_time,'%Y-%m-%d %H:%M:%S')
	finger_print_time = check_date.time()
	shift=[d.shift for d in shift_assignment]
	working_shift=frappe.db.get_list("Working Shift",filters=[['name', 'in', shift]],fields=['name','attendance_value','late_time','is_haft_working_day','on_duty_time','off_duty_time','beginning_in','ending_in','beginning_out','ending_out','leave_early_time','holiday'])
	
	punch_direction = None
	check_in_shift={}
	for d in working_shift:
		timedelta_finger_print = timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second)
		#Definde Punch Direction
		if d.beginning_in <= timedelta_finger_print and timedelta_finger_print <= d.ending_in:
			punch_direction = "IN"
			check_in_shift=d
			break
		elif d.beginning_out <= timedelta_finger_print and  timedelta_finger_print <= d.ending_out:
			punch_direction = "OUT"
			check_in_shift=d
			break
	
	working_shift=check_in_shift

	on_duty_in_hour = working_shift.on_duty_time.total_seconds() // 3600 # will return on 8h
	
	on_duty_in_mins = (working_shift.on_duty_time.total_seconds() % 3600) // 60 + working_shift.late_time #will return 10mins		
	#check exist if check in after auto insert Absent Attendance
	absents = frappe.db.exists("Attendance", {"employee": self.employee,'fiscal_year':fiscal_year,'attendance_date':check_date.date(),'status':'Absent'})
	check_in_late=0
	if absents:
		if timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins) < timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second):	
			#check if employee check in late
			if working_shift.off_duty_time >=  timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second):
				check_in_late = timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second) - timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins)
		frappe.db.set_value('Attendance', absents, {
				'status':'Present',
				'attendance_value':working_shift.attendance_value,
				'department':self.department,
				'late':check_in_late,
				'leave_early':0,
				'shift':working_shift.name,
				'log_type':punch_direction or 0,
				'photo':self.photo,
				'checkin_time':self.check_in_time,
				'checkin_log_id':self.name
		})
		return

	if punch_direction == "IN":
		if working_shift:
			
			check_in_late=timedelta()
			holiday = frappe.db.sql(f"select date from `tabHoliday Schedule` where date = '{check_date.date()}' and parent = {working_shift.holiday}",as_dict=1)
			if len(holiday)>=1:
				return
			attendance_status = "Present"
			#check if employee check on duty time
			if timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins) < timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second):
				#check if employee check in late
				if working_shift.off_duty_time >=  timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second):
					check_in_late = timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second) - timedelta(hours=on_duty_in_hour,minutes=on_duty_in_mins)
			#prenvent check in multiple times
			get_existed_attendance = frappe.db.exists("Attendance", {"shift":working_shift.name,"log_type":"IN","attendance_date": datetime.strptime(self.check_in_time,'%Y-%m-%d %H:%M:%S').date(),'employee':self.employee,'shift':working_shift.name})

			if not get_existed_attendance:
				frappe.get_doc(
					{
						'doctype': 'Attendance',
						'employee': self.employee,
						'fiscal_year':fiscal_year,
						'status':attendance_status,
						'attendance_date':self.check_in_time,
						'department':self.department,
						'late':check_in_late.total_seconds(),
						'shift':working_shift.name,
						'photo':self.photo,
						'checkin_time':self.check_in_time,
						'checkin_log_id':self.name,
						'is_finger_print':1
					}).insert()
			else:
				if timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second) <= working_shift.ending_in : 
					#Check in After insert attendance Absent update status if check in before ending in
					attendance = frappe.get_doc("Attendance",get_existed_attendance)
					attendance.status = 'Present'
					attendance.checkin_log_id = self.name
					attendance.save()
	elif punch_direction == "OUT":
		
		check_out_early=timedelta()
		attendance_status = "Present"
		if working_shift:
			begin_out_hour = working_shift.off_duty_time.total_seconds() // 3600 # will return on 8h
			begin_out_mins = ((working_shift.off_duty_time.total_seconds() % 3600*60) // 60) - working_shift.leave_early_time #will return in mins
			#check if employee check on duty time
			if timedelta(hours=begin_out_hour,seconds=begin_out_mins) > timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second):	
				#check if employee check in late
				check_out_early = timedelta(hours=begin_out_hour,seconds=begin_out_mins) - timedelta(hours=finger_print_time.hour,minutes=finger_print_time.minute,seconds=finger_print_time.second)
			holiday = frappe.db.sql(f"select date from `tabHoliday Schedule` where date = '{check_date.date()}' and parent = {working_shift.holiday}",as_dict=1)
			if len(holiday)>=1:
				return
			get_existed_attendance = frappe.db.exists("Attendance", {"shift":working_shift.name,"log_type":"IN","attendance_date": datetime.strptime(self.check_in_time,'%Y-%m-%d %H:%M:%S').date(),'employee':self.employee})
			if get_existed_attendance:
				doc = frappe.get_doc("Attendance",get_existed_attendance)
				doc.checkout_time = self.check_in_time
				attendance_value,duration = get_attendance_value(self.check_in_time,doc.checkin_time)
				doc.attendance_value=attendance_value
				doc.working_duration=duration
				doc.save()
			else:
				frappe.get_doc(
					{
						'doctype': 'Attendance',
						'employee': self.employee,
						'fiscal_year':fiscal_year,
						'status':attendance_status,
						'attendance_date':self.check_in_time,
						'department':self.department,
						'shift':working_shift.name,
						'leave_early':check_out_early.total_seconds(),
						'checkout_time':self.check_in_time,
						'photo':self.photo,
						'checkin_log_id':self.name,
						'is_finger_print':1,
						
					}).insert()


def get_attendance_value(checkout_time,checkin_time):
	break_from = frappe.db.get_single_value('HR Setting', 'break_from')
	break_to = frappe.db.get_single_value('HR Setting', 'break_to')
	total_work_per_day = frappe.db.get_single_value('HR Setting', 'total_work_per_day')
	checkout_date = datetime.strptime(checkout_time,'%Y-%m-%d %H:%M:%S')
	duration = (break_from - timedelta(hours=checkin_time.hour,minutes=checkin_time.minute,seconds=checkin_time.second) + timedelta(hours=checkout_date.hour,minutes=checkout_date.minute,seconds=checkout_date.second) - break_to)
	attendance_value = duration/timedelta(hours=total_work_per_day)
	frappe.msgprint(str(attendance_value))
	frappe.msgprint(str(duration))
	return attendance_value,duration

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
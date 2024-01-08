# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta

class Attendance(Document):
	pass

@frappe.whitelist()
def insert_absent_attendance_queue():
	frappe.enqueue('estc_app.estc_hr.doctype.attendance.attendance.insert_attendance')

def insert_attendance():
	sql = """
		select 
			name,
			attendance_device_id,
			department,
			photo
		from `tabEmployee`
		where has_no_attendance_device_id = 0 and
			name not in (select 
							employee 
						from `tabAttendance` 
						where DATE(attendance_date) = '{}')
	""".format(datetime.now().date())
	employee_list_not_check_in = frappe.db.sql(sql,as_dict=1)
	
	default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1})
	for emp in employee_list_not_check_in:
		shift_assignment = frappe.db.get_value('Shift Assignment', {'employee': emp.name,'fiscal_year': default_fiscal_year}, ['holiday','shift'],as_dict=1)
		if shift_assignment:
			day_off = frappe.db.sql("""select name from `tabHoliday Schedule` where parent = '{0}' and date = '{1}' and is_day_off = 1""".format(shift_assignment.holiday,datetime.now().date()))
			working_shift=frappe.db.get_value("Working Shift",shift_assignment.shift,['name','late_time','on_duty_time','off_duty_time','beginning_in','ending_in','beginning_out','ending_out','leave_early_time'],as_dict=1)
			if len(day_off)==0:
				frappe.get_doc(
					{
						'doctype': 'Attendance',
						'employee': emp.name,
						'fiscal_year':default_fiscal_year,
						'status':'Absent',
						'attendance_date':datetime.today().date(),
						'late' : None,
						'leave_early' : None,
						'finger_print': 1,
						'employee_device_id':emp.attendance_device_id,
						'department':emp.department,
						'photo':emp.photo
					}).save()
				frappe.db.commit()

@frappe.whitelist()
def insert_out_attendance():
	sql = """
		select 
			name,
			attendance_device_id,
			department,
			photo
		from `tabEmployee`
		where has_no_attendance_device_id = 0 and
			name not in (select 
							employee 
						from `tabAttendance` 
						where DATE(attendance_date) = '{}')
	""".format(datetime.now().date())
	employee_list_not_check_out = frappe.db.sql(sql,as_dict=1)
	fiscal_year = frappe.db.get_value('Fiscal Year', {'is_default': 1})
	if not fiscal_year:
		fiscal_year = frappe.get_last_doc('Fiscal Year')
	for emp in employee_list_not_check_out:

		working_shift = frappe.db.get_value('Shift Assignment', {'employee': emp,'fiscal_year':fiscal_year}, ['shift'], as_dict=1)

		doc = frappe.new_doc("Attendance")
		doc.employee=emp
		doc.attendance = datetime.now().date()
		doc.log_type = 'OUT'
		doc.late = None
		doc.leave_early = None
		doc.finger_print = 1
		doc.attendance_value = frappe.db.get_value('Working Shift',working_shift.shift,['attendance_value'])
		doc.working_shift = working_shift.shift
		att = frappe.db.sql(f"""select employee from `tabAttendance` where DATE(attendance_date) = '{datetime.now().date()}'""",as_dict=1)
		#check employee has check in or not in this day
		if len(att)>0:
			doc.status = 'Present'
		else:
			doc.status = 'Absent'
		doc.insert()		
	
	return employee_list_not_check_out



	

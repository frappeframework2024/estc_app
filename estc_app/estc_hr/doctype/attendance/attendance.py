# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta
from frappe.utils import  today, getdate ,now
class Attendance(Document):
	def validate(self):
		pass


@frappe.whitelist()
def insert_absent_attendance_queue():
    # check absent full day
	frappe.enqueue('estc_app.estc_hr.doctype.attendance.attendance.insert_attendance')
	frappe.enqueue('estc_app.estc_hr.doctype.attendance.attendance.insert_attendance_absent_am')
	frappe.enqueue('estc_app.estc_hr.doctype.attendance.attendance.insert_attendance_absent_pm')

	

@frappe.whitelist()
def insert_attendance():
	default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1})
	sql = """
		select 
			a.name,
			a.attendance_device_id,
			a.department,
			a.photo,
			b.shift,
			b.holiday
		from `tabEmployee` a
			inner  join `tabShift Assignment` b on a.name = b.employee  
  		where
			b.fiscal_year ='{fiscal_year}' and 
			a.has_no_attendance_device_id = 0 and
			a.status = 'Active' and
			a.name not in (
				select 
    				employee 
				from `tabAttendance` att 
    			where 

       				DATE(att.attendance_date) = '{date}'
           )
	""".format( fiscal_year = default_fiscal_year , date = datetime.now().date())

	employee_list_not_check_in = frappe.db.sql(sql,as_dict=1)

	default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1})

	for emp in employee_list_not_check_in:
		day_off = frappe.db.sql("""select name from `tabHoliday Schedule` where parent = '{0}' and date = '{1}' and is_day_off = 1""".format(emp.holiday,datetime.now().date()))
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
					"shift":emp.shift,
					'attendance_devide_id':emp.attendance_device_id,
					'department':emp.department,
					'photo':emp.photo
				}).save()
			frappe.db.commit()

@frappe.whitelist()
def insert_attendance_absent_am():
	default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1})
	sql = """
		select 
			a.name,
			a.attendance_device_id,
			a.department,
			a.photo,
			b.shift,
			b.holiday
		from `tabEmployee` a
			inner  join `tabShift Assignment` b on a.name = b.employee  
  		where
			b.fiscal_year ='{fiscal_year}' and 
			a.has_no_attendance_device_id = 0 and
			a.status = 'Active' and
			a.name  in (
				select 
    				employee 
				from `tabAttendance` att 
    			where 
					status = 'On Leave Half Day PM' and 
       				DATE(att.attendance_date) = '{date}'
           ) and 
           a.name  not in  (
				select 
    				employee 
				from `tabAttendance` att 
    			where 
					status = 'Absent (AM)' and 
       				DATE(att.attendance_date) = '{date}'
           )
           
	""".format( fiscal_year = default_fiscal_year , date = datetime.now().date())

	employee_on_leave_pm = frappe.db.sql(sql,as_dict=1)


	default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1})

	for emp in employee_on_leave_pm:
		day_off = frappe.db.sql("""select name from `tabHoliday Schedule` where parent = '{0}' and date = '{1}' and is_day_off = 1""".format(emp.holiday,datetime.now().date()))
		if len(day_off)==0:
			frappe.get_doc(
				{
					'doctype': 'Attendance',
					'employee': emp.name,
					'fiscal_year':default_fiscal_year,
					'status':'Absent (AM)',
     				'attendance_value':0.5,
					'attendance_date':datetime.today().date(),
					'late' : None,
					'leave_early' : None,
					'finger_print': 1,
					"shift":emp.shift,
					'attendance_devide_id':emp.attendance_device_id,
					'department':emp.department,
					'photo':emp.photo
				}).save()
			frappe.db.commit()


@frappe.whitelist()
def insert_attendance_absent_pm():
	default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1})
	sql = """
		select 
			a.name,
			a.attendance_device_id,
			a.department,
			a.photo,
			b.shift,
			b.holiday
		from `tabEmployee` a
			inner  join `tabShift Assignment` b on a.name = b.employee  
  		where
			b.fiscal_year ='{fiscal_year}' and 
			a.has_no_attendance_device_id = 0 and
			a.status = 'Active' and
			a.name  in (
				select 
    				employee 
				from `tabAttendance` att 
    			where 
					status = 'On Leave Half Day AM' and 
       				DATE(att.attendance_date) = '{date}'
           ) and 
           a.name  not in  (
				select 
    				employee 
				from `tabAttendance` att 
    			where 
					status = 'Absent (PM)' and 
       				DATE(att.attendance_date) = '{date}'
           )
           
	""".format( fiscal_year = default_fiscal_year , date = datetime.now().date())

	employee_on_leave_pm = frappe.db.sql(sql,as_dict=1)


	default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1})

	for emp in employee_on_leave_pm:
		# check holiday condition
		day_off = frappe.db.sql("""select name from `tabHoliday Schedule` where parent = '{0}' and date = '{1}' and is_day_off = 1""".format(emp.holiday,datetime.now().date()))
		if len(day_off)>0:
			continue
		
		# check running time we run this only after pm_ending_in hour in working shift table
		current_time =  datetime.now()
		pm_ending_in = frappe.get_cached_value("Working Shift", emp["shift"],"pm_ending_in" )
		pm_ending_in =   "{} {}".format(frappe.utils.today(), pm_ending_in)
		pm_ending_in =datetime.strptime(pm_ending_in, '%Y-%m-%d %H:%M:%S')
		if pm_ending_in>current_time:
			continue

		frappe.get_doc(
			{
				'doctype': 'Attendance',
				'employee': emp.name,
				'fiscal_year':default_fiscal_year,
				'status':'Absent (PM)',
				'attendance_value':0.5,
				'attendance_date':datetime.today().date(),
				'late' : None,
				'leave_early' : None,
				'finger_print': 1,
				"shift":emp.shift,
				'attendance_devide_id':emp.attendance_device_id,
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
			doc.status = '1nt'
		else:
			doc.status = 'Absent'
		doc.insert()		
	
	return employee_list_not_check_out

@frappe.whitelist()
def testing():
	pass
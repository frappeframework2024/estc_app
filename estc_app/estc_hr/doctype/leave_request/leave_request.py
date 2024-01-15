# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe 
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import add_to_date, getdate
from datetime import datetime


class LeaveRequest(Document):
	def validate(self):
		
		self.fiscal_year = frappe.db.get_value("Fiscal Year", {'is_default': 1},"name")
		leave_type = frappe.get_doc("Leave Type", self.leave_type)
		leave_count = frappe.db.sql("select * from `tabEmployee Attendance Leave Count` where employee='{}' and leave_type = '{}' and fiscal_year='{}'".format(self.employee, self.leave_type, self.fiscal_year),as_dict=1)
		self.hr_email = frappe.db.get_single_value("HR Setting","hr_email")
		self.director_email = frappe.db.get_single_value("HR Setting","director_email")
		# frappe.throw(str(leave_type.allow_negative))
		if leave_count:
			for d in leave_count:
				total_leave = frappe.db.sql("select sum(max_leave) total_leave from `tabEmployee Attendance Leave Count` where employee='{}' and fiscal_year='{}'".format(self.employee,d.fiscal_year),as_dict=1)[0]["total_leave"] or 0
				leave_day = d.use_leave + self.total_leave_days
				if leave_type.allow_negative == 1 and leave_day < total_leave:
					pass
				if leave_type.allow_negative == 0 and leave_day > d.max_leave:
					frappe.throw("You use all your leave day on <strong>{}</strong>".format(self.leave_type))
		else:
			frappe.throw("Please update max leave for {} in employee detail".format(self.leave_type))

		if self.docstatus==0:
			self.status ='Draft'
		employee = frappe.db.get_value("Employee",self.employee,['approve_by_supervisor','approve_by_head_department', 'name','employee_name'], as_dict=1)
		head_department = frappe.db.get_value("Employee",employee.approve_by_head_department,['approve_by_supervisor','employee_name','approve_by_head_department', 'name','company_email'],as_dict=1)
		supervisor = frappe.db.get_value("Employee",employee.approve_by_supervisor,['approve_by_supervisor','employee_name','approve_by_head_department', 'name','company_email'],as_dict=1)
		
		if not head_department:
			frappe.throw(_(f'Count not find head department for {frappe.bold(employee.employee_name)}'))
		self.head_department_approver = head_department.name
		self.head_department_approver_name = head_department.employee_name
		self.head_department_approver_email = head_department.company_email
		if supervisor:
			self.supervisor_approver = supervisor.name
			self.supervisor_approver_name = supervisor.employee_name
			self.supervisor_approver_email = supervisor.company_email

	def before_insert(self):
		if self.emergency_request==0:
			annual_leave_type = frappe.db.get_single_value("HR Setting","annual_leave_type")
			if self.leave_type == annual_leave_type :
				validates = frappe.db.get_all('Leave Request Days Validate', fields=['min_leave_days', 'max_leave_days','request_days'])
				current_date = datetime.strptime(str(getdate()), "%Y-%m-%d")
				start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
				date_diff = start_date - current_date
				request_valid =[d for d in validates if d.min_leave_days < self.total_leave_days <= d.max_leave_days]
				if len(request_valid) > 0:
					if date_diff.days < request_valid[0].request_days:
						frappe.throw(f'Your request not allow. Please request {frappe.bold(request_valid[0].request_days)} days or more before leave date')

	def on_update_after_submit(self):
		
		#frappe.throw(self.status)
		# to do add rescord to attench list
		leave_status = frappe.get_doc("Leave Status", self.status)
		sick_leave = frappe.db.get_single_value("HR Setting","sick_leave_type")
		if self.leave_type != sick_leave:
			
			if leave_status.delete_attendance_record==1:
				frappe.db.sql("delete from `tabAttendance` where leave_request='{}'".format(self.name))
			
			if leave_status.create_attendance_record==1:
				
				date = getdate(self.start_date)
				holiday_list = frappe.db.sql(f"select date from `tabHoliday Schedule` where date between '{self.start_date}' and '{self.to_date}' and is_day_off=1",as_dict=1)
				
				while date<=getdate(self.to_date):
					if any(item["date"] == date for item in holiday_list):
						date = add_to_date(date,days=1)
						continue
					doc = {
						"doctype":"Attendance",
						"fiscal_year":self.fiscal_year,
						"employee":self.employee,
						"attendance_date": date,
						"leave_type":self.leave_type,
						"leave_request":self.name,
						'late':None,
						'checkin_time':None,
						"reason":self.reason
					}
					
					if date == getdate(self.start_date) and self.is_start_date_half_day == 1 and self.is_start_date_period == "AM":
						doc["attendance_value"] = 0.5
						doc["status"] = "On Leave Half Day AM"

					elif date == getdate(self.start_date) and self.is_start_date_half_day == 1 and self.is_start_date_period == "PM":
						doc["attendance_value"] = 0.5
						doc["status"] = "On Leave Half Day PM"

					else:
						doc["attendance_value"] =1
						doc["status"] = "On Leave"
						
					
					if date == getdate(self.to_date) and self.is_to_date_half_day==1 and self.to_date_period=="AM":
						doc["attendance_value"] = 0.5
						doc["status"] = "On Leave Half Day AM"

					elif date == getdate(self.to_date) and self.is_to_date_half_day==1 and self.to_date_period=="PM":
						doc["attendance_value"] = 0.5
						doc["status"] = "On Leave Half Day PM"

					frappe.get_doc(doc).insert()
					
					date = add_to_date(date,days=1)
				update_leave_balance(self)
		elif self.leave_type == sick_leave:

			if leave_status.delete_attendance_record==1:
				frappe.db.sql("delete from `tabAttendance` where leave_request='{}'".format(self.name))
			
			if leave_status.create_attendance_record==1:
				
				date = getdate(self.start_date)
				annual_leave_type = frappe.db.get_single_value("HR Setting","annual_leave_type")
				holiday_list = frappe.db.sql(f"select date from `tabHoliday Schedule` where date between '{self.start_date}' and '{self.to_date}' and is_day_off=1",as_dict=1)
				leave_type = self.leave_type  if self.status == "HR Approved" else annual_leave_type
				if self.status != "Approved":
					
					while date<=getdate(self.to_date):
						if any(item["date"] == date for item in holiday_list):
							date = add_to_date(date,days=1)
							continue
						doc = {
							"doctype":"Attendance",
							"fiscal_year":self.fiscal_year,
							"employee":self.employee,
							"attendance_date": date,
							"leave_type":leave_type,
							"leave_request":self.name,
							'late':None,
							'checkin_time':None,
							"reason":self.reason
						}
						
						if date == getdate(self.start_date) and self.is_start_date_half_day == 1 and self.is_start_date_period == "AM":
							doc["attendance_value"] = 0.5
							doc["status"] = "On Leave Half Day AM"

						elif date == getdate(self.start_date) and self.is_start_date_half_day == 1 and self.is_start_date_period == "PM":
							doc["attendance_value"] = 0.5
							doc["status"] = "On Leave Half Day PM"

						else:
							doc["attendance_value"] =1
							doc["status"] = "On Leave"
							
						
						if date == getdate(self.to_date) and self.is_to_date_half_day==1 and self.to_date_period=="AM":
							doc["attendance_value"] = 0.5
							doc["status"] = "On Leave Half Day AM"

						elif date == getdate(self.to_date) and self.is_to_date_half_day==1 and self.to_date_period=="PM":
							doc["attendance_value"] = 0.5
							doc["status"] = "On Leave Half Day PM"
						
						frappe.get_doc(doc).insert()
						
						date = add_to_date(date,days=1)
			update_leave_balance(self)
		# frappe.enqueue("estc_app.estc_hr.doctype.leave_request.leave_request.update_leave_balance", queue='short', self =self)
			
@frappe.whitelist()
def update_leave_balance(self):
	employee_attendance = frappe.db.sql("select * from `tabEmployee Attendance Leave Count` where employee='{}' and fiscal_year='{}'".format(self.employee, self.fiscal_year),as_dict=1)
	 
	for e in employee_attendance:
		total_leave = frappe.db.sql("select sum(attendance_value) total_leave from `tabAttendance` where employee='{}' and leave_type='{}' and fiscal_year='{}'".format(self.employee,e.leave_type,e.fiscal_year),as_dict=1)[0]["total_leave"] or 0
		
		sql="update `tabEmployee Attendance Leave Count` set use_leave={0}, balance=max_leave-{0} where name='{1}'"
		sql = sql.format(total_leave, e.name)
		 
		frappe.db.sql(sql)
		 

	frappe.db.commit()

@frappe.whitelist()
def get_events(start, end, filters=None):
	from frappe.desk.calendar import get_event_conditions
	department = frappe.db.get_list("Department",pluck='name')
	conditions = get_event_conditions("Leave Request", [["Leave Request","department","in",department],["Leave Request","status","in",["Approved","Request"]]])
	
	sql = """
			select 
   				start_date as start,
				to_date as end,
				name,
				color as backgroundColor,
				CONCAT(`name`,"-",`employee_name`, ' ', `leave_type`) as title,
				status as leave_status
    		from `tabLeave Request` 
      		where start_date between "{start}" and "{end}" 
        		{conditions}
		""".format(conditions=conditions,start=start,end=end)

	holiday_holiday="""
			select 
   				min(date) as start,
      			max(date) as end,
      			description as title,
				if(is_day_off=1,"#f52047","#f5cc14") as backgroundColor
      		from `tabHoliday` 
			where date between "{start}" and "{end}" 
        	group by description
		""".format(start=start,end=end)
	holiday = frappe.db.sql(holiday_holiday,as_dict=True)
	data = frappe.db.sql(sql,as_dict=True)
	return data+holiday

@frappe.whitelist()
def get_leave_count(start,end,fiscal_year):
	holiday_setting = frappe.db.get_value("Holiday Setting",{'fiscal_year':fiscal_year})
	sql = """
		select 
  			date 
     	from 
    	`tabHoliday Schedule` 
     	where 
      	date between '{0}' and '{1}' and parent = '{2}'
    """.format(start,end,holiday_setting)
	result =  frappe.db.sql(sql)
	return result or []
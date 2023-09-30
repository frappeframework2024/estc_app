# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe 
from frappe.model.document import Document
from frappe.utils.data import add_to_date, getdate


class LeaveRequest(Document):
	def validate(self):
		leave_type = frappe.get_doc("Leave Type", self.leave_type)
		leave_count = frappe.db.sql("select * from `tabEmployee Attendance Leave Count` where parent='{}' and leave_type = '{}' and fiscal_year='{}'".format(self.employee, self.leave_type, self.fiscal_year),as_dict=1)
		
		# frappe.throw(str(leave_type.allow_negative))
		if leave_count:
			for d in leave_count:
				total_leave = frappe.db.sql("select sum(max_leave) total_leave from `tabEmployee Attendance Leave Count` where parent='{}' and fiscal_year='{}'".format(self.employee,d.fiscal_year),as_dict=1)[0]["total_leave"] or 0
				leave_day = d.use_leave + self.total_leave_days
				if leave_type.allow_negative == 1 and leave_day < total_leave:
					pass
				if leave_type.allow_negative == 0 and leave_day > d.max_leave:
					frappe.throw("You use all your leave day on <strong>{}</strong>".format(self.leave_type))
		else:
			frappe.throw("Please update max leave for {} in employee detail".format(self.leave_type))

		if self.docstatus==0:
			self.status ='Draft'
			
	def on_submit(self):
		pass
		# frappe.sendmail(recipients=[self.approver_email],
		# 	subject="Leave approval",
		# 	message= "Pls approve my leave requeast"
		# )
	
	def on_update_after_submit(self):
		 
		# frappe.throw(self.status)
		# to do add rescord to attench list
		leave_status = frappe.get_doc("Leave Status", self.status)

		if leave_status.delete_attendance_record==1:
			frappe.db.sql("delete from `tabAttendance` where leave_request='{}'".format(self.name))
	 
		if leave_status.create_attendance_record==1:
			
			date = getdate(self.start_date)
			 
			while date<=getdate(self.to_date):
				# frappe.throw(self.employee)
				doc = {
					"doctype":"Attendance",
					"fiscal_year":self.fiscal_year,
					"employee":self.employee,
					"attendance_date": date,
					"leave_request":self.name,
					
					"reason":self.reason
				}
				if date == getdate(self.start_date) and self.is_start_date_half_day==1:
					doc["attendance_value"] = 0.5
					doc["status"] = "On Leave Half Day"

				else:
					doc["attendance_value"] =1
					doc["status"] = "On Leave"
					
				
				if date == getdate(self.to_date) and self.is_to_date_half_day==1:
					doc["attendance_value"] = 0.5
					doc["status"] = "On Leave Half Day"

				else:
					doc["attendance_value"] =1
					doc["status"] = "On Leave"

				frappe.get_doc(doc).insert()
				date = add_to_date(date,days=1)
				
		# update_leave_balance(self)

		

		frappe.enqueue("estc_app.estc_hr.doctype.leave_request.leave_request.update_leave_balance", queue='short', self =self)

@frappe.whitelist()
def update_leave_balance(self):
	employee_attendance = frappe.db.sql("select * from `tabEmployee Attendance Leave Count` where parent='{}' and fiscal_year='{}'".format(self.employee, self.fiscal_year),as_dict=1)
	 
	for e in employee_attendance:
		total_leave = frappe.db.sql("select sum(attendance_value) total_leave from `tabAttendance` where employee='{}' and leave_type='{}' and fiscal_year='{}'".format(self.employee,e.leave_type,e.fiscal_year),as_dict=1)[0]["total_leave"] or 0
		
		sql="update `tabEmployee Attendance Leave Count` set use_leave={0}, balance=max_leave-{0} where name='{1}'"
		sql = sql.format(total_leave, e.name)
		 
		frappe.db.sql(sql)
		 

	frappe.db.commit()

@frappe.whitelist()
def get_events(start, end, filters=None):
	from frappe.desk.calendar import get_event_conditions
	
	conditions = get_event_conditions("Leave Request", [["Leave Request","status","in",["Approved","Request"],False]])
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
				"red" as backgroundColor
      		from `tabHoliday` 
			where date between "{start}" and "{end}" 
        	group by description
		""".format(start=start,end=end)
	holiday = frappe.db.sql(holiday_holiday,as_dict=True)
	data = frappe.db.sql(sql,as_dict=True)
	return data+holiday





		



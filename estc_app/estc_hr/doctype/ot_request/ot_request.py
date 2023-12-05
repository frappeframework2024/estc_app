# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta

class OTRequest(Document):
	def before_save(self):
		head_department = frappe.db.get_value('Employee', self.employee, ['approve_by_supervisor', 'approve_by_head_department'], as_dict=1)
		supervisor = frappe.db.get_value('Employee', head_department.approve_by_supervisor, ['name', 'employee_name','company_email'], as_dict=1)
		head_department_approver = frappe.db.get_value('Employee', head_department.approve_by_head_department, ['name', 'employee_name','company_email'], as_dict=1)
		self.hr_email = frappe.db.get_single_value("HR Setting","hr_email")
		self.director_email = frappe.db.get_single_value("HR Setting","director_email")
		self.head_department_approver = head_department_approver.name
		self.head_department_approver_name = head_department_approver.employee_name
		self.head_department_approver_email = head_department_approver.company_email
		if supervisor:
			self.supervisor_approver = supervisor.name
			self.supervisor_approver_name = supervisor.employee_name
			self.supervisor_approver_email = supervisor.company_email
		start =  datetime.strptime(self.start_time, "%H:%M:%S")
		to = datetime.strptime(self.to_time, "%H:%M:%S")
		self.total_hours = to - start
		self.status = self.workflow_state
  
	def on_update_after_submit(self):
		default_fiscal_year = frappe.db.get_value("Fiscal Year",{"is_default":1},['name'])
		if not default_fiscal_year:
			fiscal_year=frappe.get_last_doc('Fiscal Year')
			default_fiscal_year=fiscal_year.name
		total_work_hours = self.total_hours
		ot_leave_type = frappe.db.get_single_value('HR Setting','ot_leave_type')
		total_work_per_day = frappe.db.get_single_value('HR Setting','total_work_per_day')
		leave_status_approved_from_hr = frappe.db.get_single_value('HR Setting','leave_status_approved_from_hr')
		if self.status == leave_status_approved_from_hr:
			multiply_gain_from_ot = frappe.db.get_single_value('HR Setting','total_work_per_day')
			holiday = frappe.db.get_all("Holiday Schedule", filters={
						'is_day_off': 1,
						'date': self.request_date
					})
			if not holiday:
				holiday = frappe.db.get_value("Holiday", filters={
						'is_day_off': 1,
						'date': self.request_date
					})
			if not frappe.db.exists("Employee Attendance Leave Count", {"leave_type": ot_leave_type,"employee":self.employee,"fiscal_year":default_fiscal_year}):
				doc = frappe.new_doc('Employee Attendance Leave Count')
				doc.fiscal_year = default_fiscal_year
				doc.employee = self.employee
				doc.max_leave = ((total_work_hours.total_seconds()/total_work_per_day)/3600) * 2 if holiday else (total_work_hours.total_seconds()/total_work_per_day)/3600
				doc.use_leave = 0
				doc.balance = doc.max_leave - doc.use_leave
				doc.leave_type=ot_leave_type or None
				doc.save()
				frappe.db.set_value('OT Request', self.name, 'leave_count', ((total_work_hours.total_seconds()/total_work_per_day)/3600) * 2 if holiday else (total_work_hours.total_seconds()/total_work_per_day)/3600)
			else:
				frappe.db.sql(f"""
                  				UPDATE `tabEmployee Attendance Leave Count` 
                      					set 
                           					max_leave = max_leave + {((total_work_hours.total_seconds()/total_work_per_day)/3600) * 2 if holiday else (total_work_hours.total_seconds()/total_work_per_day)/3600},
                           					balance = balance + {((total_work_hours.total_seconds()/total_work_per_day)/3600) * 2 if holiday else (total_work_hours.total_seconds()/total_work_per_day)/3600}
								where
        							leave_type = '{ot_leave_type}' and
									employee = '{self.employee}' and 
									fiscal_year = '{default_fiscal_year}'
                      			""");
				frappe.db.commit()



@frappe.whitelist()
def get_events(start, end, filters=None):
	from frappe.desk.calendar import get_event_conditions
	department = frappe.db.get_list("Department",pluck='name')
	conditions = get_event_conditions("OT Request", [["OT Request","department","in",department],["OT Request","status","in",["HR Approved","Approved","Request"]]])
	
	sql = """
			select 
   				request_date as start,
				request_date as end,
				name,
				"#8ADAB2" as backgroundColor,
				CONCAT(`name`,"-",`employee_name`, ' '," ",`start_time`," To ",`to_time`) as title,
				status as leave_status
    		from `tabOT Request` 
      		where request_date between "{start}" and "{end}" 
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

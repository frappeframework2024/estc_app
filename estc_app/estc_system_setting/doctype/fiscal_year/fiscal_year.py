# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class FiscalYear(Document):
	def before_save(self):
		
		if self.is_new():
			last_fiscal_year = frappe.get_last_doc('Fiscal Year')
			employee_list= frappe.db.get_list('Employee', fields=['name', 'date_of_joining'])
			if employee_leave_balance:
				employee_leave_balance = frappe.db.get_list("Employee Attendance Leave Count", 
							filters={
									'docstatus': 1,
									'fiscal_year':last_fiscal_year.name
								},
							fields=['sum(balance) as carry_over_balance', 'employee'],
							group_by='employee')
			else:
				employee_leave_balance = frappe.db.get_list("Employee Attendance Leave Count", 
							filters={
									'docstatus': 1
								},
							fields=['sum(balance) as carry_over_balance', 'employee'],
							group_by='employee')
			annual_leave_setting = frappe.db.sql("""select * from `tabAnnual Leave Count Setting`""",as_dict=1)
			for emp in employee_list:
				start_date = emp['date_of_joining'] or datetime.date(datetime.now())
				current_date = datetime.date(datetime.strptime(self.start_date, '%Y-%m-%d'))
				diff = current_date - start_date
				
				self.append("leave_count", {
						"employee":emp['name'],
						"date_of_joining":start_date or 0,
						"duration":diff.days/365,
						"annual_leave":get_annual_leave_count(annual_leave_setting,diff.days/365),
						"sick_leave":0,
						"carry_over": get_carry_over_balance(emp['name'],employee_leave_balance),
						"monthly_accrual":0,
					})

	def on_update(self):
		frappe.enqueue('estc_app.estc_system_setting.doctype.fiscal_year.fiscal_year.generate_holidays',self=self)

def get_carry_over_balance(employee,employee_leave_balance):
	carry_over=[d.carry_over_balance for d in employee_leave_balance if d.employee==employee]
	if len(carry_over)>0:
		return carry_over[0]
	return 0


def get_annual_leave_count(leave_settings,duration):
	annual_leave_count = 0
	for leave in leave_settings:
		if duration >= leave.from_year and duration<=leave.to_year:
			annual_leave_count=leave.total_annual_leave
	return annual_leave_count

@frappe.whitelist()
def get_annual_leave_setting():
	annual_leave_settings = frappe.db.get_all('Annual Leave Count Setting',fields=['*'])
	return annual_leave_settings

@frappe.whitelist()
def update_employee_data(fiscal_year_name):
	fiscal_year = frappe.get_doc("Fiscal Year",fiscal_year_name)
	annual_leave_type = frappe.db.get_single_value("HR Setting","annual_leave_type")
	sick_leave_type = frappe.db.get_single_value("HR Setting","sick_leave_type")
	for emp in fiscal_year.leave_count:
		emp_leave_count = frappe.db.get_list(
						"Employee Attendance Leave Count",
						filters={
									'employee':emp.employee,
									'fiscal_year':fiscal_year.name
                          		},
               			fields=['name','empoyee','leave_type','fiscal_year','max_leave'])
		#annual leave

		leave_data=[d for d in emp_leave_count if d.fiscal_year==fiscal_year_name and d.leave_type == annual_leave_type]

		if len(leave_data) > 0:
			leave_data[0].max_leave = (emp.annual_leave or 0) + (emp.carry_over or 0)
			
			frappe.db.set_value('Employee Attendance Leave Count',leave_data[0].name,'max_leave',leave_data[0].max_leave)
		else:
			doc = frappe.new_doc("Employee Attendance Leave Count")
			doc.employee = emp.employee
			doc.leave_type=annual_leave_type
			doc.fiscal_year=fiscal_year_name
			doc.max_leave = (emp.annual_leave or 0) + (emp.carry_over or 0)
			doc.insert()

		#sick leave
		leave_data=[d for d in emp_leave_count if d.fiscal_year==fiscal_year_name and d.leave_type==sick_leave_type]
		if len(leave_data) > 0:
			leave_data[0].max_leave = (emp.sick_leave or 0)
			frappe.db.set_value('Employee Attendance Leave Count',leave_data[0].name,'max_leave',leave_data[0].max_leave)
		else:
			doc = frappe.new_doc("Employee Attendance Leave Count")
			doc.employee = emp.employee
			doc.leave_type=sick_leave_type
			doc.fiscal_year=fiscal_year_name
			doc.max_leave = (emp.sick_leave)
			doc.insert()
		frappe.db.commit()

def generate_holidays(self):
	frappe.db.sql(f"delete from `tabHoliday` where parent = '{self.name}'")
	for temp in self.temp_holiday:
			start_date = datetime.strptime(temp.start_date, '%Y-%m-%d')
			end_date = datetime.strptime(temp.end_date, '%Y-%m-%d')
			current_date = start_date
			while current_date <= end_date:
				holiday = frappe.new_doc('Holiday')
				holiday.parenttype='Fiscal Year'
				holiday.parentfield ='holidays'
				holiday.description=temp.description
				holiday.parent = self.name
				holiday.is_day_off = temp.is_day_off
				holiday.date = current_date.strftime('%Y-%m-%d')
				holiday.save()
				current_date += timedelta(days=1)
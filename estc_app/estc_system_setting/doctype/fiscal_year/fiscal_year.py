# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class FiscalYear(Document):
	def before_save(self):
		if self.is_new():
			last_fiscal_year = frappe.get_last_doc('Fiscal Year')
			employee_list= frappe.db.get_list('Employee', fields=['name', 'date_of_joining'])
			employee_leave_balance = frappe.db.get_list("Employee Attendance Leave Count", 
                    	filters={
								'docstatus': 1,
								'fiscal_year':last_fiscal_year.name
							},
                    	fields=['sum(balance) as carry_over_balance', 'employee'],
                    	group_by='employee')
			for emp in employee_list:
				start_date = emp['date_of_joining'] or datetime.date(datetime.now())
				current_date = datetime.date(datetime.now())
				diff = current_date - start_date
				
				self.append("leave_count", {
						"employee":emp['name'],
						"date_of_joining":start_date or 0,
						"duration":diff.days/365,
						"annual_leave":0,
						"sick_leave":0,
						"carry_over": get_carry_over_balance(emp['name'],employee_leave_balance),
						"monthly_accrual":0,
					})

def get_carry_over_balance(employee,employee_leave_balance):
	carry_over=[d.carry_over_balance for d in employee_leave_balance if d.employee==employee]
	if len(carry_over)>0:
		return carry_over[0]
	return 0

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
		doc = frappe.get_doc("Employee",emp.employee)
		
		#annual leave
		leave_data=[d for d in doc.leave_setting if d.fiscal_year==fiscal_year_name]
		if leave_data:
			leave_data[0].max_leave = (emp.annual_leave or 0) + (emp.carry_over or 0)
		else:
			doc.append("leave_setting", {
				"leave_type":annual_leave_type,
				"fiscal_year":fiscal_year_name,
				"max_leave":(emp.annual_leave or 0) + (emp.carry_over or 0)
			})

		#sick leave
		leave_data=[d for d in doc.leave_setting if d.fiscal_year==fiscal_year_name and d.leave_type==sick_leave_type]
		if leave_data:
			leave_data[0].max_leave = (emp.sick_leave or 0)
		else:
			doc.append("leave_setting", {
				"leave_type":sick_leave_type,
				"fiscal_year":fiscal_year_name,
				"max_leave":(emp.sick_leave or 0)
			})
		doc.save()

		
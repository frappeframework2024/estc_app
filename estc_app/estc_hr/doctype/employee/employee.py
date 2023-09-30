# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import today


class Employee(Document):
	def validate(self):
		for d in self.leave_setting:
			d.balance = (d.max_leave or 0) - (d.use_leave or 0)

	def on_update(self):
		 
		frappe.enqueue("estc_app.estc_hr.doctype.employee.employee.update_user_information", queue='short', self =self)
		frappe.enqueue("estc_app.estc_hr.doctype.employee.employee.update_leave_balance", queue='short', self =self)

@frappe.whitelist()
def update_user_information(self):
	if self.allow_login:
		if frappe.db.exists("User",self.company_email):
			doc = frappe.get_doc("User", self.company_email)
			doc.enabled = 1
			doc.username = self.username
			doc.first_name = self.employee_name
			doc.role_profile_name = self.role_profile
			doc.module_profile = self.module_profile
			doc.user_image = self.photo
			if self.password:
				doc.new_password = self.password

			
			doc.save()
			

		else:
			doc = frappe.get_doc({
					"doctype":"User",
					"enabled": 1,
					"email": self.company_email,
					"first_name": self.employee_name,
					"username": self.username,
					"language": "en",
					"time_zone": "Asia/Phnom_Penh",
					"send_welcome_email": 0,
					"role_profile_name": self.role_profile,
					"module_profile": self.module_profile,
					"user_type": "System User",
					"new_password":self.password,
					"user_image" : self.photo
					
				}
			).insert()
			doc = frappe.get_doc({
				'doctype':"User Permission",
				'user':self.company_email,
				'allow':self.doctype,
				'for_value':self.name,
				'apply_to_all_doctypes':1,
		}).insert()
			
	else:
		if frappe.db.exists("User",self.company_email):
			doc = frappe.get_doc("User", self.company_email)
			doc.enabled = 0
			doc.save()

	frappe.db.sql("update `tabEmployee` set password='' where name='{}'".format(self.name))


			
@frappe.whitelist()
def update_leave_balance(self):
	for d in self.leave_setting:
		sql = "select sum(attendance_value) total_leave from `tabAttendance` where employee='{}' and leave_type='{}' and fiscal_year='{}'".format(self.name,d.leave_type,d.fiscal_year)

		
		total_leave = frappe.db.sql(sql,as_dict=1)[0]["total_leave"] or 0
 

		frappe.db.sql("update `tabEmployee Attendance Leave Count` set use_leave={0}, balance=max_leave-{0} where name='{1}'".format(total_leave,d.name))
		 
	frappe.db.commit()
	

@frappe.whitelist()
def get_currency_employee(include_last_leave=None):
	data = frappe.db.sql("select name from `tabEmployee` where company_email='{}'".format(frappe.session.user),as_dict=1)
	if data:
		doc =frappe.get_doc("Employee",data[0]["name"])
		response_data={"employee":doc}
		if include_last_leave:
			last_leave = frappe.db.sql("select name, leave_type, start_date, to_date from `tabLeave Request` where status='Approved' and employee='{}' order by start_date desc limit 1".format(doc.name),as_dict=1 )
			if last_leave:
				response_data["last_leave"] = last_leave[0]

		return response_data
	else:
		user = frappe.get_doc("User",frappe.session.user)
		return {
				"employee":{
					"employee_name": user.full_name,
					"employee_code":"",
					"photo":user.user_image
				}
			}
	



@frappe.whitelist()
def get_current_employee_leave_balance(name=None):
	fiscal_year_data = frappe.db.sql("select name from `tabFiscal Year` where is_default=1",as_dict=1)

	fiscal_year = ""
	if fiscal_year_data:
		fiscal_year = fiscal_year_data[0]["name"]
	else:
		fiscal_year_data = frappe.db.sql("select name from `tabFiscal Year`",as_dict=1)
		if fiscal_year_data:
			fiscal_year = fiscal_year_data[0]["name"]
	
	if fiscal_year:
		doc = None
		if name:
			doc = frappe.get_doc("Employee", name)
		else:
			
			data = frappe.db.sql("select name from `tabEmployee` where company_email='{}'".format(frappe.session.user),as_dict=1)
			if data:
				doc = frappe.get_doc("Employee", data[0]["name"])
	
		if doc:
			attendance_count =[d  for d in  doc.leave_setting if d.fiscal_year==fiscal_year]
			return {
				"max_leave":sum([d.max_leave  for d in attendance_count]),
				"use_leave":sum([d.use_leave  for d in attendance_count]),
				"balance":sum([d.balance  for d in attendance_count]),
				"leave_data":attendance_count
			}
	
	return {
		"max_leave":  0,
		"use_leave":0,
		"balance":0,
		"leave_data":0
	}



@frappe.whitelist()
def get_recent_leave_request():
	employee = get_currency_employee()
	data = frappe.db.sql("select name,start_date,to_date, leave_type, color,posting_date,status from `tabLeave Request` where employee='{}' and docstatus=1 order by start_date desc limit 5".format(employee["employee"].name),as_dict=1)
	return data


@frappe.whitelist()
def get_employee_on_leave_today():
	sql="""select 
			name,
			photo,
			employee,
			employee_name,
			start_date, 
			to_date,
			leave_type,
			color
		from 
		`tabLeave Request` a 
		where
		
			a.name in (select leave_request from `tabAttendance` where  attendance_date='{0}') 

		""".format(
			today()
		)
	data = frappe.db.sql(sql,as_dict=1)
	return data


@frappe.whitelist()
def get_upcomming_employee_on_leave():
	sql="""select 
			name,
			photo,
			employee,
			employee_name,
			start_date, 
			to_date,
			leave_type,
			color
		from 
		`tabLeave Request` a 
		where
			a.name in (select leave_request from `tabAttendance` where  attendance_date>'{0}') 
		""".format(
			today()
		)
	data = frappe.db.sql(sql,as_dict=1)
	return data



	 


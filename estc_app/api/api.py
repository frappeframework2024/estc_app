import frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def query_doctypes(doctype, txt, searchfield, start, page_len, filters):
	user = filters.get("user")
	user_perms = frappe.utils.user.UserPermissions(user)
	user_perms.build_permissions()
	can_read = user_perms.can_read  # Does not include child tables
	include_single_doctypes = filters.get("include_single_doctypes")

	single_doctypes = [d[0] for d in frappe.db.get_values("DocType", {"issingle": 1})]
	return [
		[dt]
		for dt in can_read
		if txt.lower().replace("%", "") in dt.lower()
		and (include_single_doctypes or dt not in single_doctypes)
	]

@frappe.whitelist()
def fix_ot_leave_count():

	data = frappe.db.sql("select employee, sum(leave_count) as total from   `tabOT Request`  where status = 'HR Approved' and fiscal_year='2023-2024' group by employee",as_dict=1)
	for d in data:
		sql = "update `tabEmployee Attendance Leave Count` set max_leave={} where employee='{}' and leave_type='Over Time' and fiscal_year='2023-2024'".format(d.get("total",0),d.get("employee"))
		frappe.db.sql(sql)
	frappe.db.commit()

	# update use leave
	data = frappe.db.sql("select employee,sum(total_leave_days) as total  from   `tabLeave Request`  where   fiscal_year='2023-2024' and leave_type = 'Over Time'  and status = 'Approved' group by employee",as_dict=1)
	for d in data:
		sql = "update `tabEmployee Attendance Leave Count` set use_leave={} where employee='{}' and leave_type='Over Time' and fiscal_year='2023-2024'".format(d.get("total",0),d.get("employee"))
		frappe.db.sql(sql)
	frappe.db.commit()

	frappe.db.sql("update `tabEmployee Attendance Leave Count` set balance=max_leave-use_leave")
	frappe.db.commit()



@frappe.whitelist()
def fix_ot_carry_over_to_2024_2025():
	# update from old year
	sql = "select    employee, balance from `tabEmployee Attendance Leave Count` where fiscal_year='2023-2024' and leave_type = 'Over Time'"
	data = frappe.db.sql(sql,as_dict = 1)

	for d in data:
		sql = "update `tabEmployee Attendance Leave Count` set max_leave = {} where employee='{}' and leave_type = 'Over Time' and fiscal_year='2024-2025'".format(d.get("balance",0),d.get("employee"))
		frappe.db.sql(sql)
	frappe.db.commit()
	  



	# uupdate from ot current yeart	#
	sql = "select employee,sum(leave_count) as total from `tabOT Request` where fiscal_year='2024-2025' and status= 'HR Approved' group by employee"
	data = frappe.db.sql(sql,as_dict=1)
	for d in data:
		sql = "update `tabEmployee Attendance Leave Count` set max_leave = max_leave +  {} where employee='{}' and leave_type = 'Over Time' and fiscal_year='2024-2025'".format(d.get("total",0),d.get("employee"))
		frappe.db.sql(sql)

	frappe.db.commit()

	# update use leave 
	sql = "select employee, sum(total_leave_days) as total from `tabLeave Request` where fiscal_year='2024-2025' and leave_type = 'Over Time' and status = 'Approved' group by employee"
	data = frappe.db.sql(sql,as_dict=1)
	for d in data:
		sql = "update `tabEmployee Attendance Leave Count` set use_leave =   {} where employee='{}' and leave_type = 'Over Time' and fiscal_year='2024-2025'".format(d.get("total",0),d.get("employee"))
		frappe.db.sql(sql)

	frappe.db.commit()

	frappe.db.sql("update `tabEmployee Attendance Leave Count` set balance=max_leave-use_leave")
	frappe.db.commit()



@frappe.whitelist()
def update_use_leave_al_2023_2024():
	sql = "update `tabEmployee Attendance Leave Count` set use_leave = 0 where fiscal_year='2023-2024' and leave_type='Annual Leave'" 
	frappe.db.sql(sql)
	frappe.db.commit()
	
	sql = "select employee, sum(total_leave_days) as total  from `tabLeave Request` where fiscal_year= '2023-2024' and status = 'Approved' and leave_type='Annual Leave'   group by employee "
	data = frappe.db.sql(sql,as_dict=1)
	for d in data:
		sql = "update `tabEmployee Attendance Leave Count` set use_leave = {} where fiscal_year='2023-2024' and leave_type='Annual Leave' and employee = '{}'".format(d.get("total",0), d.get("employee"))
		frappe.db.sql(sql)

	frappe.db.commit()

	frappe.db.sql("update `tabEmployee Attendance Leave Count` set balance=max_leave-use_leave")
	frappe.db.commit()
	
@frappe.whitelist()
def update_use_leave_al_carry_over_2024_2025():
	# update to fiscal year update carie over AL in fis year 2024-2025 get balance from 2023-24

	sql = "select    employee, balance, leave_type from `tabEmployee Attendance Leave Count` where fiscal_year='2023-2024' and leave_type = 'Annual Leave'"
	data = frappe.db.sql(sql,as_dict=1)
	for d in data:
		sql = "update `tabEmployee Annual Leave` set carry_over = {} where parent='2024-2025' and employee='{}'".format(
			d.get("balance",0),
			d.get("employee")
		)
		frappe.db.sql(sql)

	frappe.db.commit()

@frappe.whitelist()
def update_use_leave_ot_carry_over_fiscal_year_2024_2025():
	# update to fiscal year update carie over AL in fis year 2024-2025 get balance from 2023-24

	sql = "select    employee, balance, leave_type from `tabEmployee Attendance Leave Count` where fiscal_year='2023-2024' and leave_type = 'Over Time'"
	data = frappe.db.sql(sql,as_dict=1)
	for d in data:
		sql = "update `tabEmployee Annual Leave` set ot_carry_over = {} where parent='2024-2025' and employee='{}'".format(
			d.get("balance",0),
			d.get("employee")
		)
		frappe.db.sql(sql)

	frappe.db.commit()

@frappe.whitelist()
def update_use_leave_al_2024_2025():
	# update to fiscal year update carie over AL in fis year 2024-2025 get balance from 2023-24

	sql = "select employee,annual_leave + carry_over as total from `tabEmployee Annual Leave` where parent = '2024-2025'"
	data = frappe.db.sql(sql,as_dict=1)
	for d in data:
		sql = "update `tabEmployee Attendance Leave Count` set max_leave = {} where fiscal_year='2024-2025' and leave_type = 'Annual Leave' and employee='{}'".format(
			d.get("total",0),
			d.get("employee")

		)
		frappe.db.sql(sql)
	frappe.db.commit()
	
 
	frappe.db.sql("update `tabEmployee Attendance Leave Count` set balance=max_leave-use_leave")
	frappe.db.commit()


	# 1 get caria over from 2024-2024
	
@frappe.whitelist()
def create_custom_print_setting():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(
                    {
                        "Print Settings": [
                            {
                                "label": "Academic year",
                                "fieldname": "fiscal_year",
                                "fieldtype": "Link",
                                "options":"Fiscal Year",
                                "default": "",
                                "insert_after": "with_letterhead"
                            },
                            {
                                "label": "Show Detail",
                                "fieldname": "show_detail",
                                "fieldtype": "Check",
                                "default":1,
                                "insert_after": "fiscal_year"
                            }
                        ]
                    }
                )
    frappe.db.commit()
    
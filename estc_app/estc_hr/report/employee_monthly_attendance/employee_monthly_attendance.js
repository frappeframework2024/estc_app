frappe.query_reports["Employee Monthly Attendance"] = {
	
	"filters": [
		{
			fieldname: "fiscal_year",
			label: "Academic Year",
			fieldtype: "Link",
			options: "Fiscal Year",
			mandatory:1
		},
		{
			fieldname: "department",
			label: "Department",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Department', txt, {"is_group": ['=', 0]});
			},
		},
		{
			fieldname: "leave_type",
			label: "Leave Type",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Leave Type', txt);
			},
		}
	]
};
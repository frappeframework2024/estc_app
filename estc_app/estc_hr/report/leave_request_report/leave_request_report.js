frappe.query_reports["Leave Request Report"] = {
	
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
			fieldname: "employee",
			label: "Employee",
			fieldtype: "Link",
			options: "Employee"
		}
		
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		return value;
	},
};
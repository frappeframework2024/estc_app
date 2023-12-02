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
			fieldname: "employee",
			label: "Employee",
			fieldtype: "Link",
			options: "Employee",
			mandatory:1
		},
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		
		
		return value;
	},
};
frappe.query_reports["Daily Employee Attendance"] = {
	
	"filters": [
		{
			fieldname: "start_date",
			label: __("Start Date"),
			fieldtype: "Date",
			mandatory:1
		},
		{
			fieldname: "end_date",
			label: __("End Date"),
			fieldtype: "Date",
			mandatory:1
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "All\nPresent\nAbsent",
			default:"All"
		},
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		return value;
	},
};
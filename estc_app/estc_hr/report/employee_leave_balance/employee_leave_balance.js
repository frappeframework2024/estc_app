// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Leave Balance"] = {
	"filters": [
		{
			fieldname: "fiscal_year",
			label: "Academic Year",
			fieldtype: "Link",
			options: "Fiscal Year"
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
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data)
		return value;
	},
};

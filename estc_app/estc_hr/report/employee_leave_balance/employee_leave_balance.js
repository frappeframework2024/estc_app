// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Leave Balance"] = {
	"filters": [
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

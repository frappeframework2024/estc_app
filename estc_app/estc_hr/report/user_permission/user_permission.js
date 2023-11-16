// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["User Permission"] = {
	filters: [
		{
			fieldname: "user",
			label: __("User"),
			fieldtype: "Link",
			options: "User",
			reqd: 1,
		},
		{
			fieldname: "doctype",
			label: __("DocType"),
			fieldtype: "Link",
			options: "DocType",
			reqd: 1,
			get_query: function () {
				return {
					query: "estc_app.api.api.query_doctypes",
					filters: {
						user: frappe.query_report.get_filter_value("user")
					},
				};
			},
		},
		{
			fieldname: "show_permissions",
			label: __("Show Permissions"),
			fieldtype: "Check",
		},
	],
};

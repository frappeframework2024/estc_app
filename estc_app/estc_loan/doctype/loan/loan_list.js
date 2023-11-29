// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Loan'] = {
	get_indicator: function(doc) {
		const status_colors = {
			"Draft": "yellow",
			"Submitted": "blue",
			"Write Off": "red",
		};
		return [__(doc.status), status_colors[doc.status], "status,=,"+doc.status];
	},
};

// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Report"] = {
	"filters": [
		{
			"fieldname": "gender",
			"label": __("Gender"),
			"fieldtype": "Select",
			"options":"\nMale\nFemale",
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options":"\nActive\nInactive\nSuspended\nLeft",
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options":"Department",
		},
		{
			"fieldname": "marital_status",
			"label": __("Marital Status"),
			"fieldtype": "Select",
			"options":"\nSingle\nMarried\nDivorced\nWindowed",
		},
		{
			"fieldname": "position",
			"label": __("Position"),
			"fieldtype": "Link",
			"options":"Position",
		},
		{
			"fieldname": "group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options":"\nTitle\nMarital Status\nDepartment\nHead Department\nPosition\nStatus\nGender\nEmployee Type\nNationality\nBlood Group",
		},
		{
			"fieldname": "order_by",
			"label": __("Order By"),
			"fieldtype": "Select",
			"options": "Last Update On\nCreated On\nID\nEmployee Name\nEmployee Code\nGender\nStatus\nDepartment\nPosition",
			default:"Last Update On"
		},
		{
			"fieldname": "sort_order",
			"label": __("Sort Order"),
			"fieldtype": "Select",
			"options": "ASC\nDESC",
			default:"ASC"
		},
	],

};

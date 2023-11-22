# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LeaveType(Document):
	pass

@frappe.whitelist()
def get_leave_type_for_custom_html():
	leave_types = frappe.db.get_list("Leave Type")
	return leave_types
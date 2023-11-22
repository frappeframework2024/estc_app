# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Department(Document):
	pass



@frappe.whitelist()
def get_department():
	departments = frappe.get_list("Department",filters={
        'is_group': 0
    })
	return departments
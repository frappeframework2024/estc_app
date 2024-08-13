# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PaymentType(Document):
	def on_update(self):
		x = frappe.get_cached_value("Payment Type","ABA Dollar","default_account")	
		frappe.throw(frappe.as_json(x))

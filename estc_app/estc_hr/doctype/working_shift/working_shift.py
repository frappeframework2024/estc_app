# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WorkingShift(Document):
	def on_update(self):
		frappe.clear_document_cache("Working Shift", self.name)

	def on_update_after_submit(self): 
		frappe.clear_document_cache("Working Shift", self.name)
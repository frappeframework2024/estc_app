# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LoanSecurityPledge(Document):
	def on_submit(self):
		loan = frappe.get_doc('Loan', self.loan)
		loan.security_pledge = 1
		loan.save()

	def on_cancel(self):
		loan = frappe.get_doc('Loan', self.loan)
		loan.security_pledge = 0
		loan.save()
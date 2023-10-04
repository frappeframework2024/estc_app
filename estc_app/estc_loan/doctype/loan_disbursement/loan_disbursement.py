# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LoanDisbursement(Document):
	def on_submit(self):
		frappe.db.sql("""update `tabLoan` set disbursed_amount = disbursed_amount + {0} where name = '{1}'""".format(self.disbursed_amount,self.loan))

	def on_cancel(self):
		frappe.db.sql("""update `tabLoan` set disbursed_amount = disbursed_amount - {0} where name = '{1}'""".format(self.disbursed_amount,self.loan))

# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from estc_app.estc_loan.utils import add_gl_entry
import frappe
class LoanWriteOff(Document):
	def after_insert(self):
		add_gl_entry(self.posting_date,self.loan_account,0,self.balance,"Loan",self.loan,"Loan Write Off",self.name,"Write Off Against Loan: {0}".format(self.loan))
		add_gl_entry(self.posting_date,self.write_off_account,self.balance,0,"Loan",self.loan,"Loan Write Off",self.name,"Write Off Against Loan: {0}".format(self.loan))

	def on_cancel(self):
		add_gl_entry(self.posting_date,self.loan_account,self.balance,0,"Loan",self.loan,"Loan Write Off",self.name,"Cancellation Of: {0}".format(self.name))
		add_gl_entry(self.posting_date,self.payment_account,0,self.balance,"Loan",self.loan,"Loan Write Off",self.name,"Cancellation Of: {0}".format(self.name))
		frappe.db.sql("update `tabGeneral Ledger Entry` set is_cancelled = 1 where voucher_no = '{}'".format(self.name))

	def on_submit(self):
		frappe.db.sql("update `tabLoan` set status = 'Write Off' where name = '{}'".format(self.loan))

	def validate(self):
		doc = frappe.db.sql("select * from `tabLoan Write Off` where loan = '{}' and docstatus=1".format(self.loan),as_dict=1)
		if len(doc) > 0:
			frappe.throw("Loan has already been mark as write off")
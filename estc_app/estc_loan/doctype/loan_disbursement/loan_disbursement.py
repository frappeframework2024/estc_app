# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from estc_app.estc_loan.utils import add_gl_entry
import json
class LoanDisbursement(Document):
	def validate(self):
		loan = frappe.get_doc('Loan',self.loan)
		if loan.disbursed_amount == loan.loan_amount:
			frappe.throw("This loan already been disbursed")
		if loan.security_pledge == 0 and loan.is_secured_loan == 1:
			frappe.throw("This is a secured loan. Please add security pledge first")

	def on_submit(self):
			frappe.db.sql("""update `tabLoan` set disbursed_amount = disbursed_amount + {0} where name = '{1}'""".format(self.disbursed_amount,self.loan))

	def after_insert(self):
			add_gl_entry(self.posting_date,self.loan_account,self.disbursed_amount,0,"Loan",self.loan,"Loan Disbursement",self.name,"Disbursement Against Loan: {0}".format(self.loan))
			add_gl_entry(self.posting_date,self.disbursed_account,0,self.disbursed_amount,"Loan",self.loan,"Loan Disbursement",self.name,"Disbursement Against Loan: {0}".format(self.loan))

	def on_cancel(self):
		frappe.db.sql("""update `tabLoan` set disbursed_amount = disbursed_amount - {0} where name = '{1}'""".format(self.disbursed_amount,self.loan))
		add_gl_entry(self.posting_date,self.loan_account,0,self.disbursed_amount,"Loan",self.loan,"Loan Disbursement",self.name,"Cancelled Disbursement Against Loan: {0}".format(self.loan))
		add_gl_entry(self.posting_date,self.disbursed_account,self.disbursed_amount,0,"Loan",self.loan,"Loan Disbursement",self.name,"Cancelled Disbursement Against Loan: {0}".format(self.loan))
		frappe.db.sql("update `tabGeneral Ledger Entry` set is_cancelled = 1 where voucher_no = '{}'".format(self.name))

@frappe.whitelist()
def get_loan_maount(loan):
	loan_ = frappe.get_doc('Loan',loan)
	return loan_.loan_amount
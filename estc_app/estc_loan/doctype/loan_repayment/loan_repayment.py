# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from estc_app.estc_loan.utils import add_gl_entry

class LoanRepayment(Document):
	def validate(self):
		loan_disbursement = frappe.db.get_list('Loan Disbursement',filters={'Loan': self.loan},fields=['name'],as_list=True)
		if len(loan_disbursement) == 0:
			frappe.throw("This is loan has no disbursement. Please add disbursement first")

	def on_submit(self):
		currency_precision = int(frappe.db.get_single_value('System Settings', 'currency_precision'))
		sql = """SELECT 
			name,
			balance
			FROM `tabLoan Repayment Schedule` 
			WHERE parent = '{0}' and balance > 0
			ORDER BY payment_date""".format(self.loan)
		repayment_schedule = frappe.db.sql(sql,as_dict=1)
		payment_amount = self.payment_amount - self.penalty_amount + self.write_off_amount
		i = 0
		while payment_amount > 0:
			a = repayment_schedule[i]
			if payment_amount < a.balance:
				frappe.db.set_value('Loan Repayment Schedule', a.name, {'balance':a.balance - payment_amount})
				payment_amount = 0
			else:
				frappe.db.set_value('Loan Repayment Schedule', a.name, {'balance':0})
			payment_amount = round(payment_amount - a.balance,currency_precision)
			i += 1
		
		loan = frappe.get_doc('Loan', self.loan)
		loan.total_paid_amount = loan.total_paid_amount + (self.payment_amount - self.penalty_amount + self.write_off_amount)
		loan.total_write_off = loan.total_write_off + self.write_off_amount
		loan.total_penalty_amount = loan.total_penalty_amount + self.penalty_amount
		loan.save()

	def after_insert(self):
			add_gl_entry(self.posting_date,self.loan_account,0,self.payment_amount,"Loan",self.loan,"Loan Repayment",self.name,"Repayment Against Loan: {0}".format(self.loan))
			add_gl_entry(self.posting_date,self.payment_account,self.payment_amount,0,"Loan",self.loan,"Loan Repayment",self.name,"Repayment Against Loan: {0}".format(self.loan))

	def on_cancel(self):
		currency_precision = int(frappe.db.get_single_value('System Settings', 'currency_precision'))
		sql = """SELECT 
			name,
			balance,
			total_payment
			FROM `tabLoan Repayment Schedule` 
			WHERE parent = '{0}' and balance != total_payment
			ORDER BY payment_date""".format(self.loan)
		repayment_schedule = frappe.db.sql(sql,as_dict=1)
		payment_amount = self.payment_amount - self.penalty_amount + self.write_off_amount
		i = 0
		while payment_amount > 0:
			a = repayment_schedule[i]
			if payment_amount >= a.total_payment:
				frappe.db.set_value('Loan Repayment Schedule', a.name, {'balance':a.total_payment})
			else:
				frappe.db.set_value('Loan Repayment Schedule', a.name, {'balance':a.balance + payment_amount})
			payment_amount = round(payment_amount - a.total_payment,currency_precision)
			i += 1
		
		loan = frappe.get_doc('Loan', self.loan)
		loan.total_paid_amount = loan.total_paid_amount - self.total_amount
		loan.total_write_off = loan.total_write_off - self.write_off_amount
		loan.total_penalty_amount = loan.total_penalty_amount - self.penalty_amount
		loan.save()

		add_gl_entry(self.posting_date,self.loan_account,self.payment_amount,0,"Loan",self.loan,"Loan Repayment",self.name,"Cancelled Repayment Against Loan: {0}".format(self.loan))
		add_gl_entry(self.posting_date,self.payment_account,0,self.payment_amount,"Loan",self.loan,"Loan Repayment",self.name,"Cancelled Repayment Against Loan: {0}".format(self.loan))
		frappe.db.sql("update `tabGeneral Ledger Entry` set is_cancelled = 1 where voucher_no = '{}'".format(self.name))

@frappe.whitelist()
def get_loan_amount_to_day(loan,posting_date):
	sql = """SELECT 
	coalesce(SUM(balance),0) total_payment,
	MIN(payment_date) min_payment_date,
	MAX(payment_date) max_payment_date
	FROM `tabLoan Repayment Schedule` 
	WHERE parent = '{0}' AND payment_date <= '{1}' and balance > 0
	ORDER BY payment_date""".format(loan,posting_date)
	total_amounts = frappe.db.sql(sql,as_dict=1)
	if total_amounts[0].total_payment == 0:
		sql = """SELECT 
		balance total_payment,
		payment_date max_payment_date
		FROM `tabLoan Repayment Schedule` 
		WHERE parent = '{0}' and balance > 0
		ORDER BY payment_date limit 1""".format(loan,posting_date)
		total_amounts = frappe.db.sql(sql,as_dict=1)
		if len(total_amounts) == 0:
			return 0
	return total_amounts[0]
# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LoanRepayment(Document):
	def on_submit(self):
		currency_precision = int(frappe.db.get_single_value('System Settings', 'currency_precision'))
		sql = """SELECT 
			name,
			balance
			FROM `tabLoan Repayment Schedule` 
			WHERE parent = '{0}' and balance > 0
			ORDER BY payment_date""".format(self.loan)
		repayment_schedule = frappe.db.sql(sql,as_dict=1)
		balance = self.payment_amount
		i = 0
		while balance > 0:
			a = repayment_schedule[i]
			if balance < a.balance:
				frappe.db.set_value('Loan Repayment Schedule', a.name, {'balance':a.balance - balance})
				balance = 0
			else:
				frappe.db.set_value('Loan Repayment Schedule', a.name, {'balance':0})
			balance = round(balance - a.balance,currency_precision)
			i += 1
		
		loan = frappe.get_doc('Loan', self.loan)
		loan.total_paid_amount = loan.total_paid_amount + (self.payment_amount - self.penalty_amount + self.write_off_amount)
		loan.total_write_off = loan.total_write_off + self.write_off_amount
		loan.total_penalty_amount = loan.total_penalty_amount + self.penalty_amount
		loan.save()


	def on_cancel(self):
		pass

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
	return total_amounts[0]
# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LoanRepayment(Document):
	pass

@frappe.whitelist()
def get_loan_amount_to_day(loan,posting_date):
	sql = """SELECT 
	coalesce(SUM(total_payment),0) total_amount
	FROM `tabLoan Repayment Schedule` 
	WHERE parent = '{0}' AND payment_date <= '{1}' 
	ORDER BY payment_date""".format(loan,posting_date)
	total_amounts = frappe.db.sql(sql,as_dict=1)
	return total_amounts[0]
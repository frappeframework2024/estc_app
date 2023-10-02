# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import math
import frappe
from frappe.model.document import Document
from frappe.utils.data import flt
from frappe.utils import add_months, flt, get_last_day, getdate, now_datetime, nowdate

class Loan(Document):

	def validate(self):
		self.make_repayment_schedule()
		self.repayment_period = len(self.repayment_schedule)
		self.update_summary()
	

	
	def update_summary(self):
		total_amount = 0
		total_interest = 0
		for a in self.repayment_schedule:
			total_amount += a.total_payment
			total_interest += a.interest_amount
		self.total_amount = total_amount
		self.total_interest = total_interest

	def make_repayment_schedule(self):
		if not self.repayment_start_date:
			frappe.throw(("Repayment Start Date is mandatory for term loans"))

		currency_precision = int(frappe.db.get_single_value('System Settings', 'currency_precision'))
		self.repayment_schedule = []
		payment_date = self.repayment_start_date
		
		if self.repayment_method == "Repay Over Number of Periods":
			Days = 30
			count = 1
			interest_rate = 0 if self.interest_rate is None else self.interest_rate / 100
			balance_amount = self.loan_amount
			total_amount = balance_amount/self.repayment_period if interest_rate == 0 else round((balance_amount * interest_rate) / (1-(1/((1+interest_rate)**self.repayment_period))),currency_precision)
			while count <= self.repayment_period:
				interest_amount = 0 if interest_rate == 0 else round(balance_amount * interest_rate / Days * Days,currency_precision)
				principal_amount =  round(total_amount - interest_amount,currency_precision)
				balance_amount =  round(balance_amount - principal_amount,currency_precision)
				total_payment =  round(principal_amount + interest_amount,currency_precision)
				self.append(
					"repayment_schedule",
					{
						"payment_date": payment_date,
						"principal_amount": principal_amount,
						"interest_amount": interest_amount,
						"total_payment": total_payment,
						"balance_loan_amount": balance_amount,
					},
				)
				next_payment_date = add_single_month(payment_date)
				payment_date = next_payment_date
				count = count + 1
				
		elif(self.repayment_method == 'Repay Over Number of Periods(Fixed Principal)'):
			count = 1
			interest_amount =  round(self.loan_amount * (self.interest_rate / 100),currency_precision)
			principal_amount =  round(self.loan_amount/self.repayment_period,currency_precision)
			balance_amount =  round(self.loan_amount - principal_amount,currency_precision)
			while count<= self.repayment_period:
				total_payment =  round(principal_amount + interest_amount,currency_precision)
				self.append(
					"repayment_schedule",
					{
						"payment_date": payment_date,
						"principal_amount": principal_amount,
						"interest_amount": interest_amount,
						"total_payment": total_payment,
						"balance_loan_amount": balance_amount,
					},
				)
				interest_amount = round(balance_amount * (self.interest_rate / 100),currency_precision)
				balance_amount = round(balance_amount - principal_amount,currency_precision)
				next_payment_date = add_single_month(payment_date)
				payment_date = next_payment_date
				count = count + 1
		else:
			repayment_period = math.ceil(self.loan_amount / self.monthly_repayment)
			balance_amount = self.loan_amount - self.monthly_repayment
			last_row_balance = 0
			count = 1
			while count <= repayment_period:
				total_payment =  round(self.monthly_repayment,currency_precision)
				principal_amount = total_payment
				
				if count == repayment_period:
					principal_amount = last_row_balance
					total_payment = principal_amount
					balance_amount = 0
				self.append(
					"repayment_schedule",
					{
						"payment_date": payment_date,
						"principal_amount": principal_amount,
						"interest_amount": 0,
						"total_payment": total_payment,
						"balance_loan_amount": balance_amount,
					},
				)
				last_row_balance = balance_amount
				balance_amount = round(balance_amount - principal_amount,currency_precision)
				next_payment_date = add_single_month(payment_date)
				payment_date = next_payment_date
				count = count+1
			
def add_single_month(date):
	if getdate(date) == get_last_day(date):
		return get_last_day(add_months(date, 1))
	else:
		return add_months(date, 1)

@frappe.whitelist()
def make_loan_disbursement(loan, applicant_type, applicant, pending_amount=0, as_dict=0):
	disbursement_entry = frappe.new_doc("Loan Disbursement")
	disbursement_entry.loan = loan
	disbursement_entry.applicant_type = applicant_type
	disbursement_entry.applicant = applicant
	disbursement_entry.posting_date = nowdate()
	disbursement_entry.disbursed_amount = pending_amount
	if as_dict:
		return disbursement_entry.as_dict()
	else:
		return disbursement_entry
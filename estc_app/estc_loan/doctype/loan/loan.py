# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import math
import frappe
from frappe.model.document import Document
from frappe.utils.data import flt
from frappe.utils import add_months, flt, get_last_day, getdate, now_datetime, nowdate
from datetime import datetime
class Loan(Document):

	def validate(self):
		loan_type =  frappe.get_doc("Loan Type", self.loan_type)
		if self.loan_amount >= loan_type.maximum_loan_amount:
			frappe.throw("Loan Exceed Maximum Amount Of {}".format(loan_type.maximum_loan_amount))
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
				if count == self.repayment_period:
					principal_amount = principal_amount + balance_amount
					total_payment = total_payment + balance_amount
					balance_amount = 0
				self.append(
					"repayment_schedule",
					{
						"payment_date": payment_date,
						"principal_amount": principal_amount,
						"interest_amount": interest_amount,
						"total_payment": total_payment,
						"balance_loan_amount": balance_amount,
						"balance":total_payment
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
				if count == self.repayment_period:
					principal_amount = principal_amount + balance_amount
					total_payment = total_payment + balance_amount
					balance_amount = 0
				self.append(
					"repayment_schedule",
					{
						"payment_date": payment_date,
						"principal_amount": principal_amount,
						"interest_amount": interest_amount,
						"total_payment": total_payment,
						"balance_loan_amount": balance_amount,
						"balance":total_payment
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
						"balance":total_payment
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
def make_loan_disbursement(loan, applicant_type, applicant,loan_account,disbursed_account, pending_amount=0):
	disbursement_entry = frappe.new_doc("Loan Disbursement")
	disbursement_entry.loan = loan
	disbursement_entry.applicant_type = applicant_type
	disbursement_entry.applicant = applicant
	disbursement_entry.posting_date = nowdate()
	disbursement_entry.disbursed_amount = pending_amount
	disbursement_entry.loan_account = loan_account
	disbursement_entry.disbursed_account = disbursed_account
	return disbursement_entry

@frappe.whitelist()
def make_loan_security_pledge(loan, applicant_type, applicant):
	disbursement_entry = frappe.new_doc("Loan Security Pledge")
	disbursement_entry.loan = loan
	disbursement_entry.applicant_type = applicant_type
	disbursement_entry.applicant = applicant
	disbursement_entry.posting_date = nowdate()
	return disbursement_entry

@frappe.whitelist()
def make_loan_repayment(loan, applicant_type, applicant, applicant_name):
	loan_repayment = frappe.new_doc("Loan Repayment")
	loan_repayment.loan = loan
	loan_repayment.applicant_type = applicant_type
	loan_repayment.applicant = applicant
	loan_repayment.applicant_name = applicant_name
	loan_repayment.posting_date = nowdate()
	return loan_repayment

@frappe.whitelist()
def mark_as_write_off(loan,applicant_type,applicant,applicant_name,total_amount,interest_amount,paid_amount,loan_account):
	loan_write_off = frappe.new_doc("Loan Write Off")
	loan_write_off.loan = loan
	loan_write_off.applicant_type = applicant_type
	loan_write_off.applicant = applicant
	loan_write_off.applicant_name = applicant_name
	loan_write_off.posting_date = nowdate()
	loan_write_off.loan_amount = total_amount
	loan_write_off.interest_amount = interest_amount
	loan_write_off.paid_amount = paid_amount
	loan_write_off.loan_account = loan_account
	loan_write_off.balance = float(total_amount) - float(paid_amount)
	return loan_write_off

@frappe.whitelist()
def show_write_off_detail(loan):
	doc = frappe.db.sql("select name from `tabLoan Write Off` where loan = '{0}' and docstatus=1".format(loan),as_dict=1)
	return doc[0].name

@frappe.whitelist()
def get_total_loan():
	sql="""
	with data as(SELECT 
	coalesce(sum(loan_amount),0) loan_amount,
	coalesce(sum(total_interest),0) total_interest,
	coalesce(sum(total_amount),0) total_amount 
	FROM `tabLoan` 
	WHERE docstatus=1 AND STATUS IN ('Submitted'))
	, payment AS (
	SELECT 
	coalesce(SUM(a.payment_amount),0) payment_amount
	FROM `tabLoan Repayment` a
	INNER JOIN `tabLoan` b ON b.name = a.loan
	WHERE b.docstatus=1 AND b.STATUS IN ('Submitted') and a.docstatus = 1
	)
	, disbursement AS (
	SELECT 
	coalesce(SUM(a.disbursed_amount),0) disbursed_amount
	FROM `tabLoan Disbursement` a
	INNER JOIN `tabLoan` b ON b.name = a.loan
	WHERE b.docstatus=1 AND b.STATUS IN ('Submitted')  and a.docstatus = 1
	)
	select loan_amount amount,'Loan Amount' name from data
	union all
	select total_interest amount,'Total Interest' name from data
	union all
	select total_amount amount,'Total Amount' name from data
	union all
	select disbursed_amount amount,'Total Disbursed' name from disbursement
	union all
	select payment_amount amount,'Total Paid' name from payment
	"""
	data = frappe.db.sql(sql,as_dict=1)
	return data

@frappe.whitelist()
def get_mtd_loan():
	sql="""
	with data as(SELECT 
	coalesce(sum(loan_amount),0) loan_amount,
	coalesce(sum(total_interest),0) total_interest,
	coalesce(sum(total_amount),0) total_amount 
	FROM `tabLoan` 
	WHERE docstatus=1 AND STATUS IN ('Submitted') AND posting_date between '{0}' and '{1}')
	, payment AS (
	SELECT 
	coalesce(SUM(a.payment_amount),0) payment_amount
	FROM `tabLoan Repayment` a
	INNER JOIN `tabLoan` b ON b.name = a.loan
	WHERE b.docstatus=1 AND b.STATUS IN ('Submitted') AND b.posting_date between '{0}' and '{1}'  and a.docstatus = 1
	)
	, disbursement AS (
	SELECT 
	coalesce(SUM(a.disbursed_amount),0) disbursed_amount
	FROM `tabLoan Disbursement` a
	INNER JOIN `tabLoan` b ON b.name = a.loan
	WHERE b.docstatus=1 AND b.STATUS IN ('Submitted') AND b.posting_date between '{0}' and '{1}'  and a.docstatus = 1
	)
	select loan_amount amount,'MTD Loan Amount' name from data
	union all
	select total_interest amount,'MTD Total Interest' name from data
	union all
	select total_amount amount,'MTD Total Amount' name from data
	union all
	select disbursed_amount amount,'MTD Total Disbursed' name from disbursement
	union all
	select payment_amount amount,'MTD Total Paid' name from payment
	""".format(datetime.now().date().replace(day=1),datetime.now().date())
	data = frappe.db.sql(sql,as_dict=1)
	return data

@frappe.whitelist()
def get_today_loan():
	sql="""
	with data as(SELECT 
	coalesce(sum(loan_amount),0) loan_amount,
	coalesce(sum(total_interest),0) total_interest,
	coalesce(sum(total_amount),0) total_amount 
	FROM `tabLoan` 
	WHERE docstatus=1 AND STATUS IN ('Submitted') AND posting_date = '{0}' )
	, payment AS (
	SELECT 
	coalesce(SUM(a.payment_amount),0) payment_amount
	FROM `tabLoan Repayment` a
	INNER JOIN `tabLoan` b ON b.name = a.loan
	WHERE b.docstatus=1 AND b.STATUS IN ('Submitted') AND b.posting_date = '{0}'  and a.docstatus = 1
	)
	, disbursement AS (
	SELECT 
	coalesce(SUM(a.disbursed_amount),0) disbursed_amount
	FROM `tabLoan Disbursement` a
	INNER JOIN `tabLoan` b ON b.name = a.loan
	WHERE b.docstatus=1 AND b.STATUS IN ('Submitted') AND b.posting_date = '{0}'  and a.docstatus = 1
	)
	select loan_amount amount,'Loan Amount' name from data
	union all
	select total_interest amount,'Total Interest' name from data
	union all
	select total_amount amount,'Total Amount' name from data
	union all
	select disbursed_amount amount,'MTD Total Disbursed' name from disbursement
	union all
	select payment_amount amount,'Total Paid' name from payment
	""".format(datetime.now().date())
	data = frappe.db.sql(sql,as_dict=1)
	return data

@frappe.whitelist()
def get_loan_repayment():
	today_sql="""
	SELECT 
	parent loan,
	payment_date,
	principal_amount,
	interest_amount,
	total_payment
	FROM `tabLoan Repayment Schedule` a
	inner join `tabLoan` b on b.name = a.parent
	WHERE a.payment_date = CURDATE() AND balance > 0 and b.docstatus = 1 and b.status='Submitted'  and a.docstatus = 1
	""".format(datetime.now().date())
	today = frappe.db.sql(today_sql,as_dict=1)
	late_sql="""
	SELECT 
	parent loan,
	payment_date,
	principal_amount,
	interest_amount,
	total_payment,
	abs(DATEDIFF(payment_date,CURDATE())) day_lates
	FROM `tabLoan Repayment Schedule` a
	inner join `tabLoan` b on b.name = a.parent
	WHERE a.payment_date < CURDATE() AND balance > 0 and b.docstatus = 1 and b.status='Submitted' and a.docstatus = 1
	""".format(datetime.now().date())
	late = frappe.db.sql(late_sql,as_dict=1)
	return {"today":today,"late":late}
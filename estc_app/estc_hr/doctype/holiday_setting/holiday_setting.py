# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class HolidaySetting(Document):
	def validate(self):
		if self.is_new():
			generate_holiday(self)
			#generl public holiday
			fiscal_year = frappe.get_doc('Fiscal Year',self.fiscal_year)
			for holiday in fiscal_year.holidays:
				self.append("holidays", {
					"date": holiday.date, 
					"day": holiday.date.strftime('%A'),
					"is_day_off": holiday.is_day_off,
					"description": holiday.description
				})
		


def generate_holiday(self):
	weekend_list = generate_dates_on_specific_days(str(self.start_date),str(self.end_date),get_days(self))
	for weekend in weekend_list:
		self.append("weekend", {
			"date": weekend['date'],
			"is_day_off":1,
			"day": weekend['day']
		})


def generate_dates_on_specific_days(start_date_str, end_date_str, days_of_week):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    days_of_week_set = set(days_of_week)
    
    result_dates = []
    
    current_date = start_date
    while current_date <= end_date:
        if current_date.strftime('%A') in days_of_week_set:
            result_dates.append({"date":current_date.strftime('%Y-%m-%d'),"day":current_date.strftime('%A')})
        current_date += timedelta(days=1)
    
    return result_dates or []

def get_days(self):
	days=[]
	if self.monday==0:
		days.append('Monday')
	if self.tuesday==0:
		days.append('Tuesday')
	if self.wednesday==0:
		days.append('Wednesday')
	if self.thursday==0:
		days.append('Thursday')
	if self.friday==0:
		days.append('Friday')
	if self.saturday==0:
		days.append('Saturday')
	if self.sunday==0:
		days.append('Sunday')
	return days
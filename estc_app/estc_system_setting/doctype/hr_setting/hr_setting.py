# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HRSetting(Document):
	pass

@frappe.whitelist()
def update_image_to_employee(image):
	frappe.enqueue('estc_app.estc_system_setting.doctype.hr_setting.hr_setting.update_employee_background',image_path=image)


def update_employee_background(image_path):
	employees=frappe.db.get_list('Employee',pluck='name')
	for emp in employees:
		frappe.db.set_value('Employee',emp,'profile_background_photo',image_path)

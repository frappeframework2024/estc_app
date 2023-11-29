# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import (cint)
from frappe.utils.nestedset import NestedSet
import json

class Account(NestedSet):
	def autoname(self):
		self.name = get_autoname(self.account_number, self.account_name,)

def get_autoname(account_number, account_name):
	name=""
	if account_number:
		name = account_number + " - " + account_name
	else:
		name = account_name
	return name

@frappe.whitelist()
def add_ac(args=None):
	from frappe.desk.treeview import make_tree_args

	if not args:
		args = frappe.local.form_dict

	args.doctype = "Account"
	frappe.throw(json.dumps(args))
	args = make_tree_args(**args)

	ac = frappe.new_doc("Account")

	if args.get("ignore_permissions"):
		ac.flags.ignore_permissions = True
		args.pop("ignore_permissions")

	ac.update(args)

	if not ac.parent_account:
		ac.parent_account = args.get("parent")

	ac.old_parent = ""
	ac.freeze_account = "No"
	if cint(ac.get("is_root")):
		ac.parent_account = None
		ac.flags.ignore_mandatory = True

	ac.insert()

	return ac.name
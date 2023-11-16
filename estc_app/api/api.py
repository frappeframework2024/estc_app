import frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def query_doctypes(doctype, txt, searchfield, start, page_len, filters):
	user = filters.get("user")
	user_perms = frappe.utils.user.UserPermissions(user)
	user_perms.build_permissions()
	can_read = user_perms.can_read  # Does not include child tables
	include_single_doctypes = filters.get("include_single_doctypes")

	single_doctypes = [d[0] for d in frappe.db.get_values("DocType", {"issingle": 1})]
	return [
		[dt]
		for dt in can_read
		if txt.lower().replace("%", "") in dt.lower()
		and (include_single_doctypes or dt not in single_doctypes)
	]

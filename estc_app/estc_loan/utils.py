import frappe
def add_gl_entry(date,account,debit,credit,against_voucher_type,against_voucher,voucher_type,voucher_no,remark):
    gle = frappe.new_doc("General Ledger Entry")
    gle.posting_date = date
    gle.account = account
    gle.debit = debit
    gle.credit = credit
    gle.against_voucher_type = against_voucher_type
    gle.against_voucher = against_voucher
    gle.voucher_type = voucher_type
    gle.voucher_no = voucher_no
    gle.remark = remark
    gle.save()
    
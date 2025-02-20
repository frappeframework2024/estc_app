import frappe

def execute(filters=None):
    return get_columns(filters), get_data(filters)

def get_columns(filters):
    columns = []
    columns.append({'fieldname':"employee",'label':"Employee",'fieldtype':'Link','options':'Employee','align':'center','width':130})
    columns.append({'fieldname':"employee_name",'label':"Employee Name",'align':'left','width':130})
    columns.append({'fieldname':"annual_leave",'label':"Annual Leave",'fieldtype':'Float',"precision":2,'align':'center','width':130, 'click': 'open_annual_leave_report'})
    columns.append({'fieldname':"aluse",'label':"AL USE",'align':'center',"precision":2,'fieldtype':'Float','width':130})
    columns.append({'fieldname':"al_balance",'label':"AL Balance","precision":2,'align':'center','fieldtype':'Float','width':130})
    columns.append({'fieldname':"over_time",'label':"Over Time","precision":2,'align':'center','fieldtype':'Float','width':130})
    columns.append({'fieldname':"otuse",'label':"OT USE","precision":2,'align':'center','fieldtype':'Float','width':130})
    columns.append({'fieldname':"ot_balance",'label':"Ot Balance","precision":2,'align':'center','fieldtype':'Float','width':130})
    columns.append({'fieldname':"alandotbalance",'label':"AL & OT Balance","precision":2,'align':'center','fieldtype':'Float','width':130})
    return columns

def get_data(filters):
    data = []
    
    # Get aggregated leave data for each employee (sum the leave data)
    employees = frappe.db.sql(""" 
        SELECT employee, employee_name,
               SUM(CASE WHEN leave_type = 'Annual Leave' THEN max_leave ELSE 0 END) AS annual_leave,
               SUM(CASE WHEN leave_type = 'Annual Leave' THEN use_leave ELSE 0 END) AS aluse,
               SUM(CASE WHEN leave_type = 'Annual Leave' THEN balance ELSE 0 END) AS al_balance,
               SUM(CASE WHEN leave_type = 'Over Time' THEN max_leave ELSE 0 END) AS over_time,
               SUM(CASE WHEN leave_type = 'Over Time' THEN use_leave ELSE 0 END) AS otuse,
               SUM(CASE WHEN leave_type = 'Over Time' THEN balance ELSE 0 END) AS ot_balance,
               SUM(CASE WHEN leave_type = 'Annual Leave' THEN balance ELSE 0 END) + 
               SUM(CASE WHEN leave_type = 'Over Time' THEN balance ELSE 0 END) AS alandotbalance 
        FROM `tabEmployee Attendance Leave Count`
        {0}
        GROUP BY employee, employee_name
    """.format(get_conditions(filters)), filters, as_dict=True)

    for emp in employees:
        data.append({
            'employee': emp['employee'],
            'employee_name': emp['employee_name'],
            'over_time': emp['over_time'],
            'annual_leave': emp['annual_leave'],
            'aluse': emp['aluse'],
            'al_balance': emp['al_balance'],
            'otuse': emp['otuse'],
            'ot_balance': emp['ot_balance'],
            'alandotbalance': emp['alandotbalance']
        })

    return data

def get_conditions(filters):
    select_filters = []
    
    if filters.get('fiscal_year'):
        select_filters.append("fiscal_year = %(fiscal_year)s")
    
    if filters.get('department') and len(filters['department']) > 0:
        select_filters.append("department in %(department)s")
    
    if filters.get('leave_type') and len(filters['leave_type']) > 0:
        select_filters.append("leave_type in %(leave_type)s")
    
    if len(select_filters) > 0:
        return " WHERE " + " AND ".join(select_filters)
    else:
        return ''

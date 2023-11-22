frappe.views.calendar['Leave Request'] = {
    field_map: {
        start: 'start',
        end: 'end',
        id: 'name',
        title: 'title',
        status: 'leave_status',
        color: 'backgroundColor'
    },
    gantt: false,
    get_events_method: 'estc_app.estc_hr.doctype.leave_request.leave_request.get_events',
}
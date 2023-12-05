frappe.views.calendar['OT Request'] = {
    field_map: {
        start: 'request_date',
        end: 'request_date',
        id: 'name',
        title: 'title',
        status: 'leave_status',
        color: 'backgroundColor'
    },
    gantt: false,
    get_events_method: 'estc_app.estc_hr.doctype.ot_request.ot_request.get_events',
}
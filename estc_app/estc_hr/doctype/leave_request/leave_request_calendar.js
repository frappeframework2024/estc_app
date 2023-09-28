frappe.views.calendar['Leave Request'] = {
    field_map: {
        start: 'start_date',
        end: 'to_date',
        id: 'name',
        // allDay: 'all_day',
        title: 'employee_name',
        status: 'status',
        color: 'color'
    },
    // get_events_method: 'frappe.desk.doctype.event.event.get_events'
}
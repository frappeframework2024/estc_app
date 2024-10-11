frappe.listview_settings['Employee'] = {
    hide_name_column: true,
    
    formatters: {
        photo: function (value, field, doc) {
            return `<img src='${doc.photo || "/assets/estc_app/images/avatar-2.png"}' style='border-radius: 50%;height:35px; margin-right:10px;margin-left:5px'/>`;
        },

    },
    get_indicator(doc) {
        if (doc.is_exit)
            return  [`<span style="font-size: 12px;background-color:red; color:white; padding: 2px 10px;border-radius: 10px;">${__('Exit')}</span>`]; 
        if (doc.status.includes("Active"))
            return  [`<span style="font-size: 12px;background-color:#17ab07; color:white; padding: 2px 10px;border-radius: 10px;">${__(doc.status)}</span>`]; 
        if (doc.status.includes("Suspended"))
            return  [`<span style="font-size: 12px;background-color:#ebca0e; color:white; padding: 2px 10px;border-radius: 10px;">${__(doc.status)}</span>`]; 
        if (doc.status.includes("Inactive"))
            return  [`<span style="font-size: 12px;background-color:#de981f; color:white; padding: 2px 10px;border-radius: 10px;">${__(doc.status)}</span>`]; 
        if (doc.status.includes("Left"))
            return  [`<span style="font-size: 12px;background-color:#1f1e1c; color:white; padding: 2px 10px;border-radius: 10px;">${__(doc.status)}</span>`]; 
    },
    onload: function (listview) {
        listview.page.add_action_item(__("Assign To Shift"), () => {
            var d = new frappe.ui.Dialog({
                title: __("Shift Assignment"),
                fields: [
                    {
                        'label': __('Working Shift'),
                        'fieldtype': 'MultiSelectList',
                        'fieldname': 'shifts',
                        get_data: function (txt) {
                            return frappe.db.get_link_options('Working Shift', txt,{
                                docstatus: 1,
                            });

                        },
                    },
                ],
                primary_action: function () {
                    if (d.get_values().shifts) {
                        employees = listview.get_checked_items()
                        const result = employees.map(emp => emp.name).join(',');
                        shifts = d.get_values().shifts.join(',')

                        frappe.call({
                            "method": 'estc_app.estc_hr.doctype.shift_assignment.shift_assignment.assign_employee_to_shift',
                            "args": {
                                "employees": result,
                                "shifts": shifts
                            },
                            callback: function (r) {
                                frappe.show_alert({
                                    message: __("Assignment successfully"),
                                    indicator: "green",
                                });
                                d.hide()

                            }
                        });
                    }else{
                        frappe.show_alert({
                            message: __("Please select working shift"),
                            indicator: "orange",
                        });
                    }

                }
            });
            d.show();
        });
    }
}
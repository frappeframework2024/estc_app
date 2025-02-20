frappe.query_reports["Employee Leave and Overtime Summary"] = {
    "filters": [
        {
            fieldname: "fiscal_year",
            label: "Academic Year",
            fieldtype: "Link",
            options: "Fiscal Year",
            "reqd": 1,
        },
        {
            fieldname: "department",
            label: "Department",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_link_options('Department', txt, {"is_group": ['=', 0]});
            },
        },
        {
            fieldname: "leave_type",
            label: "Leave Type",
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_link_options('Leave Type', txt);
            },
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (column.fieldname === 'aluse') {
            value = `<a href="#" class="annual-leave-link" data-employee="${data.employee}" data-employee-name="${data.employee_name}" style="color: blue;">${value}</a>`;
        }
        if (column.fieldname === 'over_time') {
            value = `<a href="#" class="over_time-link" data-employee="${data.employee}" data-employee-name="${data.employee_name}" style="color: blue;">${value}</a>`;
        }
        if (column.fieldname === 'otuse') {
            value = `<a href="#" class="otuse-link" data-employee="${data.employee}" data-employee-name="${data.employee_name}" style="color: blue;">${value}</a>`;
        }
        if (column.fieldname === 'annual_leave') {
            value = `<a href="#" class="annual_leave-link" data-employee="${data.employee}" data-employee-name="${data.employee_name}" style="color: blue;">${value}</a>`;
        }

        return value;
    },

    "onload": function(report) {
        $(document).on("click", ".annual-leave-link", function(e) {
            e.preventDefault();
            var employee = $(this).data('employee');
            var employeeName = $(this).data('employee-name');
            open_report(employee, employeeName , "Annual Leave" , "Leave Use Report");
        });
        $(document).on("click", ".annual_leave-link", function(e) {
            e.preventDefault();
            var employee = $(this).data('employee');
            var employeeName = $(this).data('employee-name');
            open_report(employee, employeeName , "All" , "Leave Use Report");
        });
        $(document).on("click", ".otuse-link", function(e) {
            e.preventDefault();
            var employee = $(this).data('employee');
            var employeeName = $(this).data('employee-name');
            open_report(employee, employeeName , "Over Time" , "Leave Use Report");
        });
        $(document).on("click", ".over_time-link", function(e) {
            e.preventDefault();
            var employee = $(this).data('employee');
            var employeeName = $(this).data('employee-name');
            open_report(employee, employeeName , "" , "OT Report");
        });
    }
};

function open_report(employee, employeeName, leave_type = null, report_name) {
    const fiscalYearFilter = frappe.query_report.get_filter_value("fiscal_year");
    const filters = {
        employee: employee,
        fiscal_year: fiscalYearFilter
    };

    if (leave_type && leave_type != "" ) {
            filters.leave_type = leave_type;
    }

    frappe.call({
        method: "frappe.desk.query_report.run",
        args: {
            report_name: report_name,
            filters: filters
        },
        callback: function(r) {
            if (r.message) {
                var dialog = new frappe.ui.Dialog({
                    title: report_name + " - " + employeeName,
                    size: 'large',
                    fields: [
                        {
                            fieldtype: "HTML",
                            fieldname: "report_content"
                        }
                    ],
                    primary_action_label: "Close",
                    primary_action: function() {
                        dialog.hide();
                    }
                });

                dialog.$wrapper.find('.modal-dialog').css({
                    'max-width': '90%',
                    'width': '90%'
                });

                let content = "";
                let content_ot = "";

                function processAndDisplayContent() {
                    // Combine both tables before rendering
                    let finalContent = content_ot + "<br>" + content;
                    dialog.fields_dict.report_content.$wrapper.html(finalContent);
                    dialog.show();
                }

                    frappe.call({
                        method: "frappe.desk.query_report.run",
                        args: {
                            report_name: "Carry Over Report",
                            filters: {
                                employee: employee,
                                fiscal_year: fiscalYearFilter
                            }
                        },
                        callback: function(response) {
                            if (response.message.result.length > 0) {
                                content_ot = '<h5> Carry Over </h5> <table style="margin-top:0 !important" class="table table-bordered"><thead><tr>';
                                const firstRow = response.message.result[0];
                                Object.keys(firstRow).forEach(key => {
                                    content_ot += `<th>${key}</th>`;
                                });
                                content_ot += '</tr></thead><tbody>';
                                response.message.result.forEach(row => {
                                    content_ot += '<tr>';
                                    Object.values(row).forEach(cell => {
                                        content_ot += `<td>${cell !== null ? cell : ''}</td>`;
                                    });
                                    content_ot += '</tr>';
                                });
                                content_ot += '</tbody></table>';
                            } else {
                                content_ot = "<center>No Data for Carry Over Report</center>";
                            }
                            processAndDisplayContent();
                        }
                    });
                if (typeof r.message === "string") {
                    content = r.message;
                } else if (Array.isArray(r.message.result) && r.message.result.length > 0) {
                    content = '<h5> Leave Use  </h5> <table style="margin-top:0 !important" class="table table-bordered"><thead><tr>';
                    const firstRow = r.message.result[0];
                    Object.keys(firstRow).forEach(key => {
                        content += `<th>${key}</th>`;
                    });
                    content += '</tr></thead><tbody>';
                    r.message.result.forEach(row => {
                        content += '<tr>';
                        Object.values(row).forEach(cell => {
                            content += `<td>${cell !== null ? cell : ''}</td>`;
                        });
                        content += '</tr>';
                    });
                    content += '</tbody></table>';
                } else {
                    content = "<center>No Data</center>";
                }

                if (report_name !== "Leave Use Report") {
                    processAndDisplayContent();
                }
            } else {
                console.log("No data returned for the report.");
            }
        },
        error: function(error) {
            console.error("Error fetching report:", error);
        }
    });
}

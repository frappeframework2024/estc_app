frappe.listview_settings['Employee Check In Log']={
    add_fields: ['photo','employe_device_id'],
    hide_name_column:true,
    formatters: {
        photo:function(value, field, doc) {
            return `<img src='${doc.photo || "/assets/estc_app/images/avatar-2.png" }' style='border-radius: 50%;height:35px; margin-right:10px;margin-left:5px'/>`;
        },
        
    },
   
    
}
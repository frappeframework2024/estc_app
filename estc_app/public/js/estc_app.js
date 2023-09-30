window.addEventListener('load', function () {
    if (frappe.session.user == 'Administrator'){
        const getParent = document.querySelector('#page-Workspaces')
        const childElement = getParent.querySelector('.flex.col.page-actions.justify-content-end');
        childElement.style.display = 'none';
    }
})
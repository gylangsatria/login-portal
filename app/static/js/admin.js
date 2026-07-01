/* ===== Admin Panel JavaScript ===== */

document.addEventListener('DOMContentLoaded', function() {
    // ---- App CRUD ----
    window.saveApp = function() {
        const id = document.getElementById('appId').value;
        const data = {
            name: document.getElementById('appName').value,
            description: document.getElementById('appDescription').value,
            url: document.getElementById('appUrl').value,
            icon: document.getElementById('appIcon').value,
            order: parseInt(document.getElementById('appOrder').value) || 0,
            is_active: true
        };
        
        const url = id ? `/admin/apps/${id}` : '/admin/apps';
        const method = id ? 'PUT' : 'POST';
        
        fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            location.reload();
        })
        .catch(error => alert('Error: ' + error));
    };
    
    document.querySelectorAll('.edit-app-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-app-id');
            const row = this.closest('tr');
            const cells = row.querySelectorAll('td');
            
            document.getElementById('appId').value = id;
            document.getElementById('appName').value = cells[0].textContent.trim();
            document.getElementById('appDescription').value = cells[1].textContent.trim() === '-' ? '' : cells[1].textContent.trim();
            document.getElementById('appUrl').value = cells[2].textContent.trim();
            document.getElementById('appIcon').value = cells[0].querySelector('i').className.replace('fas ', '');
            document.getElementById('appOrder').value = cells[4].textContent.trim();
            
            const config = document.getElementById('admin-config');
            document.querySelector('#addAppModal .modal-title').textContent = config.dataset.editApp;
            new bootstrap.Modal(document.getElementById('addAppModal')).show();
        });
    });
    
    document.querySelectorAll('.delete-app-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-app-id');
            const config = document.getElementById('admin-config');
            if (confirm(config.dataset.appDeleteConfirm)) {
                fetch(`/admin/apps/${id}`, {method: 'DELETE'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                })
                .catch(error => alert('Error: ' + error));
            }
        });
    });
    
    document.getElementById('addAppModal').addEventListener('hidden.bs.modal', function () {
        document.getElementById('appForm').reset();
        document.getElementById('appId').value = '';
        const config = document.getElementById('admin-config');
        document.querySelector('#addAppModal .modal-title').textContent = config.dataset.addApp;
    });
    
    // ---- User CRUD ----
    window.saveUser = function() {
        const id = document.getElementById('userId').value;
        const data = {
            full_name: document.getElementById('userFullName').value,
            username: document.getElementById('userUsername').value,
            role: document.getElementById('userRole').value,
            language: document.getElementById('userLanguage').value
        };
        
        const password = document.getElementById('userPassword').value;
        const isEdit = !!id;
        
        if (!isEdit && !password) {
            const config = document.getElementById('admin-config');
            alert(config.dataset.passwordRequired);
            return;
        }
        if (password) {
            data.password = password;
        }
        
        const url = isEdit ? `/admin/users/${id}` : '/admin/users';
        const method = isEdit ? 'PUT' : 'POST';
        
        fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json().then(r => ({status: response.status, body: r})))
        .then(function(result) {
            if (result.status >= 400) {
                alert(result.body.error || 'Error');
            } else {
                alert(result.body.message);
                location.reload();
            }
        })
        .catch(error => alert('Error: ' + error));
    };
    
    document.querySelectorAll('.edit-user-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-user-id');
            const row = this.closest('tr');
            const cells = row.querySelectorAll('td');
            const config = document.getElementById('admin-config');
            
            document.getElementById('userId').value = id;
            document.getElementById('userFullName').value = cells[0].textContent.trim();
            document.getElementById('userUsername').value = cells[1].textContent.trim();
            document.getElementById('userRole').value = cells[2].textContent.trim().toLowerCase();
            document.getElementById('userPassword').value = '';
            document.getElementById('userPassword').removeAttribute('required');
            document.getElementById('passwordHelp').textContent = config.dataset.passwordOptional;
            
            const langText = cells[3].textContent.trim();
            document.getElementById('userLanguage').value = langText === 'English' ? 'en' : 'id';
            
            document.querySelector('#addUserModal .modal-title').textContent = config.dataset.editUser;
            new bootstrap.Modal(document.getElementById('addUserModal')).show();
        });
    });
    
    document.querySelectorAll('.delete-user-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-user-id');
            const config = document.getElementById('admin-config');
            if (confirm(config.dataset.userDeleteConfirm)) {
                fetch(`/admin/users/${id}`, {method: 'DELETE'})
                .then(response => response.json().then(r => ({status: response.status, body: r})))
                .then(function(result) {
                    if (result.status >= 400) {
                        alert(result.body.error || 'Error');
                    } else {
                        alert(result.body.message);
                        location.reload();
                    }
                })
                .catch(error => alert('Error: ' + error));
            }
        });
    });
    
    document.querySelectorAll('.reset-password-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-user-id');
            const config = document.getElementById('admin-config');
            if (confirm(config.dataset.userResetPasswordConfirm)) {
                fetch(`/admin/users/${id}/reset-password`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({password: 'user123'})
                })
                .then(response => response.json().then(r => ({status: response.status, body: r})))
                .then(function(result) {
                    if (result.status >= 400) {
                        alert(result.body.error || 'Error');
                    } else {
                        alert(result.body.message);
                        location.reload();
                    }
                })
                .catch(error => alert('Error: ' + error));
            }
        });
    });
    
    document.getElementById('addUserModal').addEventListener('hidden.bs.modal', function () {
        document.getElementById('userForm').reset();
        document.getElementById('userId').value = '';
        document.getElementById('userPassword').setAttribute('required', 'required');
        const config = document.getElementById('admin-config');
        document.getElementById('passwordHelp').textContent = config.dataset.passwordMinLength;
        document.querySelector('#addUserModal .modal-title').textContent = config.dataset.addUser;
    });
});

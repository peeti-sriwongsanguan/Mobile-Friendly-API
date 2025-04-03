//static/js/script.js
// Get the API URL from the current location
function getApiUrl() {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;

    return `${protocol}//${hostname}${port ? ':' + port : ''}`;
}

const API_URL = getApiUrl();

document.addEventListener('DOMContentLoaded', function() {
    const addRowButton = document.getElementById('addRow');
    const materialsTable = document.getElementById('materialsTable').getElementsByTagName('tbody')[0];
    const materialForm = document.getElementById('materialForm');
    const messageDiv = document.getElementById('message');

    // Set today's date as default
    document.getElementById('date').valueAsDate = new Date();

    // Add row button click handler
    addRowButton.addEventListener('click', function() {
        const rowCount = materialsTable.rows.length;
        const newRow = materialsTable.insertRow();

        newRow.innerHTML = `
            <td>${rowCount + 1}</td>
            <td><input type="text" name="materialDesc"></td>
            <td><input type="text" name="materialCode"></td>
            <td><input type="number" name="quantity" min="0" step="1" onkeydown="return event.keyCode !== 190 && event.keyCode !== 188"></td>
            <td><input type="text" name="unit"></td>
            <td><button type="button" class="remove-row">ลบ</button></td>
        `;

        attachRemoveRowHandler(newRow.querySelector('.remove-row'));
    });

    // Attach remove row handlers to existing rows
    document.querySelectorAll('.remove-row').forEach(button => {
        attachRemoveRowHandler(button);
    });

    // Form submission handler
    materialForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Basic validation
        const requesterName = document.getElementById('requesterName').value.trim();
        if (!requesterName) {
            showMessage('กรุณาระบุชื่อผู้เบิก', 'error');
            return;
        }

        // Check if at least one item has a description
        let hasItems = false;
        const rows = materialsTable.rows;
        for (let i = 0; i < rows.length; i++) {
            const desc = rows[i].querySelector('input[name="materialDesc"]').value.trim();
            if (desc) {
                hasItems = true;
                break;
            }
        }

        if (!hasItems) {
            showMessage('กรุณาระบุรายการวัสดุอย่างน้อย 1 รายการ', 'error');
            return;
        }

        // Get form data
        const formData = {
            vehicle_registration: document.getElementById('vehicleReg').value,
            date: document.getElementById('date').value,
            requester_name: requesterName,
            recipient_name: document.getElementById('recipientName').value,
            items: []
        };

        // Get items from table
        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const materialDesc = row.querySelector('input[name="materialDesc"]').value.trim();

            // Skip empty rows
            if (!materialDesc) continue;

            formData.items.push({
                item_number: i + 1,
                material_description: materialDesc,
                material_code: row.querySelector('input[name="materialCode"]').value,
                quantity: parseInt(row.querySelector('input[name="quantity"]').value) || 0,
                unit: row.querySelector('input[name="unit"]').value
            });
        }

        // Show loading message
        showMessage('กำลังบันทึกข้อมูล...', 'info');

        // Submit to API
        fetch(`${API_URL}/forms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'เกิดข้อผิดพลาดในการบันทึกข้อมูล');
                });
            }
            return response.json();
        })
        .then(data => {
            // Show success message
            showMessage(`บันทึกรายการสำเร็จ (เลขที่: ${data.id})`, 'success');

            // Reset form
            materialForm.reset();
            document.getElementById('date').valueAsDate = new Date();

            // Clear table except first row
            while (materialsTable.rows.length > 1) {
                materialsTable.deleteRow(1);
            }

            // Clear first row inputs
            const firstRow = materialsTable.rows[0];
            firstRow.querySelectorAll('input').forEach(input => {
                input.value = '';
            });
        })
        .catch(error => {
            showMessage('เกิดข้อผิดพลาด: ' + error.message, 'error');
            console.error('Error:', error);
        });
    });

    // Helper function to attach remove row handler
    function attachRemoveRowHandler(button) {
        button.addEventListener('click', function() {
            const row = this.parentNode.parentNode;
            if (materialsTable.rows.length > 1) {
                row.parentNode.removeChild(row);
                updateRowNumbers();
            } else {
                // If it's the last row, just clear it
                row.querySelectorAll('input').forEach(input => {
                    input.value = '';
                });
            }
        });
    }

    // Update row numbers after deletion
    function updateRowNumbers() {
        const rows = materialsTable.rows;
        for (let i = 0; i < rows.length; i++) {
            rows[i].cells[0].textContent = i + 1;
        }
    }

    // Show message helper
    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = `message ${type}`;
        messageDiv.style.display = 'block';

        // Hide message after 5 seconds
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
});
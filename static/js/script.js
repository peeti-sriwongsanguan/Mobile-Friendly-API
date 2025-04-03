//static/js/script.js
// Get the API URL from the current location
function getApiUrl() {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;

    return `${protocol}//${hostname}${port ? ':' + port : ''}`;
}

const API_URL = getApiUrl();

// Automotive parts dictionary for auto-suggestions
const AUTOMOTIVE_PARTS = [
    { thai: "ขากระจก", english: "Mirror Bracket", code: "MIR1" },
    { thai: "ไฟหน้า", english: "Headlight", code: "HEA1" },
    { thai: "ประตู", english: "Door", code: "DOO1" },
    { thai: "กระจก", english: "Window/Glass", code: "WIN1" },
    { thai: "ไฟท้าย", english: "Tail Light", code: "TAI1" },
    { thai: "กระจังหน้า", english: "Front Grille", code: "FRO1" },
    { thai: "กันชนหน้า", english: "Front Bumper", code: "FRO2" },
    { thai: "ไฟเลี้ยว", english: "Turn Signal", code: "TUR1" },
    { thai: "เบ้ามือโด", english: "Door Handle Housing", code: "DOO2" },
    { thai: "ที่ปัดน้ำฝน", english: "Windshield Wiper", code: "WIN2" },
    { thai: "แก้มไฟหรือหน้า", english: "Light Panel or Front Cover", code: "LIG1" },
    { thai: "พลาสติกบังฝุ่นหลัง", english: "Rear Dust Cover (Plastic)", code: "REA1" },
    { thai: "พลาสติกมุมกันชน", english: "Bumper Corner Plastic", code: "BUM1" },
    { thai: "พลาสติกปิดมุมกันชน", english: "Bumper Corner Cover", code: "BUM2" },
    { thai: "ไฟในกันชน", english: "Bumper Light", code: "BUM3" },
    { thai: "พลาสติกปิดกันชน", english: "Bumper Cover", code: "BUM4" },
    { thai: "กระป๋องดีดน้ำ", english: "Washer Fluid Container", code: "WAS1" },
    { thai: "แป้นจ่ายเบรคตรัซ", english: "Brake/Clutch Pedal", code: "BRA1" },
    { thai: "มือจับแยงหน้า", english: "Front Handle", code: "FRO3" },
    { thai: "กันสาดประตู", english: "Door Visor/Rain Guard", code: "DOO3" },
    { thai: "ซองไฟหน้า", english: "Headlight Housing", code: "HEA2" },
    { thai: "พลาสติกบนไฟเลี้ยว", english: "Plastic Above Turn Signal", code: "PLA1" },
    { thai: "เพ้องยกกระจกประตู", english: "Window Lifter Cover", code: "WIN3" },
    { thai: "สักหลาดกระจกประตู", english: "Door Window Felt/Seal", code: "DOO4" },
    { thai: "ขากันชน", english: "Bumper Bracket", code: "BUM5" },
    { thai: "ยางกระจกหน้า", english: "Front Windshield Rubber", code: "FRO4" },
    { thai: "แผงหน้ากระจัง", english: "Front Grille Panel", code: "FRO5" },
    { thai: "แผ่นรองแผงหน้า", english: "Front Panel Support Plate", code: "FRO6" },
    { thai: "โล่ไก่", english: "Radiator Shield", code: "RAD1" },
    { thai: "ไฟเลี้ยวข้างประตู", english: "Door Side Turn Signal", code: "DOO5" },
    { thai: "ไฟหลังคา", english: "Roof Light", code: "ROO1" },
    { thai: "มือเปิดประตู", english: "Door Handle", code: "DOO6" },
    { thai: "บังโคลนหน้า", english: "Front Fender", code: "FRO7" },
    { thai: "ไฟป้ายทะเบียน", english: "License Plate Light", code: "LIC1" },
    { thai: "ยางรอบกระจก", english: "Window Rubber Seal", code: "WIN4" }
];

document.addEventListener('DOMContentLoaded', function() {
    const addRowButton = document.getElementById('addRow');
    const materialsTable = document.getElementById('materialsTable').getElementsByTagName('tbody')[0];
    const materialForm = document.getElementById('materialForm');
    const messageDiv = document.getElementById('message');

    // Set today's date as default
    document.getElementById('date').valueAsDate = new Date();

    // Initialize datalist for material description suggestions
    initializePartsSuggestions();

    // Add row button click handler
    addRowButton.addEventListener('click', function() {
        const rowCount = materialsTable.rows.length;
        const newRow = materialsTable.insertRow();

        newRow.innerHTML = `
            <td>${rowCount + 1}</td>
            <td>
                <input type="text" name="materialDesc" list="parts-list" autocomplete="off">
            </td>
            <td><input type="text" name="materialCode"></td>
            <td><input type="number" name="quantity" min="0" step="1" onkeydown="return event.keyCode !== 190 && event.keyCode !== 188"></td>
            <td><input type="text" name="unit"></td>
            <td><button type="button" class="remove-row">ลบ</button></td>
        `;

        attachRemoveRowHandler(newRow.querySelector('.remove-row'));
        attachMaterialDescriptionEvents(newRow.querySelector('input[name="materialDesc"]'));
    });

    // Update existing row to have datalist
    const firstRow = materialsTable.rows[0];
    const firstDescInput = firstRow.querySelector('input[name="materialDesc"]');
    firstDescInput.setAttribute('list', 'parts-list');
    firstDescInput.setAttribute('autocomplete', 'off');
    attachMaterialDescriptionEvents(firstDescInput);

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

    // Helper function to initialize parts suggestion datalist
    function initializePartsSuggestions() {
        // Create datalist element if it doesn't exist
        if (!document.getElementById('parts-list')) {
            const datalist = document.createElement('datalist');
            datalist.id = 'parts-list';

            // Add options from parts dictionary
            AUTOMOTIVE_PARTS.forEach(part => {
                const option = document.createElement('option');
                option.value = part.thai;
                option.dataset.english = part.english;
                option.dataset.code = part.code;
                datalist.appendChild(option);
            });

            document.body.appendChild(datalist);
        }
    }

    // Helper function to attach events to material description input
    function attachMaterialDescriptionEvents(input) {
        // Add change/input event to fill in the code
        input.addEventListener('input', function() {
            const row = this.closest('tr');
            const codeInput = row.querySelector('input[name="materialCode"]');

            // Try to find matching part
            const selectedPart = AUTOMOTIVE_PARTS.find(part => part.thai === this.value);
            if (selectedPart && codeInput) {
                codeInput.value = selectedPart.code;
            }
        });
    }

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
// This file contains JavaScript functions for the report generation
// and download functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize download report button
    const downloadReportBtn = document.getElementById('download-report-btn');
    if (downloadReportBtn) {
        downloadReportBtn.addEventListener('click', downloadReport);
    }
});

// Function to download the report as PDF
function downloadReport() {
    // Show loading indicator
    const btnText = document.getElementById('download-report-btn').innerHTML;
    document.getElementById('download-report-btn').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
    
    // Call the backend to generate the PDF
    fetch('/download-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Restore button text
        document.getElementById('download-report-btn').innerHTML = btnText;
        
        if (data.success) {
            // In a real implementation, this would download the actual PDF
            // For this simplified version, we'll just show a success message
            showDownloadSuccess();
            
            // In a production app, you would trigger the download like this:
            // window.location.href = data.download_url;
        } else {
            showDownloadError(data.error);
        }
    })
    .catch(error => {
        // Restore button text
        document.getElementById('download-report-btn').innerHTML = btnText;
        console.error('Download error:', error);
        showDownloadError('An error occurred while generating the report.');
    });
}

// Function to show download success message
function showDownloadSuccess() {
    // Create a Bootstrap alert to show the success message
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show mt-3" role="alert">
            <strong>Success!</strong> Your report has been generated. 
            <span>In a production implementation, the PDF would download automatically.</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Add the alert to the page
    const alertContainer = document.createElement('div');
    alertContainer.innerHTML = alertHtml;
    document.querySelector('.card-body').prepend(alertContainer.firstChild);
    
    // Automatically dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Function to show download error message
function showDownloadError(errorMessage) {
    // Create a Bootstrap alert to show the error message
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
            <strong>Error!</strong> ${errorMessage}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Add the alert to the page
    const alertContainer = document.createElement('div');
    alertContainer.innerHTML = alertHtml;
    document.querySelector('.card-body').prepend(alertContainer.firstChild);
    
    // Automatically dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Function to print the report
function printReport() {
    window.print();
}

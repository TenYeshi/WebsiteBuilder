/**
 * Application Manager for Ten Yeshi Word Processor
 * Handles adding, editing, and deleting applications
 */

// Check if the script is already defined to avoid conflicts
if (typeof TenYeshiApplicationManager === 'undefined') {

// Define a namespace for our application manager
window.TenYeshiApplicationManager = {};

document.addEventListener("DOMContentLoaded", () => {
  // Detect operating mode from URL
  const urlParams = new URLSearchParams(window.location.search);
  const mode = urlParams.get('mode') || 'add';
  const applicationId = urlParams.get('id');
  
  // DOM Elements
  const editor = document.getElementById("editor");
  const saveBtn = document.getElementById("saveBtn");
  const openBtn = document.getElementById("openBtn");
  const saveDialog = document.getElementById("saveDialog");
  const openDialog = document.getElementById("openDialog");
  const documentName = document.getElementById("documentName");
  const documentList = document.getElementById("documentList");
  const closeSaveDialog = document.getElementById("closeSaveDialog");
  const closeOpenDialog = document.getElementById("closeOpenDialog");
  const confirmSaveBtn = document.getElementById("confirmSaveBtn");
  const confirmOpenBtn = document.getElementById("confirmOpenBtn");
  const cancelSaveBtn = document.getElementById("cancelSaveBtn");
  const cancelOpenBtn = document.getElementById("cancelOpenBtn");
  const dialogBackground = document.getElementById("dialogBackground");
  
  // Application form fields
  const applicantName = document.getElementById("applicantName");
  const applicantEmail = document.getElementById("applicantEmail");
  const fatherName = document.getElementById("fatherName");
  const rollNumber = document.getElementById("rollNumber");
  const className = document.getElementById("className");
  const dateOfBirth = document.getElementById("dateOfBirth");
  const phoneNumber = document.getElementById("phoneNumber");
  const address = document.getElementById("address");
  const applicationFields = document.getElementById("applicationFields");
  
  let currentDocumentId = null;
  let selectedDocumentId = null;
  
  // Initialize page based on mode
  function initPageByMode() {
    const saveDialogTitle = document.getElementById("saveDialogTitle");
    const openDialogTitle = document.getElementById("openDialogTitle");
    
    if (mode === 'add') {
      document.title = "Ten Yeshi - Add Application";
      saveDialogTitle.innerHTML = '<i class="fas fa-save me-2"></i>Create New Application';
      applicationFields.style.display = 'block';
      
      // If in add mode, load a blank document
      currentDocumentId = null;
      editor.innerHTML = "Type here...";
    } 
    else if (mode === 'edit') {
      document.title = "Ten Yeshi - Edit Application";
      saveDialogTitle.innerHTML = '<i class="fas fa-save me-2"></i>Update Application';
      openDialogTitle.innerHTML = '<i class="fas fa-folder-open me-2"></i>Select Application to Edit';
      applicationFields.style.display = 'block';
      
      // If application ID is provided, load that specific application
      if (applicationId) {
        loadApplication(applicationId);
      } else {
        // Show open dialog automatically if no ID provided
        showOpenDialog();
      }
    } 
    else if (mode === 'delete') {
      document.title = "Ten Yeshi - Delete Application";
      saveDialogTitle.innerHTML = '<i class="fas fa-trash me-2"></i>Delete Application';
      openDialogTitle.innerHTML = '<i class="fas fa-folder-open me-2"></i>Select Application to Delete';
      applicationFields.style.display = 'none';
      confirmSaveBtn.textContent = 'Delete';
      confirmSaveBtn.classList.remove('btn-primary');
      confirmSaveBtn.classList.add('btn-danger');
      
      // Show open dialog automatically for delete mode
      showOpenDialog();
    }
  }
  
  // Fetch applications from API
  async function fetchApplications() {
    try {
      const response = await fetch(`/api/documents?mode=${mode}`);
      const data = await response.json();
      
      if (data.success) {
        return data.documents;
      } else {
        showNotification("Error loading applications", "error");
        return [];
      }
    } catch (error) {
      console.error("Error fetching applications:", error);
      showNotification("Error connecting to server", "error");
      return [];
    }
  }
  
  // Load application by ID
  // Function to update word count
  function updateWordCount() {
    const wordCountElement = document.getElementById("wordCount");
    const charCountElement = document.getElementById("charCount");
    
    if (wordCountElement && charCountElement && editor) {
      const text = editor.innerText || "";
      const words = text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
      const chars = text.length;
      
      wordCountElement.textContent = `Words: ${words}`;
      charCountElement.textContent = `Characters: ${chars}`;
    }
  }
  
  async function loadApplication(id) {
    try {
      const response = await fetch(`/api/applications/${id}`);
      const data = await response.json();
      
      if (data.success) {
        const application = data.document;
        
        // Set form fields
        documentName.value = application.title;
        editor.innerHTML = application.content;
        
        // Set application fields if they exist
        applicantName.value = application.applicant_name || '';
        applicantEmail.value = application.email || '';
        fatherName.value = application.father_name || '';
        rollNumber.value = application.roll_number || '';
        className.value = application.class_name || '';
        if (application.date_of_birth) {
          dateOfBirth.value = application.date_of_birth;
        }
        phoneNumber.value = application.phone_number || '';
        address.value = application.address || '';
        
        currentDocumentId = application.id;
        
        updateWordCount();
        showNotification("Application loaded successfully", "success");
      } else {
        showNotification("Error loading application", "error");
      }
    } catch (error) {
      console.error("Error loading application:", error);
      showNotification("Error connecting to server", "error");
    }
  }
  
  // Delete application by ID
  async function deleteApplication(id) {
    try {
      const response = await fetch(`/api/applications/${id}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        showNotification("Application deleted successfully", "success");
        return true;
      } else {
        showNotification("Error deleting application", "error");
        return false;
      }
    } catch (error) {
      console.error("Error deleting application:", error);
      showNotification("Error connecting to server", "error");
      return false;
    }
  }
  
  // Save Document
  async function saveDocument() {
    const title = documentName.value || "Untitled Application";
    const content = editor.innerHTML;
    
    if (mode === 'delete' && currentDocumentId) {
      // Delete the selected document
      const confirmed = confirm("Are you sure you want to delete this application? This action cannot be undone.");
      
      if (confirmed) {
        const success = await deleteApplication(currentDocumentId);
        
        if (success) {
          // Clear form and editor
          documentName.value = "";
          editor.innerHTML = "Type here...";
          currentDocumentId = null;
          
          saveDialog.style.display = "none";
          dialogBackground.style.display = "none";
          
          // Redirect back to dashboard
          setTimeout(() => {
            window.location.href = "/dashboard";
          }, 1500);
        }
      }
      return;
    }
    
    // Prepare data for saving
    const applicationData = {
      mode: mode,
      title: title,
      content: content,
    };
    
    // Add application fields if visible
    if (applicationFields.style.display !== 'none') {
      applicationData.applicant_name = applicantName.value;
      applicationData.email = applicantEmail.value;
      applicationData.father_name = fatherName.value;
      applicationData.roll_number = rollNumber.value;
      applicationData.class_name = className.value;
      applicationData.date_of_birth = dateOfBirth.value;
      applicationData.phone_number = phoneNumber.value;
      applicationData.address = address.value;
    }
    
    // If editing, add document ID
    if (currentDocumentId) {
      applicationData.id = currentDocumentId;
    }
    
    try {
      // Send data to server
      const response = await fetch('/api/documents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(applicationData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Update current document ID with new one if created
        if (data.application_id) {
          currentDocumentId = data.application_id;
        }
        
        saveDialog.style.display = "none";
        dialogBackground.style.display = "none";
        
        showNotification("Application saved successfully", "success");
        
        // If in add mode, redirect to view the application
        if (mode === 'add') {
          setTimeout(() => {
            window.location.href = `/application/${currentDocumentId}`;
          }, 1500);
        }
      } else {
        showNotification(data.message || "Error saving application", "error");
      }
    } catch (error) {
      console.error("Error saving application:", error);
      showNotification("Error connecting to server", "error");
    }
  }
  
  // Show Open Dialog function
  async function showOpenDialog() {
    // Fetch applications from server
    const applications = await fetchApplications();
    
    // Clear the list
    documentList.innerHTML = "";
    
    if (applications.length === 0) {
      // No documents found
      const noDocuments = document.createElement("div");
      noDocuments.className = "p-3 text-center text-muted";
      noDocuments.textContent = "No applications found";
      documentList.appendChild(noDocuments);
    } else {
      // Add applications to the list
      applications.forEach(app => {
        const item = document.createElement("div");
        item.className = "document-item";
        item.innerHTML = `
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${app.title}</strong>
              <div class="small text-muted">${app.date}</div>
            </div>
            <button class="btn btn-sm btn-outline-primary select-document" data-id="${app.id}">
              <i class="fas fa-check"></i> Select
            </button>
          </div>
        `;
        documentList.appendChild(item);
        
        // Add click event to select button
        const selectBtn = item.querySelector('.select-document');
        selectBtn.addEventListener('click', () => {
          selectedDocumentId = app.id;
          
          // Remove active class from all items
          document.querySelectorAll('.document-item').forEach(item => {
            item.classList.remove('active');
          });
          
          // Add active class to selected item
          item.classList.add('active');
          
          if (mode === 'delete') {
            // For delete mode, load the document right away
            loadApplication(selectedDocumentId);
            openDialog.style.display = "none";
            dialogBackground.style.display = "none";
            
            // Show save dialog (which is now a delete confirmation)
            showSaveDialog();
          }
        });
      });
    }
    
    openDialog.style.display = "block";
    dialogBackground.style.display = "block";
  }
  
  // Show Save Dialog function
  function showSaveDialog() {
    // Set the document name from current document ID if available
    if (currentDocumentId && mode === 'edit') {
      // The name should already be set when the document was loaded
    }
    
    saveDialog.style.display = "block";
    dialogBackground.style.display = "block";
    
    // Focus the input
    documentName.focus();
  }
  
  // Add event listeners
  saveBtn.addEventListener("click", showSaveDialog);
  openBtn.addEventListener("click", showOpenDialog);
  
  // Close dialog buttons
  closeSaveDialog.addEventListener("click", () => {
    saveDialog.style.display = "none";
    dialogBackground.style.display = "none";
  });
  
  closeOpenDialog.addEventListener("click", () => {
    openDialog.style.display = "none";
    dialogBackground.style.display = "none";
  });
  
  // Cancel buttons
  cancelSaveBtn.addEventListener("click", () => {
    saveDialog.style.display = "none";
    dialogBackground.style.display = "none";
  });
  
  cancelOpenBtn.addEventListener("click", () => {
    openDialog.style.display = "none";
    dialogBackground.style.display = "none";
  });
  
  // Confirm save/open buttons
  confirmSaveBtn.addEventListener("click", saveDocument);
  
  confirmOpenBtn.addEventListener("click", () => {
    if (selectedDocumentId) {
      loadApplication(selectedDocumentId);
      openDialog.style.display = "none";
      dialogBackground.style.display = "none";
    } else {
      showNotification("Please select an application", "error");
    }
  });
  
  // This function is already defined above
  
  // Function to show notification
  function showNotification(message, type = "default") {
    const notification = document.getElementById("notification");
    const notificationMessage = document.getElementById("notificationMessage");
    
    notification.classList.remove("success", "error");
    
    if (type === "success") {
      notification.classList.add("success");
    } else if (type === "error") {
      notification.classList.add("error");
    }
    
    notificationMessage.textContent = message;
    notification.classList.add("show");
    
    setTimeout(() => {
      notification.classList.remove("show");
    }, 3000);
  }
  
  // Initialize the page based on the mode
  initPageByMode();
});

// Close namespace check
}
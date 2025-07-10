// manage-admins.js

document.addEventListener('DOMContentLoaded', function () {
    // Elements for Add Admin modal
    const addAdminBtn = document.getElementById("add-admin-btn");
    const addAdminModal = document.getElementById("add-admin-modal");
    const closeAddModal = document.getElementById("close-add-modal");
    const cancelAddAdmin = document.getElementById("cancel-add-admin");

    // Elements for Delete Admin modal
    const deleteAdminModal = document.getElementById("delete-admin-modal");
    const closeDeleteModal = document.getElementById("close-delete-modal");
    const cancelDeleteAdmin = document.getElementById("cancel-delete-admin");
    const adminNameToDelete = document.getElementById("admin-name-to-delete");
    const adminIdToDeleteInput = document.getElementById("admin-id-to-delete");

    // ---------------------------
    // Add Admin Modal Logic
    // ---------------------------
    addAdminBtn.addEventListener("click", () => {
        addAdminModal.classList.replace("hidden", "flex");
    });

    if (window.location.hash === "#add-admin") {
    addAdminModal.classList.replace("hidden", "flex");
    }

    [closeAddModal, cancelAddAdmin].forEach(btn => {
        btn.addEventListener("click", () => {
            addAdminModal.classList.replace("flex", "hidden");
        });
    });

    // ---------------------------
    // Delete Admin Modal Logic
    // ---------------------------
    const deleteAdminBtns = document.querySelectorAll(".delete-admin-btn");

    deleteAdminBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const adminName = btn.getAttribute("data-admin-name");
            const adminId = btn.getAttribute("data-admin-id");

            adminNameToDelete.textContent = adminName;
            adminIdToDeleteInput.value = adminId;

            deleteAdminModal.classList.replace("hidden", "flex");
        });
    });

    [closeDeleteModal, cancelDeleteAdmin].forEach(btn => {
        btn.addEventListener("click", () => {
            deleteAdminModal.classList.replace("flex", "hidden");
            adminIdToDeleteInput.value = ""; // Reset
        });
    });

    const deleteForm = document.querySelector('#delete-admin-modal form');
deleteForm.addEventListener('submit', (e) => {
  if (!adminIdToDeleteInput.value) {
    e.preventDefault();
    alert("No admin selected.");
  }
});

    // ---------------------------
    // Close modals when clicking outside the modal content
    // ---------------------------
    [addAdminModal, deleteAdminModal].forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.classList.add("hidden");

                // Reset delete modal input
                if (modal === deleteAdminModal) {
                    adminIdToDeleteInput.value = "";
                }
            }
        });
    });
});

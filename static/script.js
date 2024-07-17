window.addEventListener("load", function () {
  // open add gallery modal
  this.document
    .getElementById("add-gallery")
    .addEventListener("click", function () {
      document.getElementById("add-gallery-modal").hidden = false;
    });

  // close add gallery modal
  this.document
    .getElementById("close-add-gallery-modal")
    .addEventListener("click", function () {
      document.getElementById("add-gallery-modal").hidden = true;
    });

  // close share gallery modal
  this.document
    .getElementById("close-share-gallery-modal")
    .addEventListener("click", function () {
      document.getElementById("share-gallery-modal").hidden = true;
    });

  // close update gallery modal
  this.document
    .getElementById("close-update-gallery-modal")
    .addEventListener("click", function () {
      document.getElementById("update-gallery-modal").hidden = true;
    });

  // close delete gallery modal
  this.document
    .getElementById("close-delete-gallery-modal")
    .addEventListener("click", function () {
      document.getElementById("delete-gallery-modal").hidden = true;
    });
});

// Gallery actions
function openShareGalleryModal(index) {
  document.getElementById("share-gallery-modal").hidden = false;

  // add gallery index value to the form
  document.getElementById("share_gallery_index").value = index;
}

function openUpdateGalleryModal(index) {
  document.getElementById("update-gallery-modal").hidden = false;
  document.getElementById("update_gallery_index").value = index;
}

function openDeleteGalleryModal(index) {
  document.getElementById("delete-gallery-modal").hidden = false;
  document.getElementById("delete_gallery_index").value = index;
}

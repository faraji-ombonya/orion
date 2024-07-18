window.addEventListener("load", function () {
  // open add image
  this.document
    .getElementById("add-image-button")
    .addEventListener("click", function () {
      console.log("Add image button clicked");
      document.getElementById("add-image-modal").hidden = false;
    });

  // close add image modal
  this.document
    .getElementById("close-add-image-modal")
    .addEventListener("click", function () {
      document.getElementById("add-image-modal").hidden = true;
    });
});

// // Gallery actions
// function openShareGalleryModal(index) {
//   document.getElementById("share-gallery-modal").hidden = false;

//   // add gallery index value to the form
//   document.getElementById("share_gallery_index").value = index;
// }

// function openUpdateGalleryModal(index) {
//   document.getElementById("update-gallery-modal").hidden = false;
//   document.getElementById("update_gallery_index").value = index;
// }

// function openDeleteGalleryModal(index) {
//   document.getElementById("delete-gallery-modal").hidden = false;
//   document.getElementById("delete_gallery_index").value = index;
// }

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
});

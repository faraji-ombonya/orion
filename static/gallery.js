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

function handleMouseEnter(index) {
  document.getElementById(`image-${index}`).hidden = false;
}

function handleMouseLeave(index) {
  document.getElementById(`image-${index}`).hidden = true;
}

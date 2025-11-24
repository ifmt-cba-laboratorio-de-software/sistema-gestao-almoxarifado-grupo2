(function () {
  const swalToast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 2500,
    timerProgressBar: true,
  });

  const flashContainer = document.getElementById("flash-messages");
  if (flashContainer) {
    const flashMessages = flashContainer.querySelectorAll(".flash-message");
    flashMessages.forEach((msg) => {
      const level = msg.dataset.level || "info";
      const text = msg.dataset.text || "";
      const icon = level.includes("error") || level === "danger" ? "error" : level === "success" ? "success" : "info";
      swalToast.fire({ icon, title: text });
    });
  }

  const deleteButtons = document.querySelectorAll(".confirm-delete");
  deleteButtons.forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.preventDefault();
      const form = btn.closest("form");
      const name = btn.dataset.name || "este item";
      Swal.fire({
        title: "Deseja excluir?",
        text: `Confirmar exclusao de "${name}"?`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "Sim, excluir",
        cancelButtonText: "Cancelar",
      }).then((result) => {
        if (result.isConfirmed && form) {
          form.submit();
        }
      });
    });
  });

  const toggleButton = document.getElementById("sidebar-toggle");
  if (toggleButton) {
    toggleButton.addEventListener("click", () => {
      document.body.classList.toggle("sidebar-collapsed");
    });
  }
})();

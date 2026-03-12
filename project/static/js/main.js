async function postJson(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw data || { error: "Request failed" };
  }
  return data;
}

function getApiBase() {
  if (window.NGO_PLATFORM_CONFIG && window.NGO_PLATFORM_CONFIG.apiBase) {
    return window.NGO_PLATFORM_CONFIG.apiBase;
  }
  return "";
}

document.addEventListener("DOMContentLoaded", () => {
  const apiBase = getApiBase();

  // Add animal (JSON)
  const addAnimalForm = document.getElementById("add-animal-form");
  if (addAnimalForm) {
    addAnimalForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const statusSpan = document.getElementById("add-animal-status");
      statusSpan.textContent = "Saving...";

      const payload = {
        species: document.getElementById("species").value || null,
        breed: document.getElementById("breed").value || null,
        rescue_date: document.getElementById("rescue_date").value || null,
        shelter_location:
          document.getElementById("shelter_location").value || null,
        health_status: document.getElementById("health_status").value || null,
      };

      try {
        await postJson(`${apiBase}/api/animals`, payload);
        statusSpan.textContent = "Animal added.";
        addAnimalForm.reset();
      } catch (err) {
        statusSpan.textContent =
          (err && err.error) || "Failed to add animal record.";
      }
    });
  }

  // Upload & recognize image
  const uploadForm = document.getElementById("upload-form");
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const statusSpan = document.getElementById("upload-status");
      statusSpan.textContent = "Uploading...";
      const fileInput = document.getElementById("image");
      if (!fileInput.files.length) {
        statusSpan.textContent = "Please choose an image first.";
        return;
      }

      const formData = new FormData();
      formData.append("image", fileInput.files[0]);

      try {
        const res = await fetch(`${apiBase}/api/animals/upload`, {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (!res.ok) {
          statusSpan.textContent = data.error || "Upload failed.";
          return;
        }

        statusSpan.textContent =
          data.status === "existing"
            ? `Matched existing animal: ${data.animal.animal_id}`
            : `Created new animal: ${data.animal.animal_id}`;
      } catch (err) {
        statusSpan.textContent = "Error uploading image.";
      }
    });
  }

  // Search animals
  const searchBtn = document.getElementById("search-btn");
  if (searchBtn) {
    searchBtn.addEventListener("click", async () => {
      const species = document.getElementById("search_species").value;
      const breed = document.getElementById("search_breed").value;
      const shelter = document.getElementById("search_shelter").value;
      const params = new URLSearchParams();
      if (species) params.append("species", species);
      if (breed) params.append("breed", breed);
      if (shelter) params.append("shelter_location", shelter);

      const url = `${apiBase}/api/animals?${params.toString()}`;
      try {
        const res = await fetch(url);
        const data = await res.json();
        const tbody = document.getElementById("animals-table-body");
        tbody.innerHTML = "";
        data.forEach((animal) => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${animal.animal_id}</td>
            <td>${animal.species || "Unknown"}</td>
            <td>${animal.breed || "Unknown"}</td>
            <td>${animal.shelter_location || "Unknown"}</td>
            <td>${animal.health_status || "Unknown"}</td>
            <td>${animal.adoption_status}</td>
            <td><a class="btn small" href="/animal/${animal.id}">View</a></td>
          `;
          tbody.appendChild(row);
        });
      } catch (err) {
        // In a simple starter app, fail silently in UI.
        // You can add toast notifications or console logs if needed.
      }
    });
  }

  // Adoption request
  const adoptionForm = document.getElementById("adoption-form");
  if (adoptionForm) {
    adoptionForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const statusSpan = document.getElementById("adopt-status");
      statusSpan.textContent = "Sending request...";

      const payload = {
        animal_id: Number(
          document.getElementById("adopt_animal_id").value || 0
        ),
        name: document.getElementById("adopt_name").value,
        email: document.getElementById("adopt_email").value,
        phone: document.getElementById("adopt_phone").value,
        address: document.getElementById("adopt_address").value,
        message: document.getElementById("adopt_message").value,
      };

      try {
        await postJson(`${apiBase}/api/adoption_requests`, payload);
        statusSpan.textContent = "Request sent. Thank you!";
        adoptionForm.reset();
      } catch (err) {
        statusSpan.textContent =
          (err && err.error) || "Failed to send adoption request.";
      }
    });
  }

  // Donation
  const donationForm = document.getElementById("donation-form");
  if (donationForm) {
    donationForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const statusSpan = document.getElementById("donation-status");
      statusSpan.textContent = "Recording donation...";

      const payload = {
        donor_name: document.getElementById("donor_name").value,
        donor_email: document.getElementById("donor_email").value,
        amount: Number(
          document.getElementById("donation_amount").value || 0
        ),
        message: document.getElementById("donation_message").value,
      };

      try {
        await postJson(`${apiBase}/api/donations`, payload);
        statusSpan.textContent =
          "Donation recorded (no real payment processed). Thank you!";
        donationForm.reset();
      } catch (err) {
        statusSpan.textContent =
          (err && err.error) || "Failed to record donation.";
      }
    });
  }
});


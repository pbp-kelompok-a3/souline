const container = document.getElementById("video-container");
const addBtn = document.getElementById("add-btn");

async function loadResources() {
  const res = await fetch("/resources/api/");
  const data = await res.json();
  container.innerHTML = "";
  data.forEach((r) => {
    container.innerHTML += `
      <div class="w-72 flex-shrink-0 bg-white shadow rounded-xl p-3 relative">
        <span class="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded">${r.level}</span>
        <iframe class="w-full h-40 rounded-lg mb-2" src="${r.youtube_link}" allowfullscreen></iframe>
        <h3 class="font-semibold text-gray-800">${r.title}</h3>
        <p class="text-sm text-gray-600 line-clamp-2">${r.description}</p>
        <div class="flex justify-between mt-2">
          <button onclick="editResource(${r.id})" class="text-yellow-600 text-sm">Edit</button>
          <button onclick="deleteResource(${r.id})" class="text-red-600 text-sm">Delete</button>
        </div>
      </div>`;
  });
}

async function addResource() {
  const data = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value,
    youtube_link: document.getElementById("youtube_link").value,
    level: document.getElementById("level").value,
  };
  await fetch("/resources/api/add/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  loadResources();
}

async function deleteResource(id) {
  await fetch(`/resources/api/delete/${id}/`, { method: "DELETE" });
  loadResources();
}

async function editResource(id) {
  const title = prompt("Judul baru:");
  const desc = prompt("Deskripsi baru:");
  const link = prompt("Link YouTube baru:");
  const level = prompt("Level (beginner/intermediate/advanced):");

  if (!title) return;
  await fetch(`/resources/api/edit/${id}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: title,
      description: desc,
      youtube_link: link,
      level: level,
    }),
  });
  loadResources();
}

addBtn.addEventListener("click", addResource);
loadResources();

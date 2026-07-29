// Marca o link do menu que corresponde à página atual, para o usuário
// saber sempre onde está dentro do site (o CSS cuida da aparência via .ativo).
document.addEventListener("DOMContentLoaded", () => {
	const paginaAtual = window.location.pathname.split("/").pop();
	document.querySelectorAll("#menu a[href]").forEach((link) => {
		const destino = link.getAttribute("href").split("/").pop();
		if (destino === paginaAtual) {
			link.classList.add("ativo");
		}
	});
});

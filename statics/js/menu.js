document.addEventListener("DOMContentLoaded", () => {
	// Pega só o nome do arquivo da URL atual (ex.: "index.html"), ignorando
	// o resto do caminho (pastas) e parâmetros.
	const paginaAtual = window.location.pathname.split("/").pop();

	// Passa por todos os links dentro do <nav id="menu">...
	document.querySelectorAll("#menu a[href]").forEach((link) => {
		// ...e compara o nome do arquivo de cada link com o da página atual.
		const destino = link.getAttribute("href").split("/").pop();
		if (destino === paginaAtual) {
			link.classList.add("ativo");
		}
	});
});

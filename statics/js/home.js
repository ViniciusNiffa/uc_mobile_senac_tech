// Comportamento específico da home: rolagem suave ao clicar na seta "voltar ao topo".
document.addEventListener("DOMContentLoaded", () => {
	const setaTopo = document.querySelector('a[href="#s1"]');
	if (!setaTopo) return;

	setaTopo.addEventListener("click", (evento) => {
		evento.preventDefault();
		window.scrollTo({ top: 0, behavior: "smooth" });
	});
});

// Comportamento exclusivo da home (index.html): quando o usuário clica na seta
// "voltar ao topo" no rodapé, rola a página suavemente até o início em vez de
// pular direto (o que aconteceria só com o link <a href="#s1">).
document.addEventListener("DOMContentLoaded", () => {
	const setaTopo = document.querySelector('a[href="#s1"]');
	if (!setaTopo) return;

	setaTopo.addEventListener("click", (evento) => {
		evento.preventDefault(); // evita o salto instantâneo do link âncora
		window.scrollTo({ top: 0, behavior: "smooth" });
	});
});

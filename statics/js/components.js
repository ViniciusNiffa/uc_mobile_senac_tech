// Funções compartilhadas pelas páginas de usuário (login, cadastro, recuperação de senha...).
// Depende de APP_CONFIG (statics/js/config.js), que deve ser carregado antes deste arquivo.

async function postJSON(caminho, corpo) {
	const resposta = await fetch(APP_CONFIG.API_BASE_URL + caminho, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(corpo)
	});
	const dados = await resposta.json().catch(() => ({}));
	return { ok: resposta.ok, status: resposta.status, dados };
}

function mostrarMensagem(elemento, texto, tipo) {
	if (!elemento) return;
	elemento.textContent = texto;
	elemento.classList.remove("mensagem--erro", "mensagem--sucesso");
	elemento.classList.add(tipo === "erro" ? "mensagem--erro" : "mensagem--sucesso");
}

document.addEventListener("DOMContentLoaded", () => {
	ligarFormularioLogin();
	ligarFormularioRecuperarSenha();
	ligarFormularioResetarSenha();
	ligarFormularioVerificarEmail();
	ligarFormularioPerfil();
});

function ligarFormularioLogin() {
	const form = document.getElementById("form-login");
	if (!form) return;
	const mensagem = document.getElementById("mensagem-login");

	form.addEventListener("submit", async (evento) => {
		evento.preventDefault();
		const email = document.getElementById("email").value.trim();
		const senha = document.getElementById("senha").value;

		const { status, dados } = await postJSON("/login", { email, senha });

		if (status === 200 && dados.success) {
			localStorage.setItem("access_token", dados.access_token);
			localStorage.setItem("refresh_token", dados.refresh_token);
			mostrarMensagem(mensagem, "Login realizado! Redirecionando...", "sucesso");
			window.location.href = "perfil.html";
			return;
		}

		if (status === 403 && dados.pendente) {
			sessionStorage.setItem("usuario_id_pendente", dados.usuario_id);
			window.location.href = "verificar-email.html";
			return;
		}

		mostrarMensagem(mensagem, dados.message || "Não foi possível entrar.", "erro");
	});
}

function ligarFormularioRecuperarSenha() {
	const form = document.getElementById("form-recuperar-senha");
	if (!form) return;
	const mensagem = document.getElementById("mensagem-recuperar");

	form.addEventListener("submit", async (evento) => {
		evento.preventDefault();
		const email = document.getElementById("email").value.trim();
		sessionStorage.setItem("email_recuperacao", email);

		const { dados } = await postJSON("/forgot-password", { email });
		mostrarMensagem(mensagem, dados.message || "Se o e-mail existir, enviamos um código.", "sucesso");
	});
}

function ligarFormularioResetarSenha() {
	const form = document.getElementById("form-resetar-senha");
	if (!form) return;
	const mensagem = document.getElementById("mensagem-resetar");

	const emailSalvo = sessionStorage.getItem("email_recuperacao");
	if (emailSalvo) document.getElementById("email").value = emailSalvo;

	form.addEventListener("submit", async (evento) => {
		evento.preventDefault();
		const email = document.getElementById("email").value.trim();
		const codigo = document.getElementById("codigo").value.trim();
		const senha = document.getElementById("senha").value;

		const { status, dados } = await postJSON("/reset-password", { email, codigo, senha });

		if (status === 200 && dados.success) {
			sessionStorage.removeItem("email_recuperacao");
			window.location.href = "sucesso.html";
			return;
		}
		mostrarMensagem(mensagem, dados.message || "Não foi possível redefinir a senha.", "erro");
	});
}

function ligarFormularioVerificarEmail() {
	const form = document.getElementById("form-verificar-email");
	if (!form) return;
	const mensagem = document.getElementById("mensagem-verificar");
	const usuarioId = sessionStorage.getItem("usuario_id_pendente");

	form.addEventListener("submit", async (evento) => {
		evento.preventDefault();
		const codigo = document.getElementById("codigo").value.trim();

		const { status, dados } = await postJSON("/verify-email", { usuario_id: usuarioId, codigo });

		if (status === 200 && dados.success) {
			sessionStorage.removeItem("usuario_id_pendente");
			window.location.href = "sucesso.html";
			return;
		}
		mostrarMensagem(mensagem, dados.message || "Código incorreto.", "erro");
	});

	const linkReenviar = document.getElementById("reenviar-codigo");
	if (linkReenviar) {
		linkReenviar.addEventListener("click", async (evento) => {
			evento.preventDefault();
			const { dados } = await postJSON("/resend-otp", { usuario_id: usuarioId });
			mostrarMensagem(mensagem, dados.message || "Código reenviado.", "sucesso");
		});
	}
}

function ligarFormularioPerfil() {
	const form = document.getElementById("form-perfil");
	if (!form) return;

	if (!localStorage.getItem("access_token")) {
		window.location.href = "login.html";
	}
}

// statics/js/mascaras.js
// Máscaras de input sem dependências externas.

function aplicarMascara(input, fn) {
    input.addEventListener('input', () => {
        const pos = input.selectionStart;
        const antes = input.value;
        input.value = fn(antes);
        // Reposiciona o cursor após formatação
        const diff = input.value.length - antes.length;
        input.setSelectionRange(pos + diff, pos + diff);
    });
}

function mascCEP(v) {
    v = v.replace(/\D/g, '').slice(0, 8);
    return v.length > 5 ? v.replace(/^(\d{5})(\d)/, '$1-$2') : v;
}

function mascCPF(v) {
    v = v.replace(/\D/g, '').slice(0, 11);
    if (v.length > 9) return v.replace(/^(\d{3})(\d{3})(\d{3})(\d)/, '$1.$2.$3-$4');
    if (v.length > 6) return v.replace(/^(\d{3})(\d{3})(\d)/, '$1.$2.$3');
    if (v.length > 3) return v.replace(/^(\d{3})(\d)/, '$1.$2');
    return v;
}

function mascRG(v) {
    // Formato RS: 0.000.000 — aceita até 9 dígitos com pontos e traço final opcional
    v = v.replace(/\D/g, '').slice(0, 9);
    if (v.length > 7) return v.replace(/^(\d{1,2})(\d{3})(\d{3})(\d{0,1})/, (_, a, b, c, d) => d ? `${a}.${b}.${c}-${d}` : `${a}.${b}.${c}`);
    if (v.length > 4) return v.replace(/^(\d{1,2})(\d{3})(\d)/, '$1.$2.$3');
    if (v.length > 2) return v.replace(/^(\d{1,2})(\d)/, '$1.$2');
    return v;
}

function mascNumero(v) {
    return v.replace(/\D/g, '').slice(0, 5);
}

function mascCelular(v) {
    v = v.replace(/\D/g, '').slice(0, 11);
    if (v.length === 11) return v.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
    if (v.length > 6)   return v.replace(/^(\d{2})(\d{4,5})(\d*)/, '($1) $2-$3');
    if (v.length > 2)   return v.replace(/^(\d{2})(\d*)/, '($1) $2');
    if (v.length > 0)   return v.replace(/^(\d*)/, '($1');
    return v;
}

document.addEventListener('DOMContentLoaded', () => {
    const campos = {
        cep:     mascCEP,
        cpf:     mascCPF,
        rg:      mascRG,
        celular: mascCelular,
        numero:  mascNumero,
    };

    for (const [id, fn] of Object.entries(campos)) {
        const el = document.getElementById(id);
        if (el) aplicarMascara(el, fn);
    }

    // Auto-preenche endereço ao sair do CEP
    const cepInput = document.getElementById('cep');
    if (cepInput) {
        cepInput.addEventListener('blur', async () => {
            const cep = cepInput.value.replace(/\D/g, '');
            if (cep.length !== 8) return;
            try {
                const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                const dados = await res.json();
                if (dados.erro) return;
                const set = (id, val) => { const el = document.getElementById(id); if (el && val) el.value = val; };
                set('rua',    dados.logradouro);
                set('bairro', dados.bairro);
                set('cidade', dados.localidade);
                // Seleciona o estado no <select>
                const sel = document.getElementById('estado');
                if (sel && dados.uf) {
                    for (const opt of sel.options) {
                        if (opt.value === dados.uf) { opt.selected = true; break; }
                    }
                }
            } catch (_) { /* ViaCEP offline — ignora */ }
        });
    }
});

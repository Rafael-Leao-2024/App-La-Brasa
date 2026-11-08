// 1. Inicializa o carrinho no localStorage se não existir
let carrinho = JSON.parse(localStorage.getItem('carrinhoLaBrasa')) || [];

// 2. Função que atualiza a bolinha laranja do carrinho
function atualizarContador() {
    const count = carrinho.reduce((total, item) => total + item.quantidade, 0);
    const badge = document.getElementById('cart-count');
    if (badge) badge.innerText = count;
}

// 3. Variáveis do Modal
let itemTemporario = null;
let extrasSelecionados = [];

// 4. Abre o Modal
// 4. Abre o Modal
function abrirModalAdd(id, nome, preco, descricao, foto, permiteExtra) {
    itemTemporario = { id, nome, preco };
    extrasSelecionados = [];

    document.getElementById('modalNome').innerText = nome;
    document.getElementById('modalDescricao').innerText = descricao || 'Delicioso lanche artesanal.';
    document.getElementById('modalObservacao').value = '';
    
    const imgEl = document.getElementById('modalFoto');
    if (foto) {
        imgEl.src = `/static/uploads/${foto}`;
        imgEl.classList.remove('d-none');
    } else {
        imgEl.classList.add('d-none');
    }

    // Lógica de Extras
    const areaExtras = document.getElementById('area-extras');
    const listaExtras = document.getElementById('lista-extras');
    
    const extrasDisponiveis = typeof TODOS_OS_EXTRAS !== 'undefined' ? TODOS_OS_EXTRAS : [];

    if (permiteExtra && extrasDisponiveis.length > 0) {
        areaExtras.classList.remove('d-none');
        listaExtras.innerHTML = '';
        
        extrasDisponiveis.forEach(extra => {
            // 🚨 NOVO VISUAL DO EXTRA AQUI
            const fotoHtml = extra.foto 
                ? `<img src="/static/uploads/${extra.foto}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 6px;" class="ms-3 border border-secondary">`
                : `<div class="ms-3 bg-secondary rounded d-flex align-items-center justify-content-center border border-secondary" style="width: 45px; height: 45px;">🍟</div>`;

            listaExtras.innerHTML += `
                <label class="card-extra d-flex justify-content-between align-items-center p-2 mb-2 rounded" for="extra_${extra.id}" style="cursor: pointer; background-color: rgba(255,255,255,0.05); border: 1px solid #444;">
                    
                    <!-- Esquerda: Checkbox e Nome -->
                    <div class="d-flex align-items-center flex-grow-1">
                        <input class="form-check-input extra-checkbox m-0 me-3" type="checkbox" value="${extra.id}" id="extra_${extra.id}" data-nome="${extra.nome}" data-preco="${extra.preco}" onchange="atualizarPrecoModal()">
                        <div class="d-flex flex-column">
                            <span class="text-white fw-bold">${extra.nome}</span>
                            <span class="text-orange small">+ R$ ${extra.preco.toFixed(2)}</span>
                        </div>
                    </div>

                    <!-- Direita: Foto do Extra -->
                    ${fotoHtml}
                </label>
            `;
        });
    } else {
        areaExtras.classList.add('d-none');
    }

    document.getElementById('btnConfirmarAdd').innerText = `Adicionar - R$ ${preco.toFixed(2)}`;
    const modal = new bootstrap.Modal(document.getElementById('modalAdicionar'));
    modal.show();
}

// 5. Calcula o valor no modal (Lanche + Extras)
function atualizarPrecoModal() {
    let precoTotal = itemTemporario.preco;
    
    extrasSelecionados = [];
    document.querySelectorAll('.extra-checkbox:checked').forEach(cb => {
        precoTotal += parseFloat(cb.dataset.preco);
        extrasSelecionados.push({ 
            id: parseInt(cb.value), 
            nome: cb.dataset.nome, 
            preco: parseFloat(cb.dataset.preco) 
        });
    });

    // Atualiza o botão de confirmar com o novo preço
    const btnConfirmar = document.getElementById('btnConfirmarAdd');
    btnConfirmar.innerText = `Adicionar - R$ ${precoTotal.toFixed(2)}`;
}

// 6. Evento do botão Confirmar (Adicionar ao Carrinho)
document.getElementById('btnConfirmarAdd').addEventListener('click', function() {
    if (!itemTemporario) return;

    const obs = document.getElementById('modalObservacao').value;
    
    // Cria o item com os extras anexados
    const novoItem = {
        id: itemTemporario.id,
        nome: itemTemporario.nome,
        preco_base: itemTemporario.preco,
        extras: extrasSelecionados,
        preco: itemTemporario.preco + extrasSelecionados.reduce((acc, curr) => acc + curr.preco, 0),
        quantidade: 1,
        observacao: obs
    };
    
    // Verifica se o item exato (com os mesmos extras e obs) já está no carrinho
    const itemIndex = carrinho.findIndex(i => 
        i.id === novoItem.id && 
        i.observacao === novoItem.observacao && 
        JSON.stringify(i.extras) === JSON.stringify(novoItem.extras)
    );
    
    if (itemIndex > -1) {
        carrinho[itemIndex].quantidade += 1;
    } else {
        carrinho.push(novoItem);
    }
    
    localStorage.setItem('carrinhoLaBrasa', JSON.stringify(carrinho));
    atualizarContador();
    
    // Fecha o modal e reseta
    const modalEl = document.getElementById('modalAdicionar');
    const modal = bootstrap.Modal.getInstance(modalEl);
    modal.hide();
});

// 7. Atualiza o contador ao carregar a página
document.addEventListener('DOMContentLoaded', atualizarContador);
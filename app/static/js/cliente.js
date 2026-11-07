// Inicializa o carrinho no localStorage se não existir
let carrinho = JSON.parse(localStorage.getItem('carrinhoLaBrasa')) || [];

function atualizarContador() {
    const count = carrinho.reduce((total, item) => total + item.quantidade, 0);
    const badge = document.getElementById('cart-count');
    if (badge) badge.innerText = count;
}

// Variáveis para guardar o item que está sendo adicionado no Modal
let itemTemporario = null;

function abrirModalAdd(id, nome, preco, descricao, foto) {
    // Guarda os dados do produto
    itemTemporario = { id, nome, preco };

    // Preenche o Modal
    document.getElementById('modalNome').innerText = nome;
    document.getElementById('modalDescricao').innerText = descricao || 'Delicioso lanche artesanal.';
    document.getElementById('modalObservacao').value = ''; // Limpa campo anterior
    
    const imgEl = document.getElementById('modalFoto');
    if (foto) {
        imgEl.src = `/static/uploads/${foto}`;
        imgEl.classList.remove('d-none');
    } else {
        imgEl.classList.add('d-none');
    }

    // Abre o modal do Bootstrap
    const modal = new bootstrap.Modal(document.getElementById('modalAdicionar'));
    modal.show();
}

// Evento do botão "Adicionar ao Carrinho" dentro do Modal
document.getElementById('btnConfirmarAdd').addEventListener('click', function() {
    if (!itemTemporario) return;

    const obs = document.getElementById('modalObservacao').value;
    
    // Verifica se o item com a mesma observação já está no carrinho
    const itemIndex = carrinho.findIndex(i => i.id === itemTemporario.id && i.observacao === obs);
    
    if (itemIndex > -1) {
        carrinho[itemIndex].quantidade += 1;
    } else {
        carrinho.push({ 
            id: itemTemporario.id, 
            nome: itemTemporario.nome, 
            preco: itemTemporario.preco, 
            quantidade: 1, 
            observacao: obs 
        });
    }
    
    localStorage.setItem('carrinhoLaBrasa', JSON.stringify(carrinho));
    atualizarContador();
    
    // Fecha o modal
    const modalEl = document.getElementById('modalAdicionar');
    const modal = bootstrap.Modal.getInstance(modalEl);
    modal.hide();

    // Efeito visual de sucesso (opcional)
    const badge = document.getElementById('cart-count');
    badge.classList.add('bg-success', 'text-white');
    setTimeout(() => badge.classList.remove('bg-success', 'text-white'), 500);
});

// Atualiza ao carregar a página
document.addEventListener('DOMContentLoaded', atualizarContador);
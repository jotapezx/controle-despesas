// Scripts JavaScript adicionais podem ser colocados aqui
document.addEventListener('DOMContentLoaded', function() {
    // Exemplo: Formatação automática de valores monetários
    const valorInputs = document.querySelectorAll('input[type="number"]');
    valorInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
});
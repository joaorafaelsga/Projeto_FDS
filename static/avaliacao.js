const campoPendente = document.querySelector(".avaliacao .campo-com-erro");

if (campoPendente) {
    campoPendente.scrollIntoView({ block: "center" });
    const entrada = campoPendente.querySelector("input, select");
    if (entrada) {
        entrada.focus({ preventScroll: true });
    }
}

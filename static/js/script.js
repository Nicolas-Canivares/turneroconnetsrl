document.addEventListener("DOMContentLoaded", () => {
    const btnSacarTurno = document.getElementById("btnSacarTurno");
    const ultimoTurno = document.getElementById("ultimoTurno");
    const cajasContainer = document.getElementById("cajasContainer");
    const estadoSistema = document.getElementById("estadoSistema");

    // Inicializar el sistema
    cargarEstado();
    inicializarCajas(30); // Por defecto, cuatro cajas

    const serverBaseUrl = "http://192.168.1.10:5000"; // Cambia esto según tu red

    fetch(`${serverBaseUrl}/sacar_turno`, { method: "POST" })
        .then(response => response.json())
        .then(data => {
            ultimoTurno.textContent = `Próximo turno: ${data.turno_generado}`;
        });


    btnSacarTurno.addEventListener("click", () => {
        fetch("/sacar_turno", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                ultimoTurno.textContent = `Próximo turno: ${data.turno_generado}`;
                cargarEstado();
            });
    });

    function inicializarCajas(numeroDeCajas) {
        cajasContainer.innerHTML = "";
        for (let i = 1; i <= numeroDeCajas; i++) {
            const cajaDiv = document.createElement("div");
            cajaDiv.className = "caja";
            cajaDiv.innerHTML = `
                <h3>Caja ${i}</h3>
                <p class="turno">-</p>
                <button onclick="atenderTurno(${i})">Atender Turno</button>
                <button onclick="liberarCaja(${i})">Liberar Caja</button>
            `;
            cajasContainer.appendChild(cajaDiv);
        }
    }

    window.atenderTurno = (caja) => {
        fetch("/atender_turno", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ caja })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    const turno = document.querySelector(`.caja:nth-child(${caja}) .turno`);
                    turno.textContent = data.turno;
                    cargarEstado();
                }
            });
    };

    window.liberarCaja = (caja) => {
        fetch("/liberar_caja", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ caja })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    const turno = document.querySelector(`.caja:nth-child(${caja}) .turno`);
                    turno.textContent = "-";
                    cargarEstado();
                }
            });
    };

    function cargarEstado() {
        fetch("/estado")
            .then(response => response.json())
            .then(data => {
                estadoSistema.textContent = JSON.stringify(data, null, 2);
            });
    }
});

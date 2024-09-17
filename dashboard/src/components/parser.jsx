// Función para obtener los datos del servidor usando una petición GET
async function fetchData() {
    try {
        // Petición GET al servidor que devuelve el JSON
        const response = await fetch('https://api.ejemplo.com/getDatos'); // URL de ejemplo, reemplázala con la tuya
        const data = await response.json();

        // Procesar los datos del JSON
        processTemperatureData(data.Temperatura);
        processACData(data.AC);
        processAlarmData(data.Alarma);
        processAccessData(data.Acceso);
        processHistoryData(data.Historial);
    } catch (error) {
        console.error('Error al obtener los datos:', error);
    }
}

// Funciones para procesar cada parte del JSON

// Procesar datos de temperatura
function processTemperatureData(temperatura) {
    console.log("Datos de Temperatura:");
    temperatura.forEach(item => {
        console.log(`Fecha: ${item.fecha}, Hora: ${item.hora}, Temperatura: ${item.temperatura}`);
    });
}

// Procesar datos de AC
function processACData(ac) {
    console.log("Datos de Aire Acondicionado:");
    ac.forEach(item => {
        const estado = item.true === "true" ? "Encendido" : "Apagado";
        console.log(`Fecha: ${item.fecha}, Hora: ${item.hora}, Estado: ${estado}`);
    });
}

// Procesar datos de Alarma
function processAlarmData(alarma) {
    console.log("Datos de Alarma:");
    alarma.forEach(item => {
        const estado = item.true === "true" ? "Activada" : "Desactivada";
        console.log(`Fecha: ${item.fecha}, Hora: ${item.hora}, Estado: ${estado}`);
    });
}

// Procesar datos de Acceso
function processAccessData(acceso) {
    console.log("Datos de Acceso:");
    acceso.forEach(item => {
        const accesoPermitido = item.true === "true" ? "Permitido" : "Denegado";
        console.log(`Fecha: ${item.fecha}, Hora: ${item.hora}, Acceso: ${accesoPermitido}`);
    });
}

// Procesar datos de Historial
function processHistoryData(historial) {
    console.log("Historial de Acciones:");
    historial.forEach(item => {
        console.log(`Fecha: ${item.fecha}, Hora: ${item.hora}, Acción: ${item.Accion}`);
    });
}

// Llamar a la función para obtener los datos
fetchData();

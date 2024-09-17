import { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types'; 
import { Line, Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend);

const Dashboard = ({ isAuthorized }) => {  // Recibe isAuthorized como prop
    const navigate = useNavigate();

  const [temperatureData, setTemperatureData] = useState(null);
  const [airConditioningData, setAirConditioningData] = useState(null);
  const [fireAlarmData, setFireAlarmData] = useState(null);
  const [accessLogData, setAccessLogData] = useState([]);
  const [invernaderoData, setInvernaderoData] = useState(null);
  const [alarmEnabled, setAlarmEnabled] = useState(false);
  const [manualChangeRociadores, setManualChangeRociadores] = useState(false);
  const [rociadoresEnabled, setRociadoresEnabled] = useState(false);
  const [lucesEnabled, setLucesEnabled] = useState(false);
  const [loading, setLoading] = useState(true);
  const [alarmDisabled, setAlarmDisabled] = useState(false); // Deshabilitar la alarma después de apagar
  const [message, setMessage] = useState(''); // Estado para el campo de texto
  const [shownMessage, setShownMessage] = useState(''); // Estado para mostrar el mensaje
  
  const handleShowMessage = async () => {
    try {
      const response = await fetch('http://192.168.0.21:5000/mensajes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mensaje: message }), // Envia el mensaje en formato JSON
      });
  
      if (response.ok) {
        alert('Mensaje enviado correctamente');
        setShownMessage(message);  // Mostrar el mensaje después de enviarlo
      } else {
        alert('Error al enviar el mensaje');
      }
    } catch (error) {
      console.error('Error al enviar el mensaje:', error);
      alert('Hubo un error al intentar enviar el mensaje');
    }
  };
  

  const fetchData = useCallback(async () => {
    try {
      const response = await fetch('http://192.168.0.21:5000/graficas');
      const data = await response.json();
      processTemperatureData(data.temperatura);
      processACData(data.ac);
      processAlarmData(data.alarma);
      processAccessData(data.ingreso);
      processInvernaderoData(data.invernadero);
      setLoading(false);
    } catch (error) {
      console.error('Error al obtener los datos:', error);
      setLoading(false);
    }
  }, []);

  const postStatus = async (url, estado) => {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ estado }),  // Enviar el estado como 'encendido' o 'apagado'
      });
  
      console.log('Enviando a URL:', url, 'Estado:', estado); // Verificar lo que se envía
      if (!response.ok) {
        throw new Error(`Error en la solicitud POST a ${url}`);
      }
  
      const data = await response.json();
      console.log('Respuesta de la API:', data); // Verificar lo que devuelve la API
      return data;
    } catch (error) {
      console.error('Error al enviar el estado:', error);
      return null;
    }
  };
  const fetchSensoresStatus = async () => {
    try {
        const response = await fetch('http://192.168.0.21:5000/sensores');
        const data = await response.json();

        // Verificar lo que devuelve la API
        console.log('Estado de los sensores:', data);
        
        return data;
    } catch (error) {
        console.error('Error al obtener el estado de los sensores:', error);
        return null;
    }
};
useEffect(() => {
    const interval = setInterval(async () => {
      if (!manualChangeRociadores) {
        const sensoresStatus = await fetchSensoresStatus();
      
        if (sensoresStatus) {
          // Solo actualiza si el estado ha cambiado y no hubo un cambio manual reciente
          if (sensoresStatus.alarma !== (alarmEnabled ? 'on' : 'off')) {
            setAlarmEnabled(sensoresStatus.alarma === 'on');
          }
          if (sensoresStatus.rociadores !== (rociadoresEnabled ? 'on' : 'off')) {
              setRociadoresEnabled(sensoresStatus.rociadores === 'on');
          }
          if (sensoresStatus.luces !== (lucesEnabled ? 'on' : 'off')) {
            setLucesEnabled(sensoresStatus.luces === 'on');
          }
        }
      }
    }, 2000); // Revisa el estado cada 2 segundos
  
    return () => clearInterval(interval); // Limpia el intervalo al desmontar
}, [alarmEnabled, rociadoresEnabled, lucesEnabled, manualChangeRociadores]);

  
  const processTemperatureData = (temperatura) => {
    const labels = temperatura.map(item => new Date(item.fecha).toLocaleTimeString());
    const temps = temperatura.map(item => item.temp);

    setTemperatureData({
      labels: labels,
      datasets: [
        {
          label: 'Temperatura (°C)',
          data: temps,
          borderColor: 'rgba(75,192,192,1)',
          backgroundColor: 'rgba(75,192,192,0.2)',
        },
      ],
    });

    const temperatureLog = temperatura.map(item => ({
      date: item.fecha,
      action: `Temperatura registrada: ${item.temp}°C`,
    }));
    setAccessLogData(prevLogs => [...prevLogs, ...temperatureLog]);
  };

  const processACData = (ac) => {
    const encendido = ac.filter(item => item.activado === "on").length;
    const apagado = ac.filter(item => item.activado === "off").length;

    setAirConditioningData({
      labels: ['Encendido', 'Apagado'],
      datasets: [
        {
          label: 'Aire Acondicionado',
          data: [encendido, apagado],
          backgroundColor: ['rgba(54,162,235,0.6)', 'rgba(255,99,132,0.6)'],
        },
      ],
    });

    const acLog = ac.map(item => ({
      date: item.fecha,
      action: `AC: ${item.activado === "on" ? "Encendido" : "Apagado"}`,
    }));
    setAccessLogData(prevLogs => [...prevLogs, ...acLog]);
  };
  
  const processAlarmData = (alarma) => {
    setFireAlarmData(prevData => {
      const encendidaAnterior = prevData ? prevData.datasets[0].data[0] : 0;
      const apagadaAnterior = prevData ? prevData.datasets[0].data[1] : 0;
  
      const encendida = alarma.filter(item => item.activado === "on").length;
      const apagada = alarma.filter(item => item.activado === "off").length;
  
      return {
        labels: ['Encendida', 'Apagada'],
        datasets: [
          {
            label: 'Alarma',
            data: [
              encendidaAnterior + encendida,
              apagadaAnterior + apagada
            ],
            backgroundColor: ['rgba(255,99,132,0.6)', 'rgba(255,205,86,0.6)'],
          },
        ],
      };
    });
  };
  

  const processAccessData = (acceso) => {
    const accessLog = acceso.map(item => ({
      date: item.fecha,
      action: `Solicitud de acceso: ${item.acceso ? "Permitido" : "Denegado"}`,
    }));
    setAccessLogData(prevLogs => [...prevLogs, ...accessLog]);
  };

  const processInvernaderoData = (invernadero) => {
    setInvernaderoData(prevData => {
      const encendidoAnterior = prevData ? prevData.datasets[0].data[0] : 0;
      const apagadoAnterior = prevData ? prevData.datasets[0].data[1] : 0;

      const encendido = invernadero.filter(item => item.activado === "on").length;
      const apagado = invernadero.filter(item => item.activado === "off").length;

      return {
        labels: ['Encendido', 'Apagado'],
        datasets: [
          {
            label: 'Invernadero',
            data: [
              encendidoAnterior + encendido,
              apagadoAnterior + apagado
            ],
            backgroundColor: ['rgba(75,192,192,1)', 'rgba(153,102,255,0.6)'],
          },
        ],
      };
    });

    const invernaderoLog = invernadero.map(item => ({
      date: item.fecha,
      action: `Invernadero: ${item.activado === "on" ? "Encendido" : "Apagado"}`,
    }));
    setAccessLogData(prevLogs => [...prevLogs, ...invernaderoLog]);
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleLogout = () => {
    alert('Sesión cerrada correctamente');
    navigate('/');
  };const handleSwitchChange = async (e, action) => {
    const status = e.target.checked ? 'encendido' : 'apagado';
    const currentDateTime = new Date().toLocaleString();

    console.log(`Estado del ${action}:`, status); // Verificar el estado

    if (action === 'Alarma') {
        try {
            const alarmStatus = await postStatus('http://192.168.0.21:5000/alarma', status);

            if (alarmStatus && alarmStatus.alarma === (status === 'encendido' ? 'on' : 'off')) {
                setAlarmEnabled(status === 'encendido');

                // Registrar la acción en el log
                const newLog = {
                    date: currentDateTime,
                    action: `Alarma: ${status === 'encendido' ? 'Encendida' : 'Apagada'}`,
                };
                setAccessLogData(prevLogs => [...prevLogs, newLog]);
            } else {
                alert('Error al cambiar el estado de la alarma.');
            }
        } catch (error) {
            console.error('Error al cambiar el estado de la alarma:', error);
            alert('No se pudo cambiar el estado de la alarma. Intenta de nuevo.');
            setAlarmDisabled(false);
        }
    }

    // Rociadores
    if (action === 'Rociadores') {
        try {
            // Evitar que las actualizaciones automáticas interfieran
            setManualChangeRociadores(true);
            const invernaderoStatus = await postStatus('http://192.168.0.21:5000/invernadero', status);

            if (invernaderoStatus) {
                setRociadoresEnabled(status === 'encendido');
                const newLog = {
                    date: currentDateTime,
                    action: `Invernadero: ${status === 'encendido' ? 'Encendido' : 'Apagado'}`,
                };
                setAccessLogData(prevLogs => [...prevLogs, newLog]);

                // Mantener el cambio manual por 3 segundos antes de permitir actualizaciones automáticas
                setTimeout(() => {
                    setManualChangeRociadores(false);
                }, 3000);
            } else {
                alert('Error al cambiar el estado del invernadero.');
            }
        } catch (error) {
            console.error('Error al cambiar el estado del invernadero:', error);
            setManualChangeRociadores(false); // Asegurarse de restablecer el control manual
        }
    }

    // Luces
    if (action === 'Luces') {
        try {
            const lucesStatus = await postStatus('http://192.168.0.21:5000/luces', status);

            if (lucesStatus) {
                setLucesEnabled(status === 'encendido');
                const newLog = {
                    date: currentDateTime,
                    action: `Luces: ${status === 'encendido' ? 'Encendidas' : 'Apagadas'}`,
                };
                setAccessLogData(prevLogs => [...prevLogs, newLog]);
            } else {
                alert('Error al cambiar el estado de las luces.');
            }
        } catch (error) {
            console.error('Error al cambiar el estado de las luces:', error);
        }
    }
};

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Cargando datos...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Panel de Control de la Casa Inteligente</h1>
        <button className="logout-button" onClick={handleLogout}>
          Cerrar Sesión
        </button>
      </header>
  
      <div className="dashboard-content">
        <div className="controls-section">
          <h3>Controles de la Casa</h3>
          <label className="switch">
            <input type="checkbox" onChange={(e) => handleSwitchChange(e, 'Luces')} checked={lucesEnabled} disabled={!isAuthorized} />
            <span className="slider"></span>
            Encender/Apagar Luces
          </label>
          <label className="switch">
            <input type="checkbox" onChange={(e) => handleSwitchChange(e, 'Rociadores')} checked={rociadoresEnabled} disabled={!isAuthorized} />
            <span className="slider"></span>
            Encender/Apagar Rociadores
          </label>
          <label className="switch">
            <input type="checkbox" checked={alarmEnabled} onChange={(e) => handleSwitchChange(e, 'Alarma')} disabled={!isAuthorized || alarmDisabled} />
            <span className="slider"></span>
            Apagar Alarma
          </label>
        </div>
        
        <div className="chart-section">
          <div className="chart-container">
            <h3>Lectura del sensor de temperatura</h3>
            <Line data={temperatureData} />
          </div>
  
          <div className="chart-container">
            <h3>Activaciones del sistema de aire acondicionado</h3>
            <Bar data={airConditioningData} />
          </div>
  
          <div className="chart-container">
            <h3>Activación de la alarma contra incendios</h3>
            <Pie data={fireAlarmData} />
          </div>
  
          <div className="chart-container">
            <h3>Invernadero</h3>
            <Bar data={invernaderoData} />
          </div>
          
          <div className="table-container">
            <h3>Registro de ingreso a la casa a través del patrón de seguridad</h3>
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                {accessLogData.map((log, index) => (
                  <tr key={index}>
                    <td>{log.date}</td>
                    <td>{log.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
  

    <div className="message-container">
    <h3>Mostrar Mensaje</h3>
    <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Escribe tu mensaje"
        className="message-input"
    />
    <button onClick={handleShowMessage} className="message-button">
        Mostrar Mensaje
    </button>
    {shownMessage && <p className="shown-message">{shownMessage}</p>}
    </div>

  
      <footer className="dashboard-footer">
        <p>© 2024 Casa Inteligente - Proyecto de Arquitectura de Sistemas</p>
      </footer>
    </div>
  );
  
};
Dashboard.propTypes = {
    isAuthorized: PropTypes.bool.isRequired,  
  };
export default Dashboard;

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';  // Importa PropTypes para validar props
import './login.css';

function Login({ setIsAuthorized }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const validUsername = "grupo5_A_proy1";
  const validPassword = "sisalearqui2024";

  const handleLogin = (e) => {
    e.preventDefault();

    if (username === validUsername && password === validPassword) {
      setIsAuthorized(true);  // Usuario autorizado
    } else {
      setError('Usuario o contraseña incorrectos');
      setIsAuthorized(false); // Usuario no autorizado, pero podrá ingresar con botones deshabilitados
    }

    navigate('/dashboard'); // Redirige al dashboard en ambos casos
  };

  return (
    <div className="login-page">
      <div className="login-left">
        <h1>PROYECTO ARQUI 1</h1>
      </div>
      <div className="login-right">
        <h2>Login</h2>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Usuario"
            required
          />
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
          <button type="submit" className="login-button">Enviar</button>
          {error && <p className="error-message">{error}</p>}
        </form>
      </div>
    </div>
  );
}

Login.propTypes = {
  setIsAuthorized: PropTypes.func.isRequired,
};

export default Login;

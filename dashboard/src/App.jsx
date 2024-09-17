import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/login';
import Dashboard from './components/Dashboard';

function App() {
  const [isAuthorized, setIsAuthorized] = useState(false); // Estado de autorización

  return (
    <Router>
      <Routes>
        {/* Pasamos la función setIsAuthorized al Login */}
        <Route 
          path="/" 
          element={<Login setIsAuthorized={setIsAuthorized} />} 
        />

        {/* El usuario puede ingresar, pero los botones se deshabilitan si no está autorizado */}
        <Route 
          path="/dashboard" 
          element={<Dashboard isAuthorized={isAuthorized} />} 
        />
      </Routes>
    </Router>
  );
}

export default App;

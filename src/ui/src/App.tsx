import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/index';
import DocumentPage from './pages/document/[id]';
import AnonymizePage from './pages/document/anonymize/[id]';
import DeanonymizePage from './pages/deanonymize';
import './globals.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/document/:id" element={<DocumentPage />} />
        <Route path="/document/anonymize/:id" element={<AnonymizePage />} />
        <Route path="/deanonymize" element={<DeanonymizePage />} />
      </Routes>
    </Router>
  )
}

export default App

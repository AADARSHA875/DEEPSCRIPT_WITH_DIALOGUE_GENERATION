import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import SceneInputForm from './pages/SceneInputForm';
import ResultPage from './pages/ResultPage';
import Header from "./components/Header";

export default function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<SceneInputForm />} />
        <Route path="/result" element={<ResultPage />} />
      </Routes>
    </Router>
  );
}

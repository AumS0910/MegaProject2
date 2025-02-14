import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'; 
import './App.css';
import CreateAccount from './components/CreateAccount';
import ForgotPassword from './components/ForgotPassword';
import GenerateBrochure from './components/GenerateBrochure';
import LandingPage from './components/LandingPage';
import LoginPage from './components/LoginPage';
import ProfilePage from './components/ProfilePage';
import RecentBrochurePage from './components/RecentBrochurePage';

function App() {
  return (
    <Router>
      <Routes> 
        <Route path="/" element={<LandingPage />} /> 
        <Route path="/LoginPage" element={<LoginPage/>}/>
        <Route path="/forgot-password" element={<ForgotPassword/>}/>
        <Route path="/create-account" element={<CreateAccount/>}/>
        <Route path="/generate-brochure" element={<GenerateBrochure/>}/>
        <Route path="/recent-brochures" element={<RecentBrochurePage/>}/>
        <Route path="/profile" element={<ProfilePage/>}/>
      </Routes>
    </Router>
  );
}

export default App;

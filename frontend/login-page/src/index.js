import { GoogleOAuthProvider } from '@react-oauth/google'; // Import GoogleOAuthProvider
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Google OAuth client ID
const GOOGLE_CLIENT_ID = "214570525185-6ta6b3brbvi1ieqn07ah7dime7anlcga.apps.googleusercontent.com";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <GoogleOAuthProvider 
      clientId={GOOGLE_CLIENT_ID}
      onScriptLoadError={() => {
        console.error('Failed to load Google OAuth script. Please check your configuration.');
      }}
      onScriptLoadSuccess={() => {
        console.log('Google OAuth script loaded successfully');
      }}
    >
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>
);

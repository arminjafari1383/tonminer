import React from 'react';
import {createRoot} from 'react-dom/client';
import {TonConnectUIProvider} from '@tonconnect/ui-react';
import App from './App.jsx';
import './original.css';
import './app.css';
const url=import.meta.env.VITE_PUBLIC_URL || window.location.origin;
createRoot(document.getElementById('root')).render(<TonConnectUIProvider manifestUrl={`${url.replace(/\/$/,'')}/tonconnect-manifest.json`}><App/></TonConnectUIProvider>);

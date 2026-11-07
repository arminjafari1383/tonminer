import React from "react";
import {createRoot} from "react-dom/client";
import {TonConnectUIProvider} from "@tonconnect/ui-react";
import App from "./App";
import {AuthProvider} from "./context";
import "./original.css";
import "./app.css";
import "./azure.css";

const publicUrl=import.meta.env.VITE_PUBLIC_URL || window.location.origin;
createRoot(document.getElementById("root")).render(
 <React.StrictMode>
  <TonConnectUIProvider manifestUrl={`${publicUrl.replace(/\/$/,"")}/tonconnect-manifest.json`}>
   <AuthProvider><App/></AuthProvider>
  </TonConnectUIProvider>
 </React.StrictMode>
);

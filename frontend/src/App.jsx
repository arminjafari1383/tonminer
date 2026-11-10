import React from "react";
import {useAuth} from "./context";
import MinerApp from "./pages/MinerApp";

export default function App(){
 const {user,loading,error,retry}=useAuth();
 if(loading)return <p className="loading">Loading…</p>;
 if(!user)return <main className="auth"><p className="error">{error||"Could not connect to the server."}</p><button className="primary" onClick={retry}>Try again</button></main>;
 return <>{user.demo&&<div style={{background:"#b45309",color:"#fff",textAlign:"center",padding:"6px 10px",fontSize:13}}>Demo mode: all amounts are simulated; no real TON is moved.</div>}<MinerApp demo={!!user.demo}/></>;
}
// f
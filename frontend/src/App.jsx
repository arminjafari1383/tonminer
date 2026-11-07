import React from "react";
import {useAuth} from "./context";
import MinerApp from "./pages/MinerApp";

export default function App(){
 const {user,loading,error,retry}=useAuth();
 if(loading)return <p className="loading">در حال بارگذاری…</p>;
 if(!user)return <main className="auth"><p className="error">{error||"اتصال برقرار نشد."}</p><button className="primary" onClick={retry}>تلاش دوباره</button></main>;
 return <MinerApp/>;
}

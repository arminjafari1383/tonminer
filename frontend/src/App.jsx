import React from "react";
import {useAuth} from "./context";
import MinerApp from "./pages/MinerApp";

export default function App(){
 const {user,loading,error,retry}=useAuth();
 if(loading)return <p className="loading">در حال بارگذاری…</p>;
 if(!user)return <main className="auth"><p className="error">{error||"اتصال برقرار نشد."}</p><button className="primary" onClick={retry}>تلاش دوباره</button></main>;
 return <>{user.demo&&<div style={{background:"#b45309",color:"#fff",textAlign:"center",padding:"6px 10px",fontSize:13}}>{"حالت آزمایشی: همه‌ی مبالغ فرضی هستند و هیچ TON واقعی جابه‌جا نمی‌شود."}</div>}<MinerApp/></>;
}

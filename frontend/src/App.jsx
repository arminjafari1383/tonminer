import React from "react";
import {useAuth} from "./context";
import Auth from "./pages/Auth";
import MinerApp from "./pages/MinerApp";

export default function App(){
 const {user,loading,logout}=useAuth();
 if(loading)return <p className="loading">در حال بارگذاری…</p>;
 return user?<MinerApp onLogout={logout}/>:<Auth/>;
}

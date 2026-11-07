import React,{createContext,useContext,useEffect,useState} from "react";
import {api,setTokens,clearTokens,getAccessToken} from "./services/api";
const C=createContext(null);

function initialReferral(){
 try{
  const params=new URLSearchParams(window.location.search);
  const direct=params.get("ref");
  if(direct)return direct;
  const start=params.get("tgWebAppStartParam")||window.Telegram?.WebApp?.initDataUnsafe?.start_param||"";
  return start.startsWith("ref_")?start.slice(4):"";
 }catch{return ""}
}

// Shared promise so React StrictMode's double effect doesn't create two accounts.
let starting=null;
async function start(){
 if(getAccessToken()){
  try{return await api.me();}
  catch(e){if(e.status!==401)throw e;clearTokens();}
 }
 const d=await api.guest(initialReferral());
 setTokens(d.access,d.refresh);
 return api.me();
}

export function AuthProvider({children}){
 const [user,setUser]=useState(null),[loading,setLoading]=useState(true),[error,setError]=useState("");
 function boot(){
  setLoading(true);setError("");
  starting=starting||start().finally(()=>{starting=null;});
  starting.then(setUser).catch(e=>setError(e.message||"خطا در اتصال به سرور")).finally(()=>setLoading(false));
 }
 useEffect(boot,[]);
 return <C.Provider value={{user,loading,error,retry:boot}}>{children}</C.Provider>;
}
export const useAuth=()=>useContext(C);

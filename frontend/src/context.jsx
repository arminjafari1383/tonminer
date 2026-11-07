import React,{createContext,useContext,useEffect,useState} from "react";
import {api,setTokens,clearTokens} from "./services/api";
const C=createContext(null);
export function AuthProvider({children}){
 const [user,setUser]=useState(null),[loading,setLoading]=useState(true);
 useEffect(()=>{
  if(localStorage.getItem("ton_access"))api.me().then(setUser).catch(()=>{clearTokens();}).finally(()=>setLoading(false));
  else setLoading(false);
 },[]);
 async function login(u,p){const d=await api.login(u,p);setTokens(d.access,d.refresh);setUser(await api.me());}
 async function register(u,e,p,referralCode=""){await api.register(u,e,p,referralCode);await login(u,p);}
 function logout(){clearTokens();setUser(null);}
 return <C.Provider value={{user,loading,login,register,logout}}>{children}</C.Provider>;
}
export const useAuth=()=>useContext(C);

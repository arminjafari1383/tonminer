import {useState} from "react";
import {useAuth} from "../context";

function initialReferral(){
 try{
   const params=new URLSearchParams(window.location.search);
   const direct=params.get("ref");
   if(direct)return direct;
   const start=params.get("tgWebAppStartParam") || window.Telegram?.WebApp?.initDataUnsafe?.start_param || "";
   return start.startsWith("ref_") ? start.slice(4) : "";
 }catch{return ""}
}
export default function Auth(){
 const{login,register}=useAuth();
 const[mode,setMode]=useState("login"),[u,U]=useState(""),[e,E]=useState(""),[p,P]=useState(""),[ref,R]=useState(initialReferral()),[err,Err]=useState("");
 async function submit(ev){ev.preventDefault();Err("");try{if(mode==="login")await login(u,p);else await register(u,e,p,ref)}catch(x){Err(x.message)}}
 return <main className="auth"><h1>TON Miner</h1><p className="muted">برای ادامه وارد شوید یا حساب بسازید.</p>
 <form onSubmit={submit}>
  <input placeholder="نام کاربری" value={u} onChange={x=>U(x.target.value)} required/>
  {mode==="register"&&<><input type="email" placeholder="ایمیل" value={e} onChange={x=>E(x.target.value)} required/><input placeholder="کد دعوت (اختیاری)" value={ref} onChange={x=>R(x.target.value)} dir="ltr"/></>}
  <input type="password" placeholder="رمز عبور (حداقل ۱۰ کاراکتر)" value={p} onChange={x=>P(x.target.value)} required minLength={mode==="register"?10:1}/>
  {err&&<p className="error">{err}</p>}
  <button className="primary">{mode==="login"?"ورود":"ثبت‌نام"}</button>
 </form>
 <button className="link" onClick={()=>setMode(mode==="login"?"register":"login")}>{mode==="login"?"ساخت حساب جدید":"ورود به حساب"}</button>
 </main>;
}

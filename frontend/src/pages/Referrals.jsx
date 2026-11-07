import {useEffect,useState} from "react";
import {api} from "../services/api";
import {Copy,Share2,Users,Gift,CheckCircle2} from "lucide-react";

export default function Referrals(){
 const [d,D]=useState(null),[msg,M]=useState(""),[err,E]=useState("");
 async function load(){try{D(await api.referrals())}catch(x){E(x.message)}}
 useEffect(()=>{load()},[]);
 async function copy(value,label){
   try{await navigator.clipboard.writeText(value);M(`${label} کپی شد.`)}
   catch{M("مرورگر اجازه کپی نداد؛ متن را دستی کپی کنید.")}
 }
 function share(){
   if(!d?.referral_link){M("برای ساخت لینک تلگرام، TELEGRAM_BOT_USERNAME و TELEGRAM_APP_SHORT_NAME را در فایل .env تنظیم کنید.");return}
   const url=`https://t.me/share/url?url=${encodeURIComponent(d.referral_link)}&text=${encodeURIComponent("با لینک من به TON Miner بپیوندید.")}`;
   window.open(url,"_blank","noopener,noreferrer");
 }
 if(err)return <p className="error">{err}</p>;
 if(!d)return <p>در حال بارگذاری اطلاعات دعوت…</p>;
 const inviteValue=d.referral_link || d.referral_code;
 return <>
   <h2>دعوت از دوستان</h2>
   <p className="muted">با کد دعوت شما ثبت‌نام کنند؛ پس از ثبت‌نام موفق، پاداش به موجودی شما اضافه می‌شود.</p>
   <div className="stats">
     <div><Users/><small>کل دعوت‌ها</small><b>{d.count}</b></div>
     <div><CheckCircle2/><small>دعوت‌های تأییدشده</small><b>{d.verified_count}</b></div>
   </div>
   <div className="panel">
     <Gift size={22}/>
     <h3>پاداش هر دعوت موفق</h3>
     <strong className="reward">{d.reward_per_referral} TON</strong>
     <p className="muted">مجموع پاداش دریافت‌شده: {d.total_reward} TON</p>
   </div>
   <div className="panel">
     <h3>لینک اختصاصی دعوت</h3>
     <input readOnly dir="ltr" value={inviteValue}/>
     {!d.referral_link&&<p className="muted">فعلاً کد دعوت نمایش داده شده است. برای ساخت لینک مستقیم تلگرام، تنظیمات ربات را در .env وارد کنید.</p>}
     <div className="actions">
       <button className="primary" onClick={()=>copy(inviteValue,d.referral_link?"لینک دعوت":"کد دعوت")}><Copy size={17}/> کپی</button>
       <button className="ghost" onClick={share}><Share2 size={17}/> اشتراک‌گذاری</button>
     </div>
     <p className="muted">کد دعوت: <b dir="ltr">{d.referral_code}</b></p>
   </div>
   <h3>افرادی که دعوت کرده‌اید</h3>
   {d.items.length===0?<div className="panel muted">هنوز کسی با کد دعوت شما ثبت‌نام نکرده است.</div>:d.items.map((x,i)=><div className="row" key={`${x.username}-${i}`}><span><b>{x.username}</b><small className="muted">{new Date(x.created_at).toLocaleDateString("fa-IR")}</small></span><b className="reward">+{x.reward_amount} TON</b></div>)}
   {msg&&<p className="notice">{msg}</p>}
 </>;
}

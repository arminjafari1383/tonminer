import React,{useState,useEffect} from 'react';
import {useTonWallet,useTonConnectUI,toUserFriendlyAddress} from '@tonconnect/ui-react';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000/api';
const TIERS=[{a:3,r:.5,g:'bronze'},{a:6,r:.75,g:'bronze'},{a:9,r:1,g:'bronze'},{a:20,r:1.5,g:'silver'},{a:40,r:1.75,g:'silver'},{a:60,r:2.3,g:'silver'},{a:100,r:3,g:'gold'},{a:300,r:3.5,g:'gold'},{a:1000,r:4,g:'gold'}];
const nano=n=>BigInt(Math.round(Number(n)*1e9)).toString();
const short=s=>s?`${s.slice(0,5)}…${s.slice(-5)}`:'اتصال کیف پول';
// Builds a base64 BOC with a single cell holding a text comment (opcode 0 + UTF-8 text).
function commentPayload(text){
 const t=new TextEncoder().encode(text),n=t.length+4;
 if(n>127)throw Error('Comment too long');
 const cell=[0,2*n,0,0,0,0,...t];
 const boc=[0xb5,0xee,0x9c,0x72,1,1,1,1,0,cell.length,0,...cell];
 let bin='';for(const b of boc)bin+=String.fromCharCode(b);return btoa(bin)}
async function json(url,opts={}){
 const headers={...(opts.headers||{})};
 const token=localStorage.getItem('ton_access')||'';
 if(token)headers.Authorization=`Bearer ${token}`;
 let r=await fetch(url,{...opts,headers});
 if(r.status===401){
  const refresh=localStorage.getItem('ton_refresh')||'';
  if(refresh){
   const rr=await fetch(`${API}/auth/token/refresh/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh})});
   if(rr.ok){const data=await rr.json();localStorage.setItem('ton_access',data.access);headers.Authorization=`Bearer ${data.access}`;r=await fetch(url,{...opts,headers});}
  }
 }
 const body=await r.json().catch(()=>({}));
 if(!r.ok)throw Error(body.error||body.verification_error||body.detail||'خطای سرور');
 return body
}
async function copyText(v){
 try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(v);return true}}catch{}
 try{const t=document.createElement('textarea');t.value=v;t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.focus();t.select();const ok=document.execCommand('copy');document.body.removeChild(t);return ok}catch{return false}
}
function MinerApp(){
 const wallet=useTonWallet(),[tonUI]=useTonConnectUI();
 const addr=wallet?toUserFriendlyAddress(wallet.account.address):'';
 const [tab,setTab]=useState('mine'),[amount,setAmount]=useState('20'),[order,setOrder]=useState(null),[busy,setBusy]=useState(false),[msg,setMsg]=useState(''),[orders,setOrders]=useState([]),[now,setNow]=useState(Date.now()),[referral,setReferral]=useState(null);
 useEffect(()=>{const timer=setInterval(()=>setNow(Date.now()),1000);return()=>clearInterval(timer)},[]);
 useEffect(()=>{try{setOrders(JSON.parse(localStorage.getItem('ton-orders')||'[]'))}catch{}},[]);
 useEffect(()=>{if(tab==='ref'){json(`${API}/referrals/`).then(setReferral).catch(e=>setMsg(e.message))}},[tab]);
 const storeOrder=p=>{setOrders(v=>{const old=v.find(x=>x.id===p.id)||{};const next=[{...old,...p},...v.filter(x=>x.id!==p.id)].slice(0,40);localStorage.setItem('ton-orders',JSON.stringify(next));return next})};
 const paid=orders.filter(o=>o.status==='confirmed');
 const deposit=paid.reduce((s,o)=>s+Number(o.amount),0);
 // Orders whose transaction was sent from the wallet in the last 15 minutes are checked automatically.
 const pending=orders.filter(o=>o.status==='pending'&&o.sentAt&&Date.now()-o.sentAt<15*60*1000);
 const pendingKey=pending.map(o=>o.id).join(',');
 useEffect(()=>{if(!pendingKey)return;let stop=false,running=false;
  const run=async()=>{if(running)return;running=true;
   for(const id of pendingKey.split(',')){
    try{const u=await json(`${API}/payments/${id}/`);if(stop)break;
     storeOrder(u);setOrder(cur=>cur&&cur.id===u.id?{...cur,...u}:cur);
     if(u.status==='confirmed')setMsg('پرداخت روی بلاک‌چین تأیید شد و موجودی شما افزایش یافت.')}catch{}}
   running=false};
  run();const t=setInterval(run,5000);return()=>{stop=true;clearInterval(t)}},[pendingKey]);
 const chosen=TIERS.filter(t=>Number(amount)>=t.a).at(-1)||TIERS[0];
 const days=(6*86400-Math.floor(now/1000)%(6*86400));
 const countdown=[Math.floor(days/86400),Math.floor(days%86400/3600),Math.floor(days%3600/60),days%60].map(n=>String(n).padStart(2,'0')).join(':');
 async function check(p){try{setBusy(true);const updated=await json(`${API}/payments/${p.id}/`);setOrder(updated);storeOrder(updated);setMsg(updated.status==='confirmed'?'پرداخت روی بلاک‌چین تأیید شد.':'هنوز تراکنش تأییدشده‌ای برای این سفارش پیدا نشده است.')}catch(e){setMsg(e.message)}finally{setBusy(false)}}
 async function pay(){if(!addr){await tonUI.openModal();return}const x=Number(amount);if(!Number.isFinite(x)||x<1||x>100000||!Number.isInteger(x*1e9)){setMsg('مبلغ معتبر حداقل ۱ TON وارد کنید.');return}
 try{setBusy(true);setMsg('در حال ساخت سفارش...');
 const p=await json(`${API}/payments/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({wallet:addr,amount:String(amount)})});setOrder(p);storeOrder(p);
 // TON text comment payload must be a base64 BOC cell (32-bit zero opcode + UTF-8 memo).
 const b64=commentPayload(p.memo);
 await tonUI.sendTransaction({validUntil:Math.floor(Date.now()/1000)+300,network:'-239',messages:[{address:p.receiver,amount:nano(p.amount),payload:b64}]});
 storeOrder({...p,sentAt:Date.now()});setMsg('تراکنش ارسال شد. پرداخت به‌صورت خودکار بررسی می‌شود و پس از تأیید، موجودی شما افزایش می‌یابد.');
 }catch(e){setMsg('پرداخت انجام یا تأیید نشد: '+(e?.message||'خطا'))}finally{setBusy(false)}}
 return <main>
 <header><span className="brand"><span style={{fontSize:25,color:'#0098ea'}}>◆</span><h1>TON Miner</h1></span><span className="header-actions"><button id="wbtn" className={wallet?'on':''} onClick={()=>wallet?tonUI.disconnect():tonUI.openModal()}>{short(addr)} {wallet?'×':'◉'}</button></span></header>
 {tab==='mine'&&<section id="s-mine"><div className="bal"><span className="mu">موجودی تأییدشده واریزی (TON)</span><b><span className="num">{deposit.toFixed(2)}</span><i>TON</i></b></div><div className="dial"><svg viewBox="0 0 264 264"><circle className="tr" cx="132" cy="132" r="120"/><circle className="pg" cx="132" cy="132" r="120" strokeDasharray="754" strokeDashoffset="450"/></svg><div className="mid"><span className="rig" role="img" aria-label="Mining illustration"/><span className="led"><i/>آنلاین (نمایشی)</span></div></div><div className="cd"><div className="mu">چرخه نمایشی ماینینگ</div><b className="num" style={{fontSize:28}}>{countdown}</b></div><div className="gauges"><div><b>{(10+deposit).toFixed(2)}</b><small>TH/s (نمایشی)</small></div><div><b>60</b><small>°C (نمایشی)</small></div><div><b>5200</b><small>RPM (نمایشی)</small></div></div><dl><div><dt>کل واریزهای تأییدشده</dt><dd>{deposit.toFixed(2)} TON</dd></div><div><dt>تعداد پرداخت‌های تأییدشده</dt><dd>{paid.length}</dd></div></dl><button className="btn" onClick={()=>setTab('topup')}>افزایش قدرت استخراج / پرداخت</button><p className="risk" style={{marginTop:20}}>نمایش ماینینگ و نرخ‌های سود این نسخه صرفاً نمایشی‌اند؛ استخراج واقعی و سود تضمین‌شده پیاده‌سازی نشده است.</p></section>}
 {tab==='topup'&&<section id="s-topup"><h2>افزایش قدرت با TON</h2><p className="mu">کیف پول خود را انتخاب کنید، پلن را بزنید و تراکنش را در Tonkeeper یا کیف پول دلخواه تأیید کنید.</p><div className="plans" id="plans">{TIERS.map(t=><button type="button" key={t.a} className={`plan ${t.g}`} aria-checked={Number(amount)===t.a} onClick={()=>setAmount(String(t.a))}><span className="mi"/><span className="pi"><b className="num">{t.a} TON</b><small className="grp">{t.g}</small></span><span className="r"><b>{t.r}%</b><small>نرخ نمونه اولیه</small></span></button>)}</div><label htmlFor="amt">مبلغ دلخواه (TON)</label><input id="amt" type="number" min="1" step="0.000000001" value={amount} onChange={e=>setAmount(e.target.value)}/><div className="sum"><dl><div><dt>قدرت نمایشی پس از پرداخت</dt><dd>{10+deposit+Number(amount||0)} TH</dd></div><div><dt>درصد پلن انتخابی (نمایشی)</dt><dd>{chosen.r}%</dd></div><div><dt>شبکه پرداخت</dt><dd>TON Mainnet</dd></div></dl></div><button className="btn" id="pay" disabled={busy} onClick={pay}>{busy?'در حال پردازش...':wallet?'پرداخت با کیف پول':'انتخاب کیف پول و پرداخت'}</button>{order&&<div className="sum"><h2>سفارش پرداخت</h2><p className="mu">شناسه: <span className="num">{order.id}</span></p><p>وضعیت: <b>{order.status==='confirmed'?'✅ تأییدشده':order.status==='expired'?'منقضی‌شده':'⏳ در انتظار تأیید'}</b></p><p className="mu">توضیح تراکنش: <span className="num">{order.memo}</span></p>{order.status==='pending'&&(pending.some(o=>o.id===order.id)?<p className="mu">⏳ در حال بررسی خودکار روی بلاک‌چین...</p>:<button className="btn o" disabled={busy} onClick={()=>check(order)}>بررسی دستی پرداخت</button>)}</div>}</section>}
 {tab==='ref'&&<section><h2>دعوت دوستان</h2><p className="mu">کد دعوت اختصاصی خود را برای دوستان ارسال کنید.</p>{referral?<><div className="sum"><dl><div><dt>کد دعوت شما</dt><dd className="num">{referral.referral_code}</dd></div><div><dt>کل دعوت‌ها</dt><dd>{referral.count}</dd></div><div><dt>دعوت‌های تأییدشده</dt><dd>{referral.verified_count}</dd></div><div><dt>مجموع پاداش</dt><dd>{referral.total_reward} TON</dd></div></dl></div><h2>لینک دعوت</h2><div className="box"><input readOnly dir="ltr" value={referral.referral_link||referral.referral_code}/><button onClick={async()=>{const v=referral.referral_link||referral.referral_code;setMsg((await copyText(v))?'لینک دعوت کپی شد.':'کپی نشد؛ لینک را دستی انتخاب و کپی کنید.')}}>کپی</button></div><button className="btn" onClick={()=>{if(referral.referral_link){const u=`https://t.me/share/url?url=${encodeURIComponent(referral.referral_link)}&text=${encodeURIComponent('با لینک من به TON Miner بپیوندید.')}`;window.open(u,'_blank','noopener,noreferrer')}else setMsg('برای ساخت لینک تلگرام، نام ربات و Mini App را در تنظیمات سرور وارد کنید.')}}>اشتراک‌گذاری لینک</button><h2>زیرمجموعه‌ها</h2>{referral.items?.length?referral.items.map((x,i)=><div className="history" key={i}><span>{x.username}<small>{new Date(x.created_at).toLocaleDateString('fa-IR')}</small></span><b>{x.verified?'تأییدشده':'در انتظار'} · {x.reward_amount} TON</b></div>):<p className="empty">هنوز دعوتی ثبت نشده است.</p>}</>:<p className="empty">در حال دریافت اطلاعات دعوت…</p>}</section>}
 {tab==='wd'&&<section><h2>برداشت</h2><p>برای برداشت واقعی، احراز هویت مالک کیف پول، دفتر کل موجودی و سامانه امضای امن پرداخت خروجی لازم است. برداشت در این نسخه غیرفعال است.</p><h2>تاریخچه پرداخت</h2><div className="sum">{orders.length?orders.map(o=><div className="history" key={o.id}><span>{o.amount} TON <small>{short(o.id)}</small></span><button className="chip" onClick={()=>{setOrder(o);check(o);setTab('topup')}}>{o.status==='confirmed'?'✅ تأیید':'⏳ بررسی'}</button></div>):<p className="empty">هنوز پرداختی ثبت نشده است.</p>}</div></section>}
 {msg&&<div role="status" className="message">{msg}<button onClick={()=>setMsg('')}>×</button></div>}
 <nav>{[['mine','ماین','⚙'],['topup','شارژ','◆'],['ref','دعوت','♧'],['wd','تاریخچه','☷']].map(([key,label,icon])=><button key={key} aria-selected={tab===key} onClick={()=>{setTab(key);setMsg('');window.scrollTo(0,0)}}><span style={{fontSize:21}}>{icon}</span>{label}</button>)}</nav>
 </main>
}
export default MinerApp;

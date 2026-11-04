import React,{useState,useEffect} from 'react';
import {useTonWallet,useTonConnectUI,toUserFriendlyAddress} from '@tonconnect/ui-react';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000/api';
const TIERS=[{a:3,r:.5,g:'bronze'},{a:6,r:.75,g:'bronze'},{a:9,r:1,g:'bronze'},{a:20,r:1.5,g:'silver'},{a:40,r:1.75,g:'silver'},{a:60,r:2.3,g:'silver'},{a:100,r:3,g:'gold'},{a:300,r:3.5,g:'gold'},{a:1000,r:4,g:'gold'}];
const nano=n=>BigInt(Math.round(Number(n)*1e9)).toString();
const short=s=>s?`${s.slice(0,5)}…${s.slice(-5)}`:'اتصال کیف پول';
async function json(url,opts){const r=await fetch(url,opts);const body=await r.json();if(!r.ok)throw Error(body.error||body.verification_error||'خطای سرور');return body}
function App(){
 const wallet=useTonWallet(),[tonUI]=useTonConnectUI();
 const addr=wallet?toUserFriendlyAddress(wallet.account.address):'';
 const [tab,setTab]=useState('mine'),[amount,setAmount]=useState('20'),[order,setOrder]=useState(null),[busy,setBusy]=useState(false),[msg,setMsg]=useState(''),[orders,setOrders]=useState([]),[balance,setBalance]=useState({balance:'0',confirmed_count:0}),[now,setNow]=useState(Date.now());
 useEffect(()=>{const timer=setInterval(()=>setNow(Date.now()),1000);return()=>clearInterval(timer)},[]);
 useEffect(()=>{try{setOrders(JSON.parse(localStorage.getItem('ton-orders')||'[]'))}catch{}},[]);
 const storeOrder=p=>{setOrders(v=>{const next=[p,...v.filter(x=>x.id!==p.id)].slice(0,40);localStorage.setItem('ton-orders',JSON.stringify(next));return next})};
 const paid=orders.filter(o=>o.status==='confirmed');
 const deposit=Number(balance.balance||0);
 useEffect(()=>{
  if(!addr){setBalance({balance:'0',confirmed_count:0});return}
  let active=true;
  const refresh=()=>json(`${API}/balance/?wallet=${encodeURIComponent(addr)}`).then(v=>{if(active)setBalance(v)}).catch(()=>{});
  refresh();const id=setInterval(refresh,15000);
  return()=>{active=false;clearInterval(id)};
 },[addr]);
 useEffect(()=>{
  if(!addr)return;
  const pending=orders.filter(o=>o.status==='pending' && (!o.wallet || o.wallet===addr));
  if(!pending.length)return;
  const id=setInterval(()=>pending.forEach(p=>check(p)),3000);
  return()=>clearInterval(id);
 },[addr,orders.map(o=>o.id+o.status).join('|')]);
 const chosen=TIERS.filter(t=>Number(amount)>=t.a).at(-1)||TIERS[0];
 const days=(6*86400-Math.floor(now/1000)%(6*86400));
 const countdown=[Math.floor(days/86400),Math.floor(days%86400/3600),Math.floor(days%3600/60),days%60].map(n=>String(n).padStart(2,'0')).join(':');
 async function check(p){
  try {
   const updated=await json(`${API}/payments/${p.id}/`);
   setOrder(current=>current?.id===updated.id?updated:current);
   storeOrder(updated);
   if(updated.status==='confirmed'){
    setMsg('پرداخت تأیید شد؛ موجودی شارژ و فاکتور نهایی صادر شد.');
    if(addr) setBalance(await json(`${API}/balance/?wallet=${encodeURIComponent(addr)}`));
   }
   return updated;
  }catch(e){setMsg('بررسی خودکار پرداخت موقتاً در دسترس نیست: '+e.message)}
 }
 async function pay(){if(!addr){await tonUI.openModal();return}const x=Number(amount);if(!Number.isFinite(x)||x<3||x>100000||!Number.isInteger(x*1e9)){setMsg('مبلغ معتبر حداقل ۳ TON وارد کنید.');return}
 try{setBusy(true);setMsg('در حال ساخت سفارش...');
 const p=await json(`${API}/payments/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({wallet:addr,amount:String(amount)})});setOrder(p);storeOrder({...p,wallet:addr});
 // TON text comment = single cell: 32-bit zero opcode + UTF-8 memo, serialized as a valid BOC (base64).
 const memoBytes=new TextEncoder().encode(p.memo);const cell=new Uint8Array(4+memoBytes.length);cell.set(memoBytes,4);
 const boc=new Uint8Array([0xb5,0xee,0x9c,0x72,0x01,0x01,0x01,0x01,0x00,2+cell.length,0x00,0x00,cell.length*2,...cell]);const b64=btoa(String.fromCharCode(...boc));
 await tonUI.sendTransaction({validUntil:Math.floor(Date.now()/1000)+300,network:'-239',messages:[{address:p.receiver,amount:nano(p.amount),payload:b64}]});
 setMsg('تراکنش ارسال شد؛ چند ثانیه صبر کنید، موجودی و فاکتور بعد از تأیید شبکه خودکار صادر می‌شود.');
 for(let i=0;i<90;i++){await new Promise(r=>setTimeout(r,2000));const u=await check(p);if(u&&u.status!=='pending')break}
 }catch(e){setMsg('پرداخت انجام یا تأیید نشد: '+(e?.message||'خطا'))}finally{setBusy(false)}}
 return <main>
 <header><span className="brand"><span style={{fontSize:25,color:'#0098ea'}}>◆</span><h1>TON Miner</h1></span><button id="wbtn" className={wallet?'on':''} onClick={()=>wallet?tonUI.disconnect():tonUI.openModal()}>{short(addr)} {wallet?'×':'◉'}</button></header>
 {tab==='mine'&&<section id="s-mine"><div className="bal"><span className="mu">موجودی تأییدشده واریزی (TON)</span><b><span className="num">{deposit.toFixed(2)}</span><i>TON</i></b></div><div className="dial"><svg viewBox="0 0 264 264"><circle className="tr" cx="132" cy="132" r="120"/><circle className="pg" cx="132" cy="132" r="120" strokeDasharray="754" strokeDashoffset="450"/></svg><div className="mid"><span className="rig" role="img" aria-label="Mining illustration"/><span className="led"><i/>آنلاین (نمایشی)</span></div></div><div className="cd"><div className="mu">چرخه نمایشی ماینینگ</div><b className="num" style={{fontSize:28}}>{countdown}</b></div><div className="gauges"><div><b>{(10+deposit).toFixed(2)}</b><small>TH/s (نمایشی)</small></div><div><b>60</b><small>°C (نمایشی)</small></div><div><b>5200</b><small>RPM (نمایشی)</small></div></div><dl><div><dt>کل واریزهای تأییدشده</dt><dd>{deposit.toFixed(2)} TON</dd></div><div><dt>تعداد پرداخت‌های تأییدشده</dt><dd>{balance.confirmed_count}</dd></div></dl><button className="btn" onClick={()=>setTab('topup')}>افزایش قدرت استخراج / پرداخت</button><p className="risk" style={{marginTop:20}}>نمایش ماینینگ و نرخ‌های سود این نسخه صرفاً نمایشی‌اند؛ استخراج واقعی و سود تضمین‌شده پیاده‌سازی نشده است.</p></section>}
 {tab==='topup'&&<section id="s-topup"><h2>افزایش قدرت با TON</h2><p className="mu">کیف پول خود را انتخاب کنید، پلن را بزنید و تراکنش را در Tonkeeper یا کیف پول دلخواه تأیید کنید.</p><div className="plans" id="plans">{TIERS.map(t=><button type="button" key={t.a} className={`plan ${t.g}`} aria-checked={Number(amount)===t.a} onClick={()=>setAmount(String(t.a))}><span className="mi"/><span className="pi"><b className="num">{t.a} TON</b><small className="grp">{t.g}</small></span><span className="r"><b>{t.r}%</b><small>نرخ نمونه اولیه</small></span></button>)}</div><label htmlFor="amt">مبلغ دلخواه (TON)</label><input id="amt" type="number" min="3" step="0.000000001" value={amount} onChange={e=>setAmount(e.target.value)}/><div className="sum"><dl><div><dt>قدرت نمایشی پس از پرداخت</dt><dd>{10+deposit+Number(amount||0)} TH</dd></div><div><dt>درصد پلن انتخابی (نمایشی)</dt><dd>{chosen.r}%</dd></div><div><dt>شبکه پرداخت</dt><dd>TON Mainnet</dd></div></dl></div><button className="btn" id="pay" disabled={busy} onClick={pay}>{busy?'در حال پردازش...':wallet?'پرداخت با کیف پول':'انتخاب کیف پول و پرداخت'}</button>{order&&<div className="sum"><h2>{order.status==='confirmed'?'فاکتور پرداخت نهایی':'درخواست پرداخت (هنوز فاکتور نیست)'}</h2><p className="mu">شناسه: <span className="num">{order.id}</span></p><p>وضعیت: <b>{order.status==='confirmed'?'✅ تأییدشده':order.status==='expired'?'منقضی‌شده':'⏳ در انتظار تأیید'}</b></p><p className="mu">توضیح تراکنش: <span className="num">{order.memo}</span></p>{order.receipt&&<><p>شماره فاکتور: <b>{order.receipt.number}</b></p><p>هش تراکنش: <small>{order.receipt.tx_hash}</small></p><p>مبلغ شارژشده: <b>{order.receipt.amount} TON</b></p></>}{order.status==='pending'&&<p className="mu">⏳ منتظر تأیید خودکار شبکه؛ نیازی به زدن دکمه بررسی نیست.</p>}</div>}</section>}
 {tab==='ref'&&<section><h2>دعوت دوستان</h2><p>سیستم دعوت در این نسخه نیاز به احراز هویت کاربر و ثبت اطلاعات در Django دارد و هنوز فعال نشده است.</p></section>}
 {tab==='wd'&&<section><h2>برداشت</h2><p>برای برداشت واقعی، احراز هویت مالک کیف پول، دفتر کل موجودی و سامانه امضای امن پرداخت خروجی لازم است. برداشت در این نسخه غیرفعال است.</p><h2>تاریخچه پرداخت</h2><div className="sum">{orders.length?orders.map(o=><div className="history" key={o.id}><span>{o.amount} TON <small>{short(o.id)}</small></span><button className="chip" onClick={()=>{setOrder(o);setTab('topup')}}>{o.status==='confirmed'?'✅ تأیید':'⏳ بررسی'}</button></div>):<p className="empty">هنوز پرداختی ثبت نشده است.</p>}</div></section>}
 {msg&&<div role="status" className="message">{msg}<button onClick={()=>setMsg('')}>×</button></div>}
 <nav>{[['mine','ماین','⚙'],['topup','شارژ','◆'],['ref','دعوت','♧'],['wd','تاریخچه','☷']].map(([key,label,icon])=><button key={key} aria-selected={tab===key} onClick={()=>{setTab(key);setMsg('');window.scrollTo(0,0)}}><span style={{fontSize:21}}>{icon}</span>{label}</button>)}</nav>
 </main>
}
export default App;

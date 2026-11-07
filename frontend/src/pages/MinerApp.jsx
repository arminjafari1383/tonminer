import React,{useState,useEffect} from 'react';
import {useTonWallet,useTonConnectUI,toUserFriendlyAddress} from '@tonconnect/ui-react';
const API=import.meta.env.VITE_API_URL||'http://localhost:8000/api';
const TIERS=[{a:3,r:.5,g:'bronze'},{a:6,r:.75,g:'bronze'},{a:9,r:1,g:'bronze'},{a:20,r:1.5,g:'silver'},{a:40,r:1.75,g:'silver'},{a:60,r:2.3,g:'silver'},{a:100,r:3,g:'gold'},{a:300,r:3.5,g:'gold'},{a:1000,r:4,g:'gold'}];
const nano=n=>BigInt(Math.round(Number(n)*1e9)).toString();
const short=s=>s?`${s.slice(0,5)}…${s.slice(-5)}`:'Connect wallet';
const f4=n=>Number(n||0).toFixed(4);
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
 if(!r.ok)throw Error(body.error||body.verification_error||body.detail||'Server error');
 return body
}
async function copyText(v){
 try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(v);return true}}catch{}
 try{const t=document.createElement('textarea');t.value=v;t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.focus();t.select();const ok=document.execCommand('copy');document.body.removeChild(t);return ok}catch{return false}
}
function MinerApp({demo=false}){
 const wallet=useTonWallet(),[tonUI]=useTonConnectUI();
 const addr=wallet?toUserFriendlyAddress(wallet.account.address):'';
 const [tab,setTab]=useState('mine'),[amount,setAmount]=useState('20'),[order,setOrder]=useState(null),[busy,setBusy]=useState(false),[msg,setMsg]=useState(''),[orders,setOrders]=useState([]),[now,setNow]=useState(Date.now()),[referral,setReferral]=useState(null),[d,setD]=useState(null),[wds,setWds]=useState([]),[wdAmount,setWdAmount]=useState(''),[wdWallet,setWdWallet]=useState('');
 const loadDash=()=>json(`${API}/mining/dashboard/`).then(setD).catch(e=>setMsg(e.message));
 useEffect(()=>{const timer=setInterval(()=>setNow(Date.now()),1000);return()=>clearInterval(timer)},[]);
 useEffect(()=>{loadDash();const t=setInterval(loadDash,5000);return()=>clearInterval(t)},[]);
 useEffect(()=>{try{setOrders(JSON.parse(localStorage.getItem('ton-orders')||'[]'))}catch{}},[]);
 const loadWds=()=>json(`${API}/withdrawals/`).then(setWds).catch(e=>setMsg(e.message));
 useEffect(()=>{if(tab==='wd')loadWds()},[tab]);
 useEffect(()=>{if(tab==='ref'){json(`${API}/referrals/`).then(setReferral).catch(e=>setMsg(e.message))}},[tab]);
 const storeOrder=p=>{setOrders(v=>{const old=v.find(x=>x.id===p.id)||{};const next=[{...old,...p},...v.filter(x=>x.id!==p.id)].slice(0,40);localStorage.setItem('ton-orders',JSON.stringify(next));return next})};
 const paid=orders.filter(o=>o.status==='confirmed');
 const power=10+Number(d?.deposit_total||0);
 // Orders whose transaction was sent from the wallet in the last 15 minutes are checked automatically.
 const pending=orders.filter(o=>o.status==='pending'&&o.sentAt&&Date.now()-o.sentAt<15*60*1000);
 const pendingKey=pending.map(o=>o.id).join(',');
 useEffect(()=>{if(!pendingKey)return;let stop=false,running=false;
  const run=async()=>{if(running)return;running=true;
   for(const id of pendingKey.split(',')){
    try{const u=await json(`${API}/payments/${id}/`);if(stop)break;
     storeOrder(u);setOrder(cur=>cur&&cur.id===u.id?{...cur,...u}:cur);
     if(u.status==='confirmed'){setMsg('Payment confirmed on the blockchain. Your mining power has been updated.');loadDash()}}catch{}}
   running=false};
  run();const t=setInterval(run,5000);return()=>{stop=true;clearInterval(t)}},[pendingKey]);
 const chosen=TIERS.filter(t=>Number(amount)>=t.a).at(-1)||TIERS[0];
 const left=d?Math.max(0,Math.floor((new Date(d.next_free_cycle_at).getTime()-now)/1000)):0;
 const countdown=[Math.floor(left/86400),Math.floor(left%86400/3600),Math.floor(left%3600/60),left%60].map(n=>String(n).padStart(2,'0')).join(':');
 async function check(p){try{setBusy(true);const updated=await json(`${API}/payments/${p.id}/`);setOrder(updated);storeOrder(updated);setMsg(updated.status==='confirmed'?'Payment confirmed.':'No confirmed transaction found for this order yet.');loadDash()}catch(e){setMsg(e.message)}finally{setBusy(false)}}
 async function pay(){if(!demo&&!addr){await tonUI.openModal();return}const x=Number(amount);if(!Number.isFinite(x)||x<3||x>100000||!Number.isInteger(Math.round(x*1e9))){setMsg('Enter a valid amount (minimum 3 TON).');return}
 try{setBusy(true);setMsg('Creating order...');
 const p=await json(`${API}/payments/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({wallet:addr,amount:String(amount)})});setOrder(p);storeOrder(p);
 if(demo){setMsg('Simulated purchase added. Your mining power and daily profit have been updated.');await loadDash();setTab('mine');return}
 // TON text comment payload must be a base64 BOC cell (32-bit zero opcode + UTF-8 memo).
 const b64=commentPayload(p.memo);
 await tonUI.sendTransaction({validUntil:Math.floor(Date.now()/1000)+300,network:'-239',messages:[{address:p.receiver,amount:nano(p.amount),payload:b64}]});
 storeOrder({...p,sentAt:Date.now()});setMsg('Transaction sent. The payment is checked automatically and your mining power updates once it is confirmed.');
 }catch(e){setMsg('Payment was not completed or confirmed: '+(e?.message||'error'))}finally{setBusy(false)}}
 async function withdraw(){const x=Number(wdAmount);if(!Number.isFinite(x)||x<=0){setMsg('Enter a valid amount.');return}
 try{setBusy(true);const w=await json(`${API}/withdrawals/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount:String(wdAmount),wallet_address:wdWallet.trim()})});setMsg(w.simulated?'Simulated withdrawal completed. Nothing was sent on-chain.':'Withdrawal request submitted.');setWdAmount('');await Promise.all([loadDash(),loadWds()])}catch(e){setMsg(e.message)}finally{setBusy(false)}}
 return <main>
 <header><span className="brand"><span style={{fontSize:25,color:'#0098ea'}}>◆</span><h1>TON Miner</h1></span>{!demo&&<span className="header-actions"><button id="wbtn" className={wallet?'on':''} onClick={()=>wallet?tonUI.disconnect():tonUI.openModal()}>{short(addr)} {wallet?'×':'◉'}</button></span>}</header>
 {tab==='mine'&&<section id="s-mine"><div className="bal"><span className="mu">Total mined (TON)</span><b><span className="num">{f4(d?.total_mined)}</span><i>TON</i></b></div><div className="dial"><svg viewBox="0 0 264 264"><circle className="tr" cx="132" cy="132" r="120"/><circle className="pg" cx="132" cy="132" r="120" strokeDasharray="754" strokeDashoffset="450"/></svg><div className="mid"><span className="rig" role="img" aria-label="Mining illustration"/><span className="led"><i/>Online (simulated)</span></div></div><div className="cd"><div className="mu">Next free reward: +{Number(d?.free_cycle_reward||1)} TON in</div><b className="num" style={{fontSize:28}}>{countdown}</b><div className="mu" style={{fontSize:12}}>days : hours : minutes : seconds</div></div><div className="gauges"><div><b>{power.toFixed(2)}</b><small>TH/s (simulated)</small></div><div><b>60</b><small>°C (simulated)</small></div><div><b>5200</b><small>RPM (simulated)</small></div></div><dl><div><dt>Free mining (1 TON every 5 days)</dt><dd>{f4(d?.free_earned)} TON</dd></div><div><dt>Referral rewards</dt><dd>{f4(d?.referral_earned)} TON</dd></div><div><dt>Daily profit from purchases</dt><dd>{f4(d?.yield_earned)} TON</dd></div><div><dt>Total purchased</dt><dd>{Number(d?.deposit_total||0).toFixed(2)} TON</dd></div><div><dt>Current daily profit</dt><dd>{f4(d?.daily_deposit_yield)} TON / day</dd></div><div><dt>Purchases made</dt><dd>{paid.length}</dd></div></dl><button className="btn" onClick={()=>setTab('topup')}>Buy more mining power</button><p className="risk" style={{marginTop:20}}>{demo?'Demo mode: the mining display, purchases and profit rates are simulated. No real TON is moved.':'The mining display and profit rates in this version are illustrative only; real mining and guaranteed returns are not implemented.'}</p></section>}
 {tab==='topup'&&<section id="s-topup"><h2>Buy mining power</h2><p className="mu">{demo?'Pick a plan and confirm. In demo mode no wallet or real payment is needed.':'Connect your wallet, pick a plan and confirm the transaction in Tonkeeper or your wallet of choice.'}</p><div className="plans" id="plans">{TIERS.map(t=><button type="button" key={t.a} className={`plan ${t.g}`} aria-checked={Number(amount)===t.a} onClick={()=>setAmount(String(t.a))}><span className="mi"/><span className="pi"><b className="num">{t.a} TON</b><small className="grp">{t.g}</small></span><span className="r"><b>{t.r}%</b><small>per day</small></span></button>)}</div><label htmlFor="amt">Custom amount (TON, minimum 3)</label><input id="amt" type="number" min="3" step="0.000000001" value={amount} onChange={e=>setAmount(e.target.value)}/><div className="sum"><dl><div><dt>Mining power after purchase</dt><dd>{(power+Number(amount||0)).toFixed(2)} TH</dd></div><div><dt>Daily profit rate for this amount</dt><dd>{chosen.r}%</dd></div><div><dt>Estimated daily profit</dt><dd>{(Number(amount||0)*chosen.r/100).toFixed(4)} TON</dd></div>{!demo&&<div><dt>Payment network</dt><dd>TON Mainnet</dd></div>}</dl></div><button className="btn" id="pay" disabled={busy} onClick={pay}>{busy?'Processing...':demo?'Confirm simulated purchase':wallet?'Pay with wallet':'Connect wallet and pay'}</button>{order&&<div className="sum"><h2>Payment order</h2><p className="mu">ID: <span className="num">{order.id}</span></p><p>Status: <b>{order.status==='confirmed'?'✅ Confirmed':order.status==='expired'?'Expired':'⏳ Waiting for confirmation'}</b></p>{!demo&&<p className="mu">Transaction comment: <span className="num">{order.memo}</span></p>}{order.status==='pending'&&(pending.some(o=>o.id===order.id)?<p className="mu">⏳ Checking the blockchain automatically...</p>:<button className="btn o" disabled={busy} onClick={()=>check(order)}>Check payment manually</button>)}</div>}</section>}
 {tab==='ref'&&<section><h2>Invite friends</h2><p className="mu">Share your personal invite link. You receive 1 TON for every friend who joins with it.</p>{referral?<><div className="sum"><dl><div><dt>Your invite code</dt><dd className="num">{referral.referral_code}</dd></div><div><dt>Total invites</dt><dd>{referral.count}</dd></div><div><dt>Verified invites</dt><dd>{referral.verified_count}</dd></div><div><dt>Total rewards</dt><dd>{referral.total_reward} TON</dd></div></dl></div><h2>Invite link</h2><div className="box"><input readOnly dir="ltr" value={referral.referral_link||referral.referral_code}/><button onClick={async()=>{const v=referral.referral_link||referral.referral_code;setMsg((await copyText(v))?'Invite link copied.':'Copy failed; select the link and copy it manually.')}}>Copy</button></div><button className="btn" onClick={()=>{if(referral.referral_link){const u=`https://t.me/share/url?url=${encodeURIComponent(referral.referral_link)}&text=${encodeURIComponent('Join me on TON Miner using my link.')}`;window.open(u,'_blank','noopener,noreferrer')}else setMsg('No invite link is available yet.')}}>Share link</button><h2>Your referrals</h2>{referral.items?.length?referral.items.map((x,i)=><div className="history" key={i}><span>{x.username}<small>{new Date(x.created_at).toLocaleDateString('en-US')}</small></span><b>{x.verified?'Verified':'Pending'} · {x.reward_amount} TON</b></div>):<p className="empty">No referrals yet.</p>}</>:<p className="empty">Loading referral info…</p>}</section>}
 {tab==='wd'&&<section><h2>Withdraw</h2>{demo?<>
 <div className="bal"><span className="mu">Available to withdraw (TON)</span><b><span className="num">{f4(d?.balance)}</span><i>TON</i></b></div>
 <p className="mu">Minimum withdrawal: {d?.min_withdraw||'100'} TON. Free mining, referral rewards and daily profit are all withdrawable. Demo mode: withdrawals are simulated and nothing is sent on-chain.</p>
 <label htmlFor="wdw">Destination wallet address</label><input id="wdw" dir="ltr" placeholder="UQ… (any text in demo mode)" value={wdWallet} onChange={e=>setWdWallet(e.target.value)}/>
 <label htmlFor="wda">Amount (TON)</label><div className="box"><input id="wda" type="number" min="0" step="0.000000001" value={wdAmount} onChange={e=>setWdAmount(e.target.value)}/><button onClick={()=>setWdAmount(String(Math.floor(Number(d?.balance||0)*1e6)/1e6))}>Max</button></div>
 <button className="btn" disabled={busy} onClick={withdraw}>{busy?'Processing...':'Withdraw (simulated)'}</button>
 <h2>Withdrawal history</h2><div className="sum">{wds.length?wds.map(w=><div className="history" key={w.id}><span>{w.amount} TON<small>{short(w.wallet_address)} · {new Date(w.created_at).toLocaleDateString('en-US')}</small></span><b>{w.status==='paid'?(w.simulated?'✅ Paid (simulated)':'✅ Paid'):w.status==='approved'?'Approved':w.status==='rejected'?'Rejected':'⏳ Pending'}</b></div>):<p className="empty">No withdrawals yet.</p>}</div>
 </>:<p className="mu">Withdrawals are disabled in this version.</p>}</section>}
 {msg&&<div role="status" className="message">{msg}<button onClick={()=>setMsg('')}>×</button></div>}
 <nav>{[['mine','Mine','⚙'],['topup','Buy','◆'],['ref','Invite','♧'],['wd','Withdraw','↧']].map(([key,label,icon])=><button key={key} aria-selected={tab===key} onClick={()=>{setTab(key);setMsg('');window.scrollTo(0,0)}}><span style={{fontSize:21}}>{icon}</span>{label}</button>)}</nav>
 </main>
}
export default MinerApp;

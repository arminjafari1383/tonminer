const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
let access = localStorage.getItem("ton_access") || "";
let refresh = localStorage.getItem("ton_refresh") || "";
export function setTokens(a,r){ access=a; refresh=r; localStorage.setItem("ton_access",a); localStorage.setItem("ton_refresh",r); }
export function getAccessToken(){return access;}
export function clearTokens(){access="";refresh="";localStorage.removeItem("ton_access");localStorage.removeItem("ton_refresh");}
async function request(path, options={}) {
  const headers={"Content-Type":"application/json",...(options.headers||{})};
  if(access) headers.Authorization=`Bearer ${access}`;
  let res=await fetch(`${API}${path}`,{...options,headers});
  if(res.status===401 && refresh){
    const rr=await fetch(`${API}/auth/token/refresh/`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({refresh})});
    if(rr.ok){const data=await rr.json();setTokens(data.access,refresh);headers.Authorization=`Bearer ${data.access}`;res=await fetch(`${API}${path}`,{...options,headers});}
  }
  const data=await res.json().catch(()=>({}));
  if(!res.ok){const e=new Error(data.detail || JSON.stringify(data) || "Request failed");e.status=res.status;throw e;}
  return data;
}
export const api={
  request,
  guest:(referral_code="")=>request("/auth/guest/",{method:"POST",body:JSON.stringify({referral_code})}),
  me:()=>request("/auth/me/"),
  dashboard:()=>request("/mining/dashboard/"),
  wallet:(wallet_address)=>request("/wallet/",{method:"POST",body:JSON.stringify({wallet_address})}),
  deposits:()=>request("/payments/deposits/"),
  createDeposit:(amount)=>request("/payments/deposits/",{method:"POST",body:JSON.stringify({amount})}),
  withdrawals:()=>request("/withdrawals/"),
  createWithdrawal:(amount)=>request("/withdrawals/",{method:"POST",body:JSON.stringify({amount})}),
  referrals:()=>request("/referrals/"),
};

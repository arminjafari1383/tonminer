import {NavLink} from "react-router-dom";import{Pickaxe,Wallet,Users,ArrowDownToLine}from"lucide-react";
const items=[["/","استخراج",Pickaxe],["/topup","شارژ",Wallet],["/referrals","دعوت",Users],["/withdraw","برداشت",ArrowDownToLine]];
export default function BottomNavigation(){return <nav className="bottom">{items.map(([to,label,I])=><NavLink end={to==="/"} to={to} key={to}><I size={21}/><small>{label}</small></NavLink>)}</nav>}

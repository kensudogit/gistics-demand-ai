"use client";
import { useState } from "react";
export default function Home() {
  const [history, setHistory] = useState("12,14,11,17,20,16,15");
  const [result, setResult] = useState<string>("");
  async function predict() {
    try {
      const response = await fetch("/api/forecast", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({history:history.split(",").map(Number),horizon:7}) });
      if (!response.ok) throw new Error(`API error ${response.status}`);
      setResult(JSON.stringify(await response.json(), null, 2));
    } catch(e) { setResult(String(e)); }
  }
  return <main style={{padding:32,maxWidth:720,margin:"auto"}}><h1>物流・需要予測AI（デモ）</h1><p>過去の需要（カンマ区切り）</p><input style={{width:"100%",padding:10}} value={history} onChange={e=>setHistory(e.target.value)} /><p><button onClick={predict}>7日先を予測</button></p><pre>{result}</pre><p>実運用では認証・時系列モデル・データパイプラインが必要です。</p></main>;
}

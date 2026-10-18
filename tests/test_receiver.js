"use strict";
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../web/receiver.js'),'utf8');
function setup(){
 const nodes=new Map();
 const get=id=>{if(!nodes.has(id))nodes.set(id,{value:'auto',textContent:'',dataset:{},parentElement:{},attributes:{},handlers:{},style:{setProperty(){}},setAttribute(key,value){this.attributes[key]=value;},addEventListener(name,callback){this.handlers[name]=callback;},focus(){this.focused=true;},pause(){},play:()=>Promise.resolve()});return nodes.get(id);};
 class Context{
  constructor(){this.state='running';this.sampleRate=48000;this.destination={};this.audioWorklet={addModule:()=>Promise.resolve()};}
  resume(){return Promise.resolve();}
  close(){this.closed=true;return Promise.resolve();}
 }
 class Socket{
  constructor(){Socket.last=this;this.readyState=1;}
  close(){this.closed=true;this.onclose?.({reason:'closed'});}
  send(value){this.sent=JSON.parse(value);}
 }
 class Peer{
  constructor(){Peer.last=this;this.iceGatheringState='complete';}
  close(){this.closed=true;}
  addEventListener(name,callback){this[name]=callback;}
  addTransceiver(){return{receiver:{}};}
  createOffer(){return Promise.resolve({type:'offer',sdp:'test'});}
  setLocalDescription(value){this.localDescription=value;return Promise.resolve();}
  setRemoteDescription(){return Promise.resolve();}
 }
 class Node{
  constructor(){this.port={postMessage(){}};}
  connect(){}
  disconnect(){}
 }
 const scope={console,AudioContext:Context,AudioWorkletNode:Node,WebSocket:Socket,RTCPeerConnection:Peer,
  navigator:{userAgent:'Windows',maxTouchPoints:0},
  document:{getElementById:get,querySelectorAll:()=>[],documentElement:{},body:{dataset:{}},addEventListener(){}},
  location:{href:'https://localhost/',protocol:'https:'},
  localStorage:{getItem:()=>null,setItem(){}},URL,URLSearchParams,AbortController,
  setTimeout,clearTimeout,setInterval:()=>1,clearInterval(){},
  fetch:async url=>url==='/ui'?{ok:false}:{ok:true,json:async()=>({type:'answer',sdp:'answer'})},
 };
 scope.window={isSecureContext:true,AudioContext:Context,AudioWorkletNode:Node,WebSocket:Socket,addEventListener(){}};
 vm.createContext(scope);vm.runInContext(source,scope);
 return{scope,nodes,get,Socket,Peer,read:expression=>vm.runInContext(expression,scope)};
}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 const good=setup();await good.read('start()');
 good.Socket.last.onmessage({data:JSON.stringify({type:'format',version:1,codec:'pcm_s16le',channels:2,sampleRate:48000})});
 assert.equal(good.read('phase'),'live_listen');assert.match(good.read('transportInfo'),/1.536 Mb/);
 assert.match(good.get('mode-badge').textContent,/Lossless PCM/);
 assert.ok(!good.nodes.has('best-mode'));
 assert.equal(good.Socket.last.sent.type,'ready');
 good.read('pcmSession.node.port.onmessage({data:{bufferMs:80,underruns:1}})');
 assert.equal(good.Socket.last.sent.type,'stats');assert.equal(good.Socket.last.sent.bufferMs,80);
 const context=good.read('pcmSession.context');await good.read('start()');
 assert.equal(good.read('phase'),'ready');assert.ok(context.closed&&good.Socket.last.closed);
 assert.match(good.get('mode-badge').textContent,/Not connected/);
 const forced=setup();forced.get('quality').value='pcm';await forced.read('start()');forced.Socket.last.onerror();
 assert.equal(forced.read('phase'),'error');assert.equal(forced.read('pc'),null);
 const auto=setup();await auto.read('start()');auto.Socket.last.onerror();await tick();
 assert.ok(auto.Peer.last);assert.match(auto.read('fallbackReason'),/PCM/);assert.match(auto.read('transportInfo'),/Opus/);
 assert.match(auto.get('mode-badge').textContent,/Negotiating/);
 auto.Peer.last.connectionState='connected';auto.Peer.last.connectionstatechange();
 assert.match(auto.get('mode-badge').textContent,/Lossy Opus/);
 auto.read('cleanup()');
 const remote=setup();await remote.read('start()');const old=remote.Socket.last;
 remote.read("applyQuality({quality:'opus',revision:2})");await tick();
 assert.ok(old.closed&&remote.Peer.last);
 assert.equal(remote.get('quality').value,'opus');
 remote.read("applyQuality({quality:'auto',revision:1})");
 assert.equal(remote.get('quality').value,'opus','Ignore stale sync responses');
 remote.read('cleanup()');
 const manual=setup();manual.scope.fetch=async url=>({ok:true,json:async()=>url==='/ui/quality'?{quality:'pcm',revision:3}:{type:'answer',sdp:'answer'}});
 manual.get('quality').value='pcm';await manual.read('changeQuality()');
 assert.equal(manual.read('selectedQuality'),'pcm');assert.ok(!manual.get('quality').disabled);
 assert.equal(manual.get('quality-pcm').attributes['aria-checked'],'true');
 const segmented=setup();let written;
 segmented.scope.fetch=async(url,options)=>{written=JSON.parse(options.body).quality;return{ok:true,json:async()=>({quality:written,revision:4})};};
 segmented.get('quality-opus').handlers.click();await tick();
 assert.equal(written,'opus');assert.equal(segmented.read('selectedQuality'),'opus');
 assert.equal(segmented.get('quality-opus').attributes['aria-checked'],'true');
 segmented.get('quality-opus').handlers.keydown({key:'Home',preventDefault(){}});await tick();
 assert.equal(written,'auto');assert.ok(segmented.get('quality-auto').focused);
 const rejected=setup();rejected.scope.fetch=async()=>({ok:false,status:403});rejected.get('quality').value='pcm';await rejected.read('changeQuality()');
 assert.equal(rejected.get('quality').value,'auto');assert.match(rejected.read('qualityError'),/403/);
 const cancelled=setup();let release;
 cancelled.scope.AudioContext.prototype.resume=()=>new Promise(resolve=>{release=resolve;});
 const pending=cancelled.read('start()');await tick();cancelled.read('cleanup()');release();await pending;
 assert.equal(cancelled.Socket.last,undefined);
 const insecure=setup();insecure.scope.window.isSecureContext=false;await insecure.read('start()');await tick();
 assert.ok(insecure.Peer.last);assert.match(insecure.read('fallbackReason'),/HTTPS/);insecure.read('cleanup()');
 console.log('PASS: PCM negotiation, stop, forced-mode errors, visible Opus fallback, cancellation, insecure-context fallback');
})().catch(error=>{console.error(error);process.exitCode=1;});

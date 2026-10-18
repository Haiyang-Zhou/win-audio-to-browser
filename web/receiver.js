"use strict";
const $ = id => document.getElementById(id);
const player = $('player'), startBtn = $('start');
const fallback = {hero:'Sound, a little closer.',intro:'Bring your computer’s sound to the device beside you.',listen:'Listen',mic:'Microphone',listen_hint:'Play your computer’s audio on this device.',mic_hint:'Send this device’s microphone to your computer.',secure_hint:'Microphone access requires HTTPS and your permission.',ready:'Ready to connect',connecting:'Connecting…',live_listen:'Receiving computer audio',live_mic:'Microphone is live',disconnected:'Disconnected. You can reconnect.',blocked:'Tap the button to allow audio playback',error:'Connection failed: {error}',sync:'Follows desktop',local:'Local network only',buffer:'Playback buffer',loss:'Packets lost / sec',note:'Buffer is browser-side only, not total latency. Keep this page in front; locking the screen may interrupt audio.',device:'This device',private:'Your sound stays on your local network.',play:'Start listening',enable_mic:'Enable microphone',stop:'Disconnect',sending:'Packets sent / sec',offline:'Desktop settings are temporarily unavailable',unsupported:'WebRTC is unavailable. Use a current Safari, Chrome, Edge or Firefox.',details:'Connection details'};
let messages=fallback, language='en', languageLabel='English', syncOK=true;
let pc=null, micStream=null, statsTimer=null, previous=null, wakeLock=null;
let mode='listen', phase='ready', errorText='', generation=0, playbackBlocked=false, offerAbort=null;
const micSupported=window.isSecureContext && !!navigator.mediaDevices?.getUserMedia;
const rtcSupported=typeof RTCPeerConnection!=='undefined';
const ua=navigator.userAgent;
const deviceKind=/iPad/.test(ua)||(/Macintosh/.test(ua)&&navigator.maxTouchPoints>1)?'iPad':/iPhone/.test(ua)?'iPhone':/Android/.test(ua)?'Android':/Windows/.test(ua)?'Windows':/Macintosh/.test(ua)?'Mac':'Browser';
$('device-kind').textContent=deviceKind;
let deviceId='';
try{deviceId=localStorage.getItem('audio-link-device-id')||'';if(!/^[a-f0-9]{32}$/.test(deviceId)){deviceId=Array.from(crypto.getRandomValues(new Uint8Array(16)),byte=>byte.toString(16).padStart(2,'0')).join('');localStorage.setItem('audio-link-device-id',deviceId);}}catch(_){deviceId='';}
function t(key,values={}){return(messages[key]||fallback[key]||key).replace(/\{(\w+)\}/g,(_,name)=>String(values[name]??''));}
function render(){
 document.documentElement.lang=language;
 document.querySelectorAll('[data-i18n]').forEach(node=>{node.textContent=t(node.dataset.i18n);});
 $('language-label').textContent=syncOK?`${t('sync')} · ${languageLabel}`:t('offline');$('language-label').parentElement.title=$('language-label').textContent;
 $('status').textContent=phase==='error'?t('error',{error:errorText}):t(phase);
 $('hint').textContent=t(mode==='listen'?'listen_hint':micSupported?'mic_hint':'secure_hint');
 $('button-label').textContent=t(phase==='blocked'?'play':pc?'stop':mode==='listen'?'play':'enable_mic');
 $('button-icon').innerHTML=pc&&phase!=='blocked'?'<path d="M7 7h10v10H7z"/>':'<path d="m9 5 10 7-10 7Z"/>';
 $('packet-label').textContent=t(mode==='listen'?'loss':'sending');
 for(const next of ['listen','mic']){const button=$('mode-'+next);button.setAttribute('aria-selected',String(mode===next));button.disabled=!!pc;}
 document.body.dataset.state=phase;startBtn.disabled=!rtcSupported;if(!rtcSupported)$('status').textContent=t('unsupported');
}
function setPhase(next,detail=''){phase=next;errorText=detail;render();}
let syncing=false;
async function syncLanguage(){
 if(syncing)return;syncing=true;const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),3500);
 try{const response=await fetch('/ui',{cache:'no-store',signal:controller.signal});if(!response.ok)throw Error(String(response.status));const data=await response.json();if(typeof data.language!=='string'||!data.messages||Object.keys(fallback).some(key=>typeof data.messages[key]!=='string'))throw Error('Invalid translations');language=data.language;languageLabel=data.languageLabel||language;messages=data.messages;syncOK=true;}catch(_){syncOK=false;}finally{clearTimeout(timer);syncing=false;render();}
}
function stopStats(){clearInterval(statsTimer);statsTimer=null;previous=null;$('buffer').textContent='—';$('packets').textContent='—';}
function startStats(connection){
 stopStats();statsTimer=setInterval(async()=>{
  if(pc!==connection||connection.connectionState!=='connected')return;
  try{const report=await connection.getStats();if(pc!==connection)return;report.forEach(entry=>{
   if(entry.type!==(mode==='listen'?'inbound-rtp':'outbound-rtp')||(entry.kind||entry.mediaType)!=='audio')return;
   if(previous){const elapsed=(entry.timestamp-previous.timestamp)/1000;if(elapsed>0){const count=entry.jitterBufferEmittedCount-previous.jitterBufferEmittedCount,delay=entry.jitterBufferDelay-previous.jitterBufferDelay;if(mode==='listen'&&count>0&&Number.isFinite(delay))$('buffer').textContent=Math.round(delay/count*1000)+' ms';const packets=mode==='listen'?Math.max(0,(entry.packetsLost||0)-(previous.packetsLost||0)):entry.packetsSent-previous.packetsSent;if(Number.isFinite(packets))$('packets').textContent=Math.round(packets/elapsed);}}previous=entry;
  });}catch(_){}
 },1000);
}
function cleanup(){
 generation++;offerAbort?.abort();offerAbort=null;const connection=pc;pc=null;connection?.close();
 if(micStream){micStream.getTracks().forEach(track=>track.stop());micStream=null;}
 player.pause();player.srcObject=null;if(wakeLock){wakeLock.release().catch(()=>{});wakeLock=null;}playbackBlocked=false;stopStats();
}
async function keepAwake(){try{const active=pc;if(active?.connectionState==='connected'&&!wakeLock){const lock=await navigator.wakeLock.request('screen');if(pc!==active){await lock.release();return;}wakeLock=lock;lock.addEventListener('release',()=>{if(wakeLock===lock)wakeLock=null;});}}catch(_){}}
function waitForIce(connection){
 if(connection.iceGatheringState==='complete')return Promise.resolve();
 return new Promise((resolve,reject)=>{const finish=error=>{clearTimeout(timer);connection.removeEventListener('icegatheringstatechange',check);error?reject(error):resolve();};const check=()=>{if(connection.iceGatheringState==='complete')finish();else if(connection.signalingState==='closed')finish(Error('Connection cancelled'));};const timer=setTimeout(()=>finish(Error('Network negotiation timed out')),8000);connection.addEventListener('icegatheringstatechange',check);});
}
async function start(){
 if(phase==='blocked'&&pc){try{await player.play();playbackBlocked=false;setPhase('live_listen');}catch(_){setPhase('blocked');}return;}
 if(pc){cleanup();setPhase('ready');return;}if(!rtcSupported)return;
 const current=++generation;let connection;try{connection=new RTCPeerConnection({iceServers:[]});}catch(error){setPhase('error',error.message);return;}pc=connection;setPhase('connecting');
 const stillCurrent=()=>current===generation&&pc===connection;
 const fail=error=>{if(stillCurrent()){cleanup();setPhase('error',error?.message||String(error));}};
 connection.addEventListener('connectionstatechange',()=>{if(!stillCurrent())return;if(connection.connectionState==='connected'){setPhase(playbackBlocked?'blocked':'live_'+mode);startStats(connection);keepAwake();}else if(['failed','disconnected','closed'].includes(connection.connectionState)){cleanup();setPhase('disconnected');}});
 try{
  if(mode==='listen'){
   // Keep this call inside the tap gesture to unlock audio on Safari.
   player.play().catch(()=>{});const receiver=connection.addTransceiver('audio',{direction:'recvonly'}).receiver;
   try{if('playoutDelayHint'in receiver)receiver.playoutDelayHint=0;if('jitterBufferTarget'in receiver)receiver.jitterBufferTarget=0;}catch(_){}
   connection.addEventListener('track',event=>{if(!stillCurrent())return;player.srcObject=event.streams[0]||new MediaStream([event.track]);player.play().catch(()=>{if(stillCurrent()){playbackBlocked=true;setPhase('blocked');}});});
  }else{
   if(!micSupported)throw Error(t('secure_hint'));
   const stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:false,noiseSuppression:true,autoGainControl:true}});
   if(!stillCurrent()){stream.getTracks().forEach(track=>track.stop());return;}micStream=stream;stream.getAudioTracks().forEach(track=>connection.addTransceiver(track,{direction:'sendonly'}));
  }
  await connection.setLocalDescription(await connection.createOffer());await waitForIce(connection);if(!stillCurrent())return;
  const controller=new AbortController();offerAbort=controller;const timeout=setTimeout(()=>controller.abort(),12000);let answer;
  try{const response=await fetch(mode==='mic'?'/mic-offer':'/offer',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({sdp:connection.localDescription.sdp,type:connection.localDescription.type,deviceId,deviceKind})});if(!response.ok)throw Error('HTTP '+response.status);answer=await response.json();}finally{clearTimeout(timeout);}
  if(!stillCurrent())return;await connection.setRemoteDescription(answer);
 }catch(error){fail(error);}
}
for(const next of ['listen','mic'])$('mode-'+next).addEventListener('click',()=>{if(!pc){mode=next;render();}});
startBtn.addEventListener('click',start);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'){syncLanguage();keepAwake();}});window.addEventListener('pagehide',cleanup);
render();syncLanguage();setInterval(syncLanguage,2000);

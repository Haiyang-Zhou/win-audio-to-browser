"use strict";
const $ = id => document.getElementById(id);
const player = $('player'), startBtn = $('start');
const fallback = {hero:'Sound, a little closer.',intro:'Bring your computer’s sound to the device beside you.',listen:'Listen',mic:'Microphone',listen_hint:'Play your computer’s audio on this device.',mic_hint:'Send this device’s microphone to your computer.',secure_hint:'Microphone access requires HTTPS and your permission.',ready:'Ready to connect',connecting:'Connecting…',live_listen:'Receiving computer audio',live_mic:'Microphone is live',disconnected:'Disconnected. You can reconnect.',blocked:'Tap the button to allow audio playback',error:'Connection failed: {error}',sync:'Follows desktop',local:'Local network only',buffer:'Playback buffer',loss:'Packets lost / sec',note:'Buffer is browser-side only, not total latency. Keep this page in front; locking the screen may interrupt audio.',device:'This device',private:'Your sound stays on your local network.',play:'Start listening',enable_mic:'Enable microphone',stop:'Disconnect',sending:'Packets sent / sec',offline:'Desktop settings are temporarily unavailable',unsupported:'WebRTC is unavailable. Use a current Safari, Chrome, Edge or Firefox.',details:'Connection details'};
let messages=fallback, language='en', languageLabel='English', syncOK=true;
Object.assign(fallback,{quality:'Audio transport',quality_auto:'Auto (lossless first)',quality_pcm:'Lossless PCM',quality_opus:'Compatible Opus',underruns:'Playback underruns',fallback_notice:'Fell back to lossy Opus',pcm_requires:'Lossless requires HTTPS and an AudioWorklet-capable browser',resampled:'Playback resampled to'});
Object.assign(fallback,{quality_short_auto:'Auto',quality_short_pcm:'PCM',quality_short_opus:'Opus'});
let pc=null, micStream=null, statsTimer=null, previous=null, wakeLock=null;
let pcmSession=null, transportInfo='', fallbackReason='';
let actualTransport='';
let selectedQuality='auto',settingsRevision=-1,qualitySaving=false,qualityError='',rtcSessionId='',statsPosting=false;
Object.assign(fallback,{audio_current:'Current mode',audio_pcm:'Lossless PCM',audio_opus:'Lossy Opus',audio_idle:'Not connected',audio_pending:'Negotiating',audio_unknown:'Unknown mode',audio_mixed:'Mixed modes'});
function pcmSupported(){return window.isSecureContext&&!!window.AudioContext&&!!window.AudioWorkletNode&&!!window.WebSocket;}
function audioFormat(format){return `${format.bits}-bit / ${format.sampleRate/1000} kHz / ${format.channels} ch`;}
$('quality').value='auto';
function applyQuality(data){
 if(qualitySaving||!['auto','pcm','opus'].includes(data.quality)||!Number.isSafeInteger(data.revision)||data.revision<settingsRevision)return;
 const changed=selectedQuality!==data.quality;
 selectedQuality=data.quality;settingsRevision=data.revision;$('quality').value=selectedQuality;
 if(changed&&active()&&mode==='listen'){cleanup();fallbackReason='';setPhase('ready');start();}
}
async function changeQuality(){
 const requested=$('quality').value;qualitySaving=true;qualityError='';render();
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),5000);
 try{
  const response=await fetch('/ui/quality',{method:'POST',headers:{'Content-Type':'application/json','X-Audio-Link':'1'},body:JSON.stringify({quality:requested}),signal:controller.signal});
  if(!response.ok)throw Error('HTTP '+response.status);
  const result=await response.json();qualitySaving=false;applyQuality(result);
 }catch(error){$('quality').value=selectedQuality;syncOK=false;qualityError=error.message;}
 finally{clearTimeout(timer);qualitySaving=false;render();}
}
function chooseQuality(quality){
 if(qualitySaving||quality===$('quality').value)return;
 $('quality').value=quality;changeQuality();
}
async function reportStats(data){
 if(pcmSession?.ws?.readyState===1){pcmSession.ws.send(JSON.stringify({type:'stats',...data}));return;}
 if(!rtcSessionId||statsPosting)return;
 statsPosting=true;const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),1500);
 try{await fetch('/diagnostics',{method:'POST',headers:{'Content-Type':'application/json','X-Audio-Link':'1'},body:JSON.stringify({sessionId:rtcSessionId,...data}),signal:controller.signal});}catch(_){}
 finally{clearTimeout(timer);statsPosting=false;}
}
function active(){return !!(pc||pcmSession);}
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
 $('button-label').textContent=t(phase==='blocked'?'play':active()?'stop':mode==='listen'?'play':'enable_mic');
 $('button-icon').innerHTML=active()&&phase!=='blocked'?'<path d="M7 7h10v10H7z"/>':'<path d="m9 5 10 7-10 7Z"/>';
 $('packet-label').textContent=t(pcmSession?'underruns':mode==='listen'?'loss':'sending');
 $('quality-control').hidden=mode!=='listen';$('quality').disabled=qualitySaving;
 const qualityOptions=['auto','pcm','opus'];
 $('quality-segments').style.setProperty('--quality-index',Math.max(0,qualityOptions.indexOf($('quality').value)));
 $('quality-segments').setAttribute('aria-busy',String(qualitySaving));
 for(const quality of qualityOptions){const option=$('quality-'+quality),checked=$('quality').value===quality;option.setAttribute('aria-checked',String(checked));option.setAttribute('aria-label',t('quality_'+quality));option.setAttribute('aria-disabled',String(qualitySaving));option.title=t('quality_'+quality);option.tabIndex=checked?0:-1;}
 const modeKey=actualTransport?'audio_'+actualTransport:active()?'audio_pending':'audio_idle';
 $('mode-badge').textContent=t(modeKey);$('mode-badge').dataset.transport=actualTransport;
 if(pcmSession?.format){const format=pcmSession.format;transportInfo=`PCM · ${audioFormat(format)} · ${(format.sampleRate*format.channels*16/1e6).toFixed(3)} Mb/s`;if(pcmSession.context.sampleRate!==format.sampleRate)transportInfo+=` · ${t('resampled')} ${pcmSession.context.sampleRate/1000} kHz`;}
 $('transport-info').textContent=[qualityError?t('error',{error:qualityError}):'',fallbackReason?t('fallback_notice')+': '+fallbackReason:'',transportInfo].filter(Boolean).join(' · ');
 for(const next of ['listen','mic']){const button=$('mode-'+next);button.setAttribute('aria-selected',String(mode===next));button.disabled=active();}
 document.body.dataset.state=phase;startBtn.disabled=qualitySaving||(mode==='mic'&&!rtcSupported);
}
function setPhase(next,detail=''){phase=next;errorText=detail;render();}
let syncing=false;
async function syncLanguage(){
 if(syncing)return;syncing=true;const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),3500);
 try{const response=await fetch('/ui',{cache:'no-store',signal:controller.signal});if(!response.ok)throw Error(String(response.status));const data=await response.json();if(typeof data.language!=='string'||!data.messages||Object.keys(fallback).some(key=>typeof data.messages[key]!=='string'))throw Error('Invalid translations');language=data.language;languageLabel=data.languageLabel||language;messages=data.messages;applyQuality(data);syncOK=true;}catch(_){syncOK=false;}finally{clearTimeout(timer);syncing=false;render();}
}
function stopStats(){clearInterval(statsTimer);statsTimer=null;previous=null;$('buffer').textContent='—';$('packets').textContent='—';}
function startStats(connection){
 stopStats();statsTimer=setInterval(async()=>{
  if(pc!==connection||connection.connectionState!=='connected')return;
  try{const report=await connection.getStats();if(pc!==connection)return;report.forEach(entry=>{
   if(entry.type!==(mode==='listen'?'inbound-rtp':'outbound-rtp')||(entry.kind||entry.mediaType)!=='audio')return;
   if(previous){const elapsed=(entry.timestamp-previous.timestamp)/1000;if(elapsed>0){const count=entry.jitterBufferEmittedCount-previous.jitterBufferEmittedCount,delay=entry.jitterBufferDelay-previous.jitterBufferDelay;const bufferMs=mode==='listen'&&count>0&&Number.isFinite(delay)?delay/count*1000:undefined;if(bufferMs!==undefined)$('buffer').textContent=Math.round(bufferMs)+' ms';const packets=mode==='listen'?Math.max(0,(entry.packetsLost||0)-(previous.packetsLost||0)):entry.packetsSent-previous.packetsSent;if(Number.isFinite(packets))$('packets').textContent=Math.round(packets/elapsed);reportStats({bufferMs,packets:packets/elapsed});}}previous=entry;
  });}catch(_){}
 },1000);
}
function cleanup(){
 const oldPcm=pcmSession;pcmSession=null;
 if(oldPcm){clearTimeout(oldPcm.timer);oldPcm.ws?.close();oldPcm.node?.disconnect();oldPcm.context.close().catch(()=>{});}
 transportInfo='';actualTransport='';rtcSessionId='';
 generation++;offerAbort?.abort();offerAbort=null;const connection=pc;pc=null;connection?.close();
 if(micStream){micStream.getTracks().forEach(track=>track.stop());micStream=null;}
 player.pause();player.srcObject=null;if(wakeLock){wakeLock.release().catch(()=>{});wakeLock=null;}playbackBlocked=false;stopStats();
}
async function keepAwake(){try{const connection=pc||pcmSession;if(connection&&(phase==='live_listen'||phase==='live_mic')&&!wakeLock){const lock=await navigator.wakeLock.request('screen');if((pc||pcmSession)!==connection){await lock.release();return;}wakeLock=lock;lock.addEventListener('release',()=>{if(wakeLock===lock)wakeLock=null;});}}catch(_){}}
function waitForIce(connection){
 if(connection.iceGatheringState==='complete')return Promise.resolve();
 return new Promise((resolve,reject)=>{const finish=error=>{clearTimeout(timer);connection.removeEventListener('icegatheringstatechange',check);error?reject(error):resolve();};const check=()=>{if(connection.iceGatheringState==='complete')finish();else if(connection.signalingState==='closed')finish(Error('Connection cancelled'));};const timer=setTimeout(()=>finish(Error('Network negotiation timed out')),8000);connection.addEventListener('icegatheringstatechange',check);});
}
async function startRtc(){
 if(phase==='blocked'&&pc){try{await player.play();playbackBlocked=false;setPhase('live_listen');}catch(_){setPhase('blocked');}return;}
 if(pc){cleanup();setPhase('ready');return;}if(!rtcSupported)return;
 const current=++generation;let connection;try{connection=new RTCPeerConnection({iceServers:[]});}catch(error){setPhase('error',error.message);return;}pc=connection;setPhase('connecting');
 transportInfo=mode==='mic'?'Opus · 48 kHz':'Opus · 48 kHz · 96 kb/s';render();
 const stillCurrent=()=>current===generation&&pc===connection;
 const fail=error=>{if(stillCurrent()){cleanup();setPhase('error',error?.message||String(error));}};
 connection.addEventListener('connectionstatechange',()=>{if(!stillCurrent())return;if(connection.connectionState==='connected'){actualTransport='opus';setPhase(playbackBlocked?'blocked':'live_'+mode);startStats(connection);keepAwake();}else if(['failed','disconnected','closed'].includes(connection.connectionState)){cleanup();setPhase('disconnected');}});
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
  try{const response=await fetch(mode==='mic'?'/mic-offer':'/offer',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({sdp:connection.localDescription.sdp,type:connection.localDescription.type,deviceId,deviceKind})});if(!response.ok)throw Error('HTTP '+response.status);answer=await response.json();if(stillCurrent())rtcSessionId=response.headers?.get('X-Audio-Session')||'';}finally{clearTimeout(timeout);}
  if(!stillCurrent())return;await connection.setRemoteDescription(answer);
 }catch(error){fail(error);}
}
async function start(){
 if(phase==='blocked'&&pc){await startRtc();return;}
 if(phase==='blocked'&&pcmSession){const pending=pcmSession;try{await pending.context.resume();if(pcmSession===pending&&pending.context.state==='running')setPhase(pending.node?'live_listen':'connecting');}catch(_){}return;}
 if(active()){cleanup();fallbackReason='';setPhase('ready');return;}
 fallbackReason='';
 if(mode==='mic'||$('quality').value==='opus'){if(!rtcSupported){setPhase('error',t('unsupported'));return;}await startRtc();return;}
 const auto=$('quality').value==='auto';
 const fallbackToOpus=reason=>{
  cleanup();
  if(auto&&rtcSupported){fallbackReason=reason;startRtc();}
  else setPhase('error',reason);
 };
 if(!pcmSupported()){fallbackToOpus(t('pcm_requires'));return;}
 let context;
 try{context=new AudioContext({latencyHint:'interactive'});}catch(error){fallbackToOpus(error.message);return;}
 const session={context,ws:null,node:null,timer:null};pcmSession=session;
 const current=++generation,valid=()=>pcmSession===session&&current===generation;
 const fail=error=>{if(valid())fallbackToOpus(error?.message||String(error));};
 setPhase('connecting');
 // Resume synchronously from the user's tap, before fetching the worklet.
 const resumed=context.resume().then(()=>null,error=>error);
 if(context.state!=='running')setPhase('blocked');
 context.onstatechange=()=>{if(valid()&&session.node)setPhase(context.state==='running'?'live_listen':'blocked');};
 try{
  if(!context.audioWorklet)throw Error(t('pcm_requires'));
  await context.audioWorklet.addModule('/pcm-worklet.js');if(!valid())return;
  const resumeError=await resumed;if(!valid())return;if(resumeError)throw resumeError;
  session.timer=setTimeout(()=>fail(Error('PCM handshake timed out')),10000);
  const url=new URL('/pcm',location.href);url.protocol=location.protocol==='https:'?'wss:':'ws:';url.search=new URLSearchParams({deviceId,deviceKind});
  const ws=session.ws=new WebSocket(url);ws.binaryType='arraybuffer';
  ws.onmessage=event=>{
   if(!valid())return;
   try{
    if(typeof event.data==='string'){
     if(session.node)throw Error('Duplicate PCM format');
     const format=JSON.parse(event.data);
     if(format.type!=='format'||format.version!==1||format.codec!=='pcm_s16le'||![1,2].includes(format.channels)||!Number.isInteger(format.sampleRate)||format.sampleRate<8000||format.sampleRate>192000)throw Error('Unsupported PCM format');
     format.bits=16;session.format=format;
     const node=session.node=new AudioWorkletNode(context,'pcm-receiver',{numberOfInputs:0,numberOfOutputs:1,outputChannelCount:[format.channels],processorOptions:{channels:format.channels,sourceRate:format.sampleRate}});
     node.port.onmessage=message=>{if(!valid())return;const data=message.data;if(data.error){fail(Error(data.error));return;}$('buffer').textContent=Math.round(data.bufferMs)+' ms';$('packets').textContent=String(data.underruns);reportStats({bufferMs:data.bufferMs,underruns:data.underruns});};
     node.onprocessorerror=()=>fail(Error('PCM audio processor failed'));node.connect(context.destination);
     actualTransport='pcm';
     ws.send(JSON.stringify({type:'ready',outputSampleRate:context.sampleRate}));
     clearTimeout(session.timer);setPhase(context.state==='running'?'live_listen':'blocked');keepAwake();
    }else{
     if(!session.node)throw Error('PCM audio before format');
     session.node.port.postMessage(event.data,[event.data]);
    }
   }catch(error){fail(error);}
  };
  ws.onerror=()=>fail(Error('PCM connection unavailable'));
  ws.onclose=event=>fail(Error(event.reason||'PCM connection closed'));
 }catch(error){fail(error);}
}
for(const next of ['listen','mic'])$('mode-'+next).addEventListener('click',()=>{if(!active()){mode=next;transportInfo='';fallbackReason='';render();}});
$('quality').addEventListener('change',changeQuality);
for(const [index,quality] of ['auto','pcm','opus'].entries()){
 const option=$('quality-'+quality);
 option.addEventListener('click',()=>chooseQuality(quality));
 option.addEventListener('keydown',event=>{
  const directions={ArrowLeft:-1,ArrowUp:-1,ArrowRight:1,ArrowDown:1};let next;
  if(event.key in directions)next=(index+directions[event.key]+3)%3;
  else if(event.key==='Home')next=0;else if(event.key==='End')next=2;else return;
  event.preventDefault();if(qualitySaving)return;
  const target=['auto','pcm','opus'][next];$('quality-'+target).focus();chooseQuality(target);
 });
}
startBtn.addEventListener('click',start);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'){syncLanguage();keepAwake();}});window.addEventListener('pagehide',cleanup);
render();syncLanguage();setInterval(syncLanguage,2000);

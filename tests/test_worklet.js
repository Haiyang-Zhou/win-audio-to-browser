"use strict";
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
let Processor;
const scope={sampleRate:48000,Float32Array,DataView,Math,Number,
 AudioWorkletProcessor:class{constructor(){this.events=[];this.port={postMessage:data=>this.events.push(data)};}},
 registerProcessor:(_,value)=>{Processor=value;}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../web/pcm-worklet.js'),'utf8'),scope);
function send(processor,frames,channels){
 const data=new ArrayBuffer(frames*channels*2),view=new DataView(data);
 for(let i=0;i<frames*channels;i++)view.setInt16(i*2,(i%65536)-32768,true);
 processor.port.onmessage({data});
}
for(const channels of [1,2]){
 const p=new Processor({processorOptions:{channels,sourceRate:48000}});
 send(p,8192,channels);
 let frame=0;
 for(let block=0;block<60;block++){
  const output=Array.from({length:channels},()=>new Float32Array(128));
  p.process([], [output]);
  for(let i=0;i<128;i++,frame++)for(let ch=0;ch<channels;ch++)
   assert.equal(output[ch][i],(((frame*channels+ch)%65536)-32768)/32768);
 }
 assert.equal(p.underruns,0);
 for(let i=0;i<10;i++)p.process([], [Array.from({length:channels},()=>new Float32Array(128))]);
 assert.equal(p.underruns,1);
 const overflow=new Processor({processorOptions:{channels,sourceRate:48000}});
 send(overflow,24001,channels);
 assert.ok(overflow.failed&&overflow.events[0].error);
}
const resampled=new Processor({processorOptions:{channels:1,sourceRate:24000}});
send(resampled,4096,1);
const output=[new Float32Array(128)];resampled.process([], [output]);
assert.equal(resampled.size,4096-64);
assert.equal(output[0][1],(-32768+0.5)/32768);
console.log('PASS: PCM mono/stereo exact samples, ring boundaries, underruns, overflow, rate conversion');

/* Bounded stereo/mono s16le ring; no codec, gain adjustment or silent dropping. */
class PcmReceiver extends AudioWorkletProcessor {
 constructor(options) {
  super();
  const {channels, sourceRate}=options.processorOptions;
  this.channels=channels; this.ratio=sourceRate/sampleRate;
  this.capacity=Math.ceil(sourceRate/2); this.ring=new Float32Array(this.capacity*channels);
  this.read=0; this.write=0; this.size=0; this.fraction=0;
  this.target=Math.ceil(sourceRate*0.08); this.started=false; this.failed=false;
  this.underruns=0; this.ticks=0;
  this.port.onmessage=event=>{
   if(this.failed)return;
   const data=new DataView(event.data), frames=data.byteLength/(2*channels);
   if(!Number.isInteger(frames)||frames+this.size>this.capacity){this.failed=true;this.port.postMessage({error:'PCM playback buffer overflow'});return;}
   for(let frame=0;frame<frames;frame++){
    for(let ch=0;ch<channels;ch++)this.ring[this.write*channels+ch]=data.getInt16((frame*channels+ch)*2,true)/32768;
    this.write=(this.write+1)%this.capacity;
   }
   this.size+=frames;
  };
 }
 process(_,outputs) {
  const output=outputs[0];
  if(this.failed)return true;
  if(!this.started&&this.size>=this.target)this.started=true;
  if(this.started){
   for(let i=0;i<output[0].length;i++){
    const advance=Math.floor(this.fraction+this.ratio);
    if(this.size<Math.max(2,advance+1)){this.started=false;this.underruns++;break;}
    for(let ch=0;ch<output.length;ch++){
     const a=this.ring[this.read*this.channels+ch];
     // Exact sample values at equal rates; linear interpolation only if rates differ.
     const b=this.ring[((this.read+1)%this.capacity)*this.channels+ch];
     output[ch][i]=a+(b-a)*this.fraction;
    }
    this.fraction+=this.ratio;this.fraction-=advance;
    this.read=(this.read+advance)%this.capacity;this.size-=advance;
   }
  }
  if(++this.ticks>=Math.ceil(sampleRate/output[0].length)){
   this.ticks=0;this.port.postMessage({bufferMs:this.size/sampleRate/this.ratio*1000,underruns:this.underruns});
  }
  return true;
 }
}
registerProcessor('pcm-receiver',PcmReceiver);

(() => {
  const root = document.querySelector('.karka-bot-root');
  if (!root) return;
  const launcher = document.getElementById('karkaBotLauncher');
  const panel = document.getElementById('karkaBotPanel');
  const close = document.getElementById('karkaBotClose');
  const backdrop = document.getElementById('karkaBotBackdrop');
  const form = document.getElementById('karkaBotForm');
  const input = document.getElementById('karkaBotInput');
  const send = document.getElementById('karkaBotSend');
  const messages = document.getElementById('karkaBotMessages');
  const suggestions = document.getElementById('karkaBotSuggestions');
  const language = document.getElementById('karkaBotLanguage');
  const mic = document.getElementById('karkaBotMic');
  const micText = document.getElementById('karkaBotMicText');
  const voiceState = document.getElementById('karkaBotVoiceState');
  const chars = document.getElementById('karkaBotChars');
  const endpoint = root.dataset.chatEndpoint;
  let recognition = null;
  let recording = false;
  let speaking = false;
  let selectedVoice = null;

  const LANGS = { 'en-IN':'en-IN','ta-IN':'ta-IN','hi-IN':'hi-IN','ml-IN':'ml-IN','te-IN':'te-IN','kn-IN':'kn-IN','mr-IN':'mr-IN','bn-IN':'bn-IN' };

  function openBot() {
    panel.classList.add('is-open'); panel.setAttribute('aria-hidden','false'); launcher.setAttribute('aria-expanded','true');
    setTimeout(() => input.focus(), 220);
  }
  function closeBot() {
    panel.classList.remove('is-open'); panel.setAttribute('aria-hidden','true'); launcher.setAttribute('aria-expanded','false');
    if (recording) stopRecording();
    if (speaking && 'speechSynthesis' in window) speechSynthesis.cancel();
  }
  launcher?.addEventListener('click', openBot); close?.addEventListener('click', closeBot); backdrop?.addEventListener('click', closeBot);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && panel.classList.contains('is-open')) closeBot(); });

  function addMessage(text, who='bot', meta='') {
    const wrap = document.createElement('div'); wrap.className = `karka-bot-message ${who}`;
    if (who === 'bot') {
      wrap.innerHTML = `<div class="bot-mark">✦</div><div><p></p>${meta ? `<small>${escapeHtml(meta)}</small>` : ''}</div>`;
    } else wrap.innerHTML = `<div><p></p>${meta ? `<small>${escapeHtml(meta)}</small>` : ''}</div>`;
    renderText(wrap.querySelector('p'), text);
    messages.appendChild(wrap); scrollMessages(); return wrap;
  }
  // Shows text safely (no HTML injection) and turns http(s) links, e.g. the Google Maps pin, into tappable links.
  function renderText(el, text) {
    const parts = String(text).split(/(https?:\/\/[^\s]+)/g);
    parts.forEach(part => {
      if (/^https?:\/\//.test(part)) {
        const a = document.createElement('a');
        a.href = part; a.textContent = 'Open in Google Maps ↗'.length && /maps\./.test(part) ? 'Open in Google Maps ↗' : part;
        a.target = '_blank'; a.rel = 'noopener noreferrer';
        el.appendChild(a);
      } else el.appendChild(document.createTextNode(part));
    });
  }
  function addTyping() {
    const wrap = document.createElement('div'); wrap.className='karka-bot-message bot';
    wrap.innerHTML='<div class="bot-mark">✦</div><div><p class="karka-bot-typing"><i></i><i></i><i></i></p></div>';
    messages.appendChild(wrap); scrollMessages(); return wrap;
  }
  function scrollMessages(){ messages.scrollTop = messages.scrollHeight; }
  function escapeHtml(s){ return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }

  function updateCount(){ chars.textContent = `${input.value.length} / 1200`; input.style.height='auto'; input.style.height=Math.min(input.scrollHeight,110)+'px'; }
  input.addEventListener('input', updateCount); input.addEventListener('keydown', e => { if(e.key==='Enter' && !e.shiftKey){e.preventDefault();form.requestSubmit();} });
  suggestions?.querySelectorAll('button').forEach(btn => btn.addEventListener('click',()=>{input.value=btn.textContent.trim();updateCount();form.requestSubmit();}));

  function voiceFor(lang) {
    if (!('speechSynthesis' in window)) return null;
    const voices = speechSynthesis.getVoices(); if (!voices.length) return null;
    const prefix = lang.split('-')[0].toLowerCase();
    return voices.find(v => v.lang.toLowerCase() === lang.toLowerCase()) || voices.find(v => v.lang.toLowerCase().startsWith(prefix)) || voices.find(v => v.lang.toLowerCase().startsWith('en')) || voices[0];
  }
  if ('speechSynthesis' in window) speechSynthesis.onvoiceschanged = () => { selectedVoice = voiceFor(language.value); };
  language.addEventListener('change',()=>{ selectedVoice = voiceFor(language.value); });

  function speak(text) {
    if (!('speechSynthesis' in window) || !text) return;
    speechSynthesis.cancel(); selectedVoice = selectedVoice || voiceFor(language.value);
    const utter = new SpeechSynthesisUtterance(text); utter.lang=language.value; if(selectedVoice) utter.voice=selectedVoice; utter.rate=.98; utter.pitch=1.02; utter.volume=1;
    speaking=true; utter.onend=()=>{speaking=false}; utter.onerror=()=>{speaking=false}; speechSynthesis.speak(utter);
  }

  // Voice recording: the mic is OFF by default. It records only after the learner taps it,
  // records one question, then switches itself off (tap again to stop earlier).
  function resetMicUI(){
    recording=false; mic.classList.remove('is-listening'); mic.setAttribute('aria-pressed','false');
    micText.textContent='Record'; voiceState.hidden=true; input.placeholder='Ask your doubt…';
  }
  function setupRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return null;
    const r = new SR();
    r.continuous=false; r.interimResults=true; r.maxAlternatives=1;
    r.lang=LANGS[language.value] || language.value;
    let transcript='';
    r.onstart=()=>{
      recording=true; transcript='';
      mic.classList.add('is-listening'); mic.setAttribute('aria-pressed','true');
      micText.textContent='Stop'; voiceState.hidden=false;
    };
    r.onresult=e=>{
      let finalText='', interim='';
      for(let i=e.resultIndex;i<e.results.length;i++){
        const t=e.results[i][0].transcript;
        if(e.results[i].isFinal) finalText+=t; else interim+=t;
      }
      if(finalText) transcript=(transcript+' '+finalText).trim();
      input.placeholder = interim ? interim : 'Recording…';
    };
    r.onerror=e=>{
      if(e.error==='not-allowed'||e.error==='service-not-allowed'){
        addMessage('Microphone access is blocked. Please allow microphone permission in your browser settings, or type your question instead.','bot','Microphone');
      }
    };
    r.onend=()=>{
      const text=transcript.trim();
      resetMicUI(); recognition=null;
      if(text){ input.value=text.slice(0,1200); updateCount(); form.requestSubmit(); }
    };
    return r;
  }
  function startRecording(){
    if('speechSynthesis' in window) speechSynthesis.cancel();   // never record the assistant's own voice
    recognition=setupRecognition();
    if(!recognition){ addMessage('Voice recording is not supported in this browser. You can still type your question.','bot','Tip'); return; }
    try{ recognition.start(); }catch(_){ resetMicUI(); recognition=null; }
  }
  function stopRecording(){ try{ recognition?.stop(); }catch(_){ resetMicUI(); recognition=null; } }
  mic.addEventListener('click',()=> recording ? stopRecording() : startRecording());

  async function sendQuestion(text){
    const clean=text.trim(); if(!clean || send.disabled) return;
    addMessage(clean,'user'); input.value=''; updateCount(); suggestions?.remove();
    const typing=addTyping(); send.disabled=true;
    try{
      const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({message:clean,language:language.value})});
      const data=await response.json(); typing.remove();
      if(!response.ok) throw new Error(data.error || 'The assistant is temporarily unavailable.');
      const answer=data.answer || 'I’m here to help. Please try asking that in another way.';
      addMessage(answer,'bot',data.cached?'Karka AI · instant answer':'Karka AI · AI mentor');
      speak(answer);
    }catch(err){ typing.remove(); addMessage(err.message || 'I could not reach the AI right now. Please try again.','bot','Karka AI · fallback'); }
    finally{ send.disabled=false; input.focus(); }
  }
  form.addEventListener('submit',e=>{e.preventDefault();sendQuestion(input.value);});
})();

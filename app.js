const TOPICS = [
  {topic:"What if Earth stopped spinning for 5 seconds?", hook:"For five seconds, Earth forgets how to spin.", fact:"The equator moves at about 1,670 km/h because of Earth's rotation.", danger:"The ground stops, but oceans, air and loose objects keep moving eastward.", payoff:"It would not feel like a pause. It would feel like the planet became a weapon.", score:96},
  {topic:"What if you dropped a sugar cube of neutron-star matter on Earth?", hook:"Imagine a sugar cube heavier than a mountain.", fact:"Neutron-star matter is extremely dense because atoms are crushed into nuclear-scale material.", danger:"Its gravity and pressure would violently disturb everything nearby.", payoff:"A tiny cube could behave less like an object and more like a disaster.", score:95},
  {topic:"What if the Moon disappeared tonight?", hook:"Tonight the Moon vanishes, and Earth keeps moving.", fact:"The Moon stabilizes Earth's axial tilt and strongly affects ocean tides.", danger:"Tides weaken, nights darken, ecosystems are disrupted and long-term climate stability changes.", payoff:"The sky would look emptier, but the damage would be written into the oceans.", score:92},
  {topic:"What if Jupiter became a second Sun?", hook:"A second sun appears where Jupiter used to be.", fact:"Jupiter is massive but still far too light to become a true star naturally.", danger:"If it somehow ignited, the outer solar system would become brighter, hotter and dynamically unstable.", payoff:"Earth might survive the light, but the solar system would no longer be the same machine.", score:90},
  {topic:"What if a black hole passed through Earth?", hook:"A black hole crosses the planet in silence.", fact:"A small black hole could pass through matter, but its gravity would still pull on nearby material.", danger:"The event would trigger violent seismic and gravitational effects along its path.", payoff:"The scariest part is not the darkness. It is how cleanly gravity can cut.", score:94},
  {topic:"What if Earth had rings like Saturn?", hook:"Look up at night and the sky has a glowing ring across it.", fact:"A ring system would be made of countless small particles orbiting Earth.", danger:"Falling material, satellite damage and altered night brightness would change life and technology.", payoff:"It would be beautiful, but beauty in orbit can still be dangerous.", score:88},
  {topic:"What if the Sun vanished for 8 minutes?", hook:"The Sun disappears, but Earth does not know it immediately.", fact:"Sunlight takes about 8 minutes to reach Earth.", danger:"After the delay, daylight and solar gravity effects would stop arriving together.", payoff:"For 8 minutes, everything looks normal. Then the solar system becomes a mystery.", score:91},
  {topic:"What if a Mars-sized planet hit Earth today?", hook:"A world the size of Mars is coming straight toward Earth.", fact:"A giant impact is one leading idea for how the Moon formed early in Earth's history.", danger:"Today, an impact like that would melt global surfaces and erase modern civilization.", payoff:"Some collisions create moons. Others end worlds.", score:93},
  {topic:"What if humans lived on a rogue planet?", hook:"A planet drifts alone with no star, and humans try to survive on it.", fact:"Rogue planets move through space without orbiting a star.", danger:"Without sunlight, survival would depend on internal heat, nuclear energy or protected underground habitats.", payoff:"The night would never end, but life might still find a way to hide.", score:87},
  {topic:"What if gravity became 10% weaker for one day?", hook:"For one day, gravity loosens its grip.", fact:"Gravity controls weight, tides, orbits and atmospheric behavior.", danger:"People would feel lighter, oceans would shift, and orbital systems could become disturbed.", payoff:"Even a small change in gravity rewrites the rules for everything touching Earth.", score:89},
  {topic:"What if a supernova exploded near Earth?", hook:"A nearby star dies, and its light arrives like a warning.", fact:"Supernovae release enormous energy and radiation into space.", danger:"If close enough, radiation could damage the atmosphere and threaten life.", payoff:"The explosion would be far away, but the danger could arrive at the speed of light.", score:92},
  {topic:"What if Earth had two moons?", hook:"Two moons rise together, and Earth's nights change forever.", fact:"Extra moons would affect tides, orbital stability and eclipse patterns.", danger:"Depending on size and distance, the second moon could destabilize tides or create collision risks.", payoff:"A second moon sounds romantic until gravity starts negotiating.", score:86}
];

const VISUAL_STYLE = "cinematic realistic sci-fi, deep space lighting, dramatic scale, blue-orange glow, high contrast, detailed particles, educational short-form video frame, no text on screen";
const SITE_URL = "https://mirzafraztahir-coder.github.io/Orbit-Unknown/";
const REVIEW_TEXT = `Orbit Studio is a web-based content-production dashboard for Orbit Unknown. It helps create educational science and space short-form videos by generating topics, scripts, scenes, AI video prompts, captions, titles, descriptions, thumbnail prompts, JSON exports and performance records. The app currently does not collect, access, store or share TikTok user data. It is being prepared for future TikTok/Symphony integration after the required access and credentials are approved.`;

const state = {
  jobs: JSON.parse(localStorage.getItem("orbit_jobs") || "[]"),
  settings: JSON.parse(localStorage.getItem("orbit_settings") || "{}"),
  performance: JSON.parse(localStorage.getItem("orbit_performance") || "[]")
};

function qs(id){ return document.getElementById(id); }
function save(){ localStorage.setItem("orbit_jobs", JSON.stringify(state.jobs)); localStorage.setItem("orbit_settings", JSON.stringify(state.settings)); }
function nowLabel(){ return new Date().toLocaleString(); }
function escapeHtml(str){ return String(str).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
function latest(){ return state.jobs[0]; }
function pickTopic(){
  const used = new Set(state.jobs.slice(0, 8).map(j => j.topic));
  const fresh = TOPICS.filter(t => !used.has(t.topic));
  const pool = fresh.length ? fresh : TOPICS;
  return pool[Math.floor(Math.random()*pool.length)];
}
function getSettings(){
  return {
    brand: state.settings.brand || "Orbit Unknown",
    handle: state.settings.handle || "@OrbitUnknownX",
    duration: Number(state.settings.duration || 35),
    format: state.settings.format || "Short cinematic science"
  };
}
function buildCaptions(script){
  return script.split(/\n+/).filter(Boolean).map((line, i) => ({block:i+1, text:line.length > 90 ? line.slice(0, 87) + "..." : line}));
}
function buildPackage(seed){
  const settings = getSettings();
  const script = `${seed.hook}\n\n${seed.fact}\n\nNow the dangerous part: ${seed.danger}\n\nIn only a few seconds, the result would be chaos, not science fiction.\n\n${seed.payoff}\n\n${settings.brand}. Impossible questions. Real science.`;
  const scenes = [
    {time:"0-5s", title:"Hook", prompt:`${seed.hook}. Planet-scale cinematic opening. ${VISUAL_STYLE}`},
    {time:"5-12s", title:"Fact reveal", prompt:`Show the scientific principle visually: ${seed.fact}. ${VISUAL_STYLE}`},
    {time:"12-22s", title:"Escalation", prompt:`Visualize the consequence: ${seed.danger}. Epic but scientifically grounded. ${VISUAL_STYLE}`},
    {time:"22-31s", title:"Climax", prompt:`Massive scale shot showing the peak danger of: ${seed.topic}. ${VISUAL_STYLE}`},
    {time:`31-${settings.duration}s`, title:"Ending", prompt:`Quiet final space shot with Orbit Unknown mood, mysterious and premium. ${VISUAL_STYLE}`}
  ];
  const captions = buildCaptions(script);
  const metadata = {
    title: seed.topic.replace("What if", "What If"),
    shortTitle: seed.topic.replace("What if ", "").replace("?", ""),
    caption: `${seed.topic} ${settings.handle} #space #science #whatif #physics #shorts`,
    hashtags: ["#space", "#science", "#whatif", "#physics", "#shorts"],
    thumbnailPrompt: `A dramatic premium sci-fi thumbnail for ${seed.topic}, high contrast, simple central object, deep space background, no words`,
    voice: "Clear, curious, cinematic, fast but understandable",
    aspectRatio: "9:16 preferred for Shorts/Reels/TikTok",
    productionNotes: "Use short scenes, hard cuts, captions on every sentence, no unsupported scientific claims beyond this script."
  };
  return {
    id: (crypto.randomUUID ? crypto.randomUUID() : String(Date.now())),
    topic: seed.topic,
    status: "Ready package",
    score: seed.score,
    duration: settings.duration,
    format: settings.format,
    created: nowLabel(),
    script,
    captions,
    scenes,
    metadata,
    performance: null
  };
}
function fullTextPackage(job){
  if(!job) return "No package generated.";
  return `ORBIT STUDIO PRODUCTION PACKAGE\n\nTopic: ${job.topic}\nDuration: ${job.duration}s\nStatus: ${job.status}\nScore: ${job.score}/100\n\nVOICE SCRIPT\n${job.script}\n\nSCENES AND PROMPTS\n${job.scenes.map((s,i)=>`Scene ${i+1} (${s.time}) - ${s.title}\n${s.prompt}`).join("\n\n")}\n\nCAPTION BLOCKS\n${job.captions.map(c=>`${c.block}. ${c.text}`).join("\n")}\n\nPUBLISHING METADATA\n${JSON.stringify(job.metadata, null, 2)}\n`;
}
function download(name, data, type="application/json"){
  const blob = new Blob([data], {type});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
}
async function copy(text, target="copyResult"){
  await navigator.clipboard.writeText(text);
  const el = qs(target);
  if(el){ el.textContent = "Copied."; setTimeout(()=>{ el.textContent = ""; }, 1800); }
}
function renderCalendar(){
  const today = new Date();
  qs("calendarList").innerHTML = Array.from({length:7}).map((_,i)=>{
    const d = new Date(today); d.setDate(today.getDate()+i);
    const topic = TOPICS[(state.jobs.length+i) % TOPICS.length];
    return `<div class="calendar-item"><strong>${d.toLocaleDateString(undefined,{weekday:"short", month:"short", day:"numeric"})}</strong><span>${escapeHtml(topic.topic)}</span></div>`;
  }).join("");
}
function render(){
  const jobs = state.jobs;
  const settings = getSettings();
  qs("metricJobs").textContent = jobs.length;
  qs("metricReady").textContent = jobs.filter(j=>j.status.includes("Ready")).length;
  qs("metricDuration").textContent = `${settings.duration}s`;
  qs("settingBrand").value = settings.brand;
  qs("settingHandle").value = settings.handle;
  qs("settingDuration").value = settings.duration;
  qs("settingFormat").value = settings.format;
  qs("reviewText").textContent = REVIEW_TEXT;
  renderCalendar();

  qs("jobsTable").innerHTML = jobs.length ? jobs.map(j=>`<tr data-id="${j.id}"><td>${escapeHtml(j.topic)}</td><td>${escapeHtml(j.status)}</td><td>${j.score}/100</td><td>${j.duration}s</td><td>${escapeHtml(j.created)}</td></tr>`).join("") : `<tr><td colspan="5" class="empty">No jobs yet. Generate the first one.</td></tr>`;

  const job = latest();
  if(!job){
    qs("performanceBox").textContent = state.performance.length ? JSON.stringify(state.performance, null, 2) : "No performance saved yet.";
    return;
  }
  qs("latestTitle").textContent = job.topic;
  qs("latestStatus").textContent = job.status;
  qs("scriptBox").textContent = job.script;
  qs("metadataBox").textContent = JSON.stringify(job.metadata, null, 2);
  qs("packageBox").textContent = fullTextPackage(job);
  qs("sceneList").innerHTML = job.scenes.map((s,i)=>`<article class="scene-card"><div class="scene-meta">Scene ${i+1} • ${s.time}</div><h4>${escapeHtml(s.title)}</h4><p>${escapeHtml(s.prompt)}</p></article>`).join("");
  qs("performanceBox").textContent = state.performance.length ? JSON.stringify(state.performance, null, 2) : "No performance saved yet.";
}

qs("generateToday").addEventListener("click", ()=>{ state.jobs.unshift(buildPackage(pickTopic())); save(); render(); });
qs("exportLatest").addEventListener("click", ()=>{ const job = latest(); if(!job){ alert("Generate a package first."); return; } download(`orbit-package-${job.id}.json`, JSON.stringify(job, null, 2)); });
qs("exportText").addEventListener("click", ()=>{ const job = latest(); if(!job){ alert("Generate a package first."); return; } download(`orbit-package-${job.id}.txt`, fullTextPackage(job), "text/plain"); });
qs("copyScript").addEventListener("click", ()=>{ const job=latest(); if(job) copy(job.script); });
qs("copyCaptions").addEventListener("click", ()=>{ const job=latest(); if(job) copy(job.captions.map(c=>c.text).join("\n")); });
qs("copyMetadata").addEventListener("click", ()=>{ const job=latest(); if(job) copy(JSON.stringify(job.metadata, null, 2)); });
qs("copyReviewText").addEventListener("click", ()=>copy(REVIEW_TEXT));
qs("copyUrls").addEventListener("click", ()=>copy(`Website: ${SITE_URL}\nTerms: ${SITE_URL}terms.html\nPrivacy: ${SITE_URL}privacy.html`));
qs("saveSettings").addEventListener("click", ()=>{ state.settings = {brand:qs("settingBrand").value, handle:qs("settingHandle").value, duration:Number(qs("settingDuration").value), format:qs("settingFormat").value}; save(); render(); });
qs("clearJobs").addEventListener("click", ()=>{ if(confirm("Clear local Orbit Studio jobs from this browser?")){ state.jobs=[]; save(); render(); } });
qs("savePerformance").addEventListener("click", ()=>{
  const job = latest();
  const perf = {topic: job ? job.topic : "Manual entry", views:Number(qs("viewsInput").value||0), likes:Number(qs("likesInput").value||0), watchPercent:Number(qs("watchInput").value||0), saved:nowLabel()};
  state.performance.unshift(perf); localStorage.setItem("orbit_performance", JSON.stringify(state.performance)); render();
});

render();

const TOPICS = [
  {
    topic: "What if Earth stopped spinning for 5 seconds?",
    hook: "For five seconds, Earth forgets how to spin.",
    fact: "The equator moves at about 1,670 km/h because of Earth's rotation.",
    danger: "The ground stops, but oceans, air and loose objects keep moving eastward.",
    payoff: "It would not feel like a pause. It would feel like the planet became a weapon."
  },
  {
    topic: "What if you dropped a sugar cube of neutron-star matter on Earth?",
    hook: "Imagine a sugar cube heavier than a mountain.",
    fact: "Neutron-star matter is extremely dense because atoms are crushed into nuclear-scale material.",
    danger: "Its gravity and pressure would violently disturb everything nearby.",
    payoff: "A tiny cube could behave less like an object and more like a disaster."
  },
  {
    topic: "What if the Moon disappeared tonight?",
    hook: "Tonight the Moon vanishes, and Earth keeps moving.",
    fact: "The Moon stabilizes Earth's axial tilt and strongly affects ocean tides.",
    danger: "Tides weaken, nights darken, ecosystems are disrupted and long-term climate stability changes.",
    payoff: "The sky would look emptier, but the damage would be written into the oceans."
  },
  {
    topic: "What if Jupiter became a second Sun?",
    hook: "A second sun appears where Jupiter used to be.",
    fact: "Jupiter is massive but still far too light to become a true star naturally.",
    danger: "If it somehow ignited, the outer solar system would become brighter, hotter and dynamically unstable.",
    payoff: "Earth might survive the light, but the solar system would no longer be the same machine."
  },
  {
    topic: "What if a black hole passed through Earth?",
    hook: "A black hole crosses the planet in silence.",
    fact: "A small black hole could pass through matter, but its gravity would still pull on nearby material.",
    danger: "The event would trigger violent seismic and gravitational effects along its path.",
    payoff: "The scariest part is not the darkness. It is how cleanly gravity can cut."
  }
];

const VISUAL_STYLE = "cinematic realistic sci-fi, deep space lighting, dramatic scale, blue-orange glow, high contrast, detailed particles, educational short-form video frame, no text on screen";
const state = {
  jobs: JSON.parse(localStorage.getItem("orbit_jobs") || "[]"),
  settings: JSON.parse(localStorage.getItem("orbit_settings") || "{}"),
  performance: JSON.parse(localStorage.getItem("orbit_performance") || "null")
};

function qs(id){ return document.getElementById(id); }
function save(){ localStorage.setItem("orbit_jobs", JSON.stringify(state.jobs)); localStorage.setItem("orbit_settings", JSON.stringify(state.settings)); }
function nowLabel(){ return new Date().toLocaleString(); }
function pickTopic(){ return TOPICS[Math.floor(Math.random()*TOPICS.length)]; }

function buildPackage(seed){
  const duration = Number(state.settings.duration || 35);
  const brand = state.settings.brand || "Orbit Unknown";
  const handle = state.settings.handle || "@OrbitUnknownX";
  const script = `${seed.hook}\n\n${seed.fact}\n\nNow the dangerous part: ${seed.danger}\n\nIn only a few seconds, the result would be chaos, not science fiction.\n\n${seed.payoff}\n\n${brand}. Impossible questions. Real science.`;
  const scenes = [
    {time:"0-5s", title:"Hook", prompt:`${seed.hook}. Planet-scale cinematic opening. ${VISUAL_STYLE}`},
    {time:"5-12s", title:"Fact reveal", prompt:`Show the scientific principle visually: ${seed.fact}. ${VISUAL_STYLE}`},
    {time:"12-24s", title:"Escalation", prompt:`Visualize the consequence: ${seed.danger}. Epic but scientifically grounded. ${VISUAL_STYLE}`},
    {time:"24-32s", title:"Climax", prompt:`Massive scale shot showing the peak danger of: ${seed.topic}. ${VISUAL_STYLE}`},
    {time:"32-${duration}s", title:"Ending", prompt:`Quiet final space shot with Orbit Unknown mood, mysterious and premium. ${VISUAL_STYLE}`}
  ];
  const metadata = {
    title: seed.topic.replace("What if", "What If"),
    caption: `${seed.topic} ${handle} #space #science #whatif #shorts`,
    hashtags: ["#space", "#science", "#whatif", "#physics", "#shorts"],
    thumbnailPrompt: `A dramatic premium sci-fi thumbnail for ${seed.topic}, high contrast, simple central object, space background, no words`,
    voice: "Clear, curious, cinematic, fast but understandable",
    productionNotes: "Use short scenes, hard cuts, captions on every sentence, avoid claims beyond the script."
  };
  return {
    id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
    topic: seed.topic,
    status: "Ready package",
    score: Math.floor(82 + Math.random()*15),
    duration,
    created: nowLabel(),
    script,
    scenes,
    metadata,
    performance: null
  };
}

function render(){
  const jobs = state.jobs;
  qs("metricJobs").textContent = jobs.length;
  qs("metricReady").textContent = jobs.filter(j=>j.status.includes("Ready")).length;
  qs("metricDuration").textContent = `${state.settings.duration || 35}s`;
  qs("settingBrand").value = state.settings.brand || "Orbit Unknown";
  qs("settingHandle").value = state.settings.handle || "@OrbitUnknownX";
  qs("settingDuration").value = state.settings.duration || 35;

  qs("jobsTable").innerHTML = jobs.length ? jobs.map(j=>`<tr data-id="${j.id}"><td>${escapeHtml(j.topic)}</td><td>${escapeHtml(j.status)}</td><td>${j.score}/100</td><td>${j.duration}s</td><td>${escapeHtml(j.created)}</td></tr>`).join("") : `<tr><td colspan="5" class="empty">No jobs yet. Generate the first one.</td></tr>`;

  const latest = jobs[0];
  if(!latest){ return; }
  qs("latestTitle").textContent = latest.topic;
  qs("latestStatus").textContent = latest.status;
  qs("scriptBox").textContent = latest.script;
  qs("metadataBox").textContent = JSON.stringify(latest.metadata, null, 2);
  qs("sceneList").innerHTML = latest.scenes.map((s,i)=>`<article class="scene-card"><div class="scene-meta">Scene ${i+1} • ${s.time}</div><h4>${escapeHtml(s.title)}</h4><p>${escapeHtml(s.prompt)}</p></article>`).join("");
  qs("performanceBox").textContent = state.performance ? JSON.stringify(state.performance, null, 2) : "No performance saved yet.";
}

function escapeHtml(str){ return String(str).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
function latest(){ return state.jobs[0]; }
function download(name, data){
  const blob = new Blob([data], {type:"application/json"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
}

qs("generateToday").addEventListener("click", ()=>{
  const job = buildPackage(pickTopic());
  state.jobs.unshift(job);
  save(); render();
});
qs("exportLatest").addEventListener("click", ()=>{
  const job = latest();
  if(!job){ alert("Generate a package first."); return; }
  download(`orbit-package-${job.id}.json`, JSON.stringify(job, null, 2));
});
qs("copyLatest").addEventListener("click", async ()=>{
  const job = latest();
  if(!job){ qs("copyResult").textContent = "Generate a script first."; return; }
  await navigator.clipboard.writeText(job.script);
  qs("copyResult").textContent = "Latest script copied.";
});
qs("saveSettings").addEventListener("click", ()=>{
  state.settings = {brand:qs("settingBrand").value, handle:qs("settingHandle").value, duration:Number(qs("settingDuration").value)};
  save(); render();
});
qs("clearJobs").addEventListener("click", ()=>{
  if(confirm("Clear local Orbit Studio jobs from this browser?")){ state.jobs=[]; save(); location.reload(); }
});
qs("savePerformance").addEventListener("click", ()=>{
  const job = latest();
  const perf = {topic: job ? job.topic : "Manual entry", views:Number(qs("viewsInput").value||0), likes:Number(qs("likesInput").value||0), watchPercent:Number(qs("watchInput").value||0), saved:nowLabel()};
  state.performance = perf; localStorage.setItem("orbit_performance", JSON.stringify(perf)); render();
});

render();

"""Orbit Unknown: deterministic daily topic rotation and preflight checks."""
import json
import random
from datetime import datetime, timezone
from pathlib import Path

TOPICS = [
 {"topic":"What If the Sun Vanished?","hook":"The Sun disappears. For eight minutes, nobody knows.","fact":"Sunlight takes about eight minutes and twenty seconds to reach Earth.","danger":"After that delay, the daylit side goes dark and Earth no longer follows its solar orbit.","payoff":"The planet keeps moving through space. Cooling happens over time, not instantly."},
 {"topic":"What If the Moon Vanished?","hook":"One night, the Moon is simply gone.","fact":"The Moon is a major driver of Earth's ocean tides.","danger":"Tidal patterns change, while Earth's axial stability is affected over very long timescales.","payoff":"The most important consequences are not an instant worldwide catastrophe."},
 {"topic":"What If Earth Stopped Rotating?","hook":"Imagine Earth suddenly stopped spinning.","fact":"The equator normally moves at roughly 1,670 kilometres per hour.","danger":"If the ground stopped abruptly, inertia would keep much of the atmosphere and oceans moving.","payoff":"A five-second pause would be anything but peaceful."},
 {"topic":"What If You Fell Into Jupiter?","hook":"There is no solid surface waiting for you on Jupiter.","fact":"Jupiter's visible clouds conceal an atmosphere that becomes denser with depth.","danger":"Pressure and temperature rise enormously as you descend.","payoff":"You would not land on a normal rocky ground."},
 {"topic":"What If Earth Had Two Moons?","hook":"Imagine two bright moons above every night.","fact":"Two moons would each exert gravitational forces on Earth's oceans.","danger":"Tides and long-term orbital stability would depend on their masses and distances.","payoff":"A beautiful sky could hide a complicated gravitational dance."},
 {"topic":"What If a Star Exploded Nearby?","hook":"A supernova flashes in our cosmic neighbourhood.","fact":"Supernovae release extraordinary amounts of radiation and expanding matter.","danger":"A sufficiently close explosion could harm Earth's atmosphere and biosphere.","payoff":"Distance matters far more than the dramatic brightness alone."},
 {"topic":"What If You Traveled at Light Speed?","hook":"Could a spacecraft ever reach the speed of light?","fact":"Objects with mass cannot be accelerated to light speed under special relativity.","danger":"The energy required grows without bound as speed approaches light speed.","payoff":"Near-light-speed travel is already strange enough."},
 {"topic":"What If Saturn Lost Its Rings?","hook":"Saturn wakes up without its famous rings.","fact":"Saturn's rings are mostly ice particles orbiting the planet.","danger":"The disappearance would transform its appearance, not destroy the planet.","payoff":"Saturn itself would keep orbiting the Sun."},
 {"topic":"What If the Oceans Froze?","hook":"Picture every ocean under a lid of ice.","fact":"Ice floats, insulating liquid water beneath it.","danger":"Marine ecosystems and climate would change dramatically as freezing progressed.","payoff":"The deepest ocean would not instantly turn solid."},
 {"topic":"What If Mars Had an Ocean?","hook":"Imagine blue seas on the red planet.","fact":"Mars shows strong evidence of ancient flowing liquid water.","danger":"A lasting surface ocean today would require radically different environmental conditions.","payoff":"Water alone does not make a planet habitable."}
]

def main():
    out=Path("outbox");out.mkdir(exist_ok=True)
    log=out/"topic_history.json"
    history=json.loads(log.read_text()) if log.exists() else []
    used={x.get("topic") for x in history[-len(TOPICS):]}
    available=[t for t in TOPICS if t["topic"] not in used] or TOPICS
    rng=random.Random(datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    topic=rng.choice(available)
    package={"topic":topic["topic"],"script":" ".join(topic[k] for k in ("hook","fact","danger","payoff")),"metadata":{"title":topic["topic"],"caption":topic["topic"]+" | Impossible Questions. Real Science. #shorts #science #space #orbitunknown","privacyStatus":"public"},"scenes":[{"time":f"{i*4}-{(i+1)*4}s","text":topic[k]} for i,k in enumerate(("hook","fact","danger","payoff"))]}
    (out/"next_topic.json").write_text(json.dumps(package,indent=2))
    print("Prepared distinct topic:",topic["topic"])
if __name__=="__main__": main()

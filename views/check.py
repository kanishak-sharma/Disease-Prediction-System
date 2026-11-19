import streamlit as st

from core import charts
from core.diseases import DISEASES
from core.knowledge import KNOWLEDGE, LEVEL_LABEL, flagged, overall_advice_level
from core.training import explain, load_bundle, out_of_range, predict, risk_level
from core.ui import disclaimer, esc, page_head


@st.cache_resource(show_spinner=False)
def bundle(key):
    return load_bundle(key)


def snap(v, f):
    """Round a typical value to the input's step so widgets accept it."""
    step = f.get("step", 1.0)
    return round(round(v / step) * step, 4) if f["kind"] == "num" else int(round(v))


def set_values(key, which):
    b = bundle(key)
    for f in DISEASES[key]["features"]:
        v = b["stats"][f["name"]][which]
        st.session_state[f"{key}_{f['name']}"] = (bool(snap(v, f)) if f["kind"] == "cat" and f["options"] == {0: "No", 1: "Yes"}
                                                   else snap(v, f))


page_head("Health check", "Pick a condition, enter your numbers, and see your risk compared with a healthy person.")

keys = list(DISEASES)
if st.session_state.get("disease") not in keys:
    st.session_state["disease"] = keys[0]
key = st.segmented_control("Condition", keys, format_func=lambda k: f"{DISEASES[k]['emoji']} {DISEASES[k]['name']}",
                           default=st.session_state["disease"], label_visibility="collapsed") or st.session_state["disease"]
st.session_state["disease"] = key
cfg, b, kb = DISEASES[key], bundle(key), KNOWLEDGE[key]

st.caption(f"**{cfg['name']}** · {cfg['tagline']}")
if key == "liver":
    st.warning("Experimental: this model is the weakest of the six. Use it as a hint only.", icon="🧪")
st.info(cfg["caveat"], icon="ℹ️")

# initialise widget state with typical healthy values
for f in cfg["features"]:
    k = f"{key}_{f['name']}"
    if k not in st.session_state:
        set_values(key, "healthy_median")

left, right = st.columns([5, 7], gap="large")

with left:
    st.markdown("#### Your numbers")
    b1, b2 = st.columns(2)
    b1.button("Typical healthy person", on_click=set_values, args=(key, "healthy_median"), width="stretch", key=f"h_{key}")
    b2.button("Typical patient", on_click=set_values, args=(key, "disease_median"), width="stretch", key=f"d_{key}")
    values = {}
    with st.container(border=True):
        for f in cfg["features"]:
            k = f"{key}_{f['name']}"
            label = f["label"] + (f" ({f['unit']})" if f["unit"] else "")
            s = b["stats"][f["name"]]
            if f["kind"] == "cat":
                if f["options"] == {0: "No", 1: "Yes"}:
                    values[f["name"]] = int(st.toggle(f["label"], key=k, help=f["help"] or None))
                else:
                    values[f["name"]] = st.selectbox(f["label"], list(f["options"]), format_func=f["options"].get, key=k, help=f["help"] or None)
            else:
                fmt = f"%.{f['decimals']}f" if f["decimals"] else "%.0f"
                values[f["name"]] = st.number_input(label, min_value=0.0, max_value=float(max(s["max"] * 2, 1)), step=float(f["step"]),
                                                    format=fmt, key=k, help=(f["help"] or None))

p = predict(b, values)
level = risk_level(p)
flags = flagged(key, values)
advice = overall_advice_level(flags, p)

with right:
    st.markdown("#### Your result")
    g, r = st.columns([5, 6], gap="medium")
    g.plotly_chart(charts.gauge(p), width="stretch", config={"displayModeBar": False})
    headline = {"Low": "Low risk", "Moderate": "Moderate risk", "High": "High risk"}[level]
    sub = {"ok": "Nothing here needs urgent action. Keep up healthy habits.",
           "watch": "A few values deserve attention. Review the home-care tips.",
           "see": "Please book a doctor's visit to confirm these results.",
           "urgent": "Some values are in a dangerous range. Get medical care promptly."}[advice]
    r.markdown(f'<div class="result-card {level.lower()}"><h2>{headline}</h2>'
               f'<p><b>{p * 100:.0f}%</b> estimated chance of {esc(cfg["name"].lower())} based on the model.</p>'
               f'<p>{sub}</p></div>', unsafe_allow_html=True)
    odd = out_of_range(b, values)
    if odd:
        names = ", ".join(next(f["label"] for f in cfg["features"] if f["name"] == n) for n in odd)
        st.warning(f"These values are outside the range the model learned from, so the result may be unreliable: {names}.", icon="⚠️")

    tabs = st.tabs(["📊 Vs. normal", "🔍 Why this result", "🌿 Home care", "🩺 When to see a doctor", "📄 Report"])

    with tabs[0]:
        st.caption("Green band = normal range (or typical healthy range where no medical standard exists). "
                   "Teal dot = you, red dot = you are outside the band.")
        st.plotly_chart(charts.range_chart(b, cfg, values), width="stretch", config={"displayModeBar": False})
        with st.expander("Overall profile (radar)"):
            st.plotly_chart(charts.radar(b, cfg, values), width="stretch", config={"displayModeBar": False})

    with tabs[1]:
        ex = explain(b, values)
        st.caption("How much each input changes your risk compared with having a typical healthy value there. Red raises risk, green lowers it.")
        st.plotly_chart(charts.contributions(ex, cfg), width="stretch", config={"displayModeBar": False})

    with tabs[2]:
        tier = level.lower()
        st.markdown(f"**Suggested at your risk level ({level.lower()})**")
        for tip in kb["remedies"][tier]:
            st.markdown(f"- {tip}")
        if tier != "high":
            with st.expander("If your risk rises"):
                for tip in kb["remedies"]["high"]:
                    st.markdown(f"- {tip}")
        st.caption("Home care supports medical treatment. It never replaces it.")

    with tabs[3]:
        if flags:
            st.markdown("**Your values that need attention**")
            for fl in flags:
                label = next(f["label"] for f in cfg["features"] if f["name"] == fl["feature"])
                st.markdown(f'<div class="flag {fl["level"]}"><small>{LEVEL_LABEL[fl["level"]]} · {esc(label)}</small>{esc(fl["message"])}</div>',
                            unsafe_allow_html=True)
        else:
            st.success("None of your entered values crosses a warning threshold.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Go to a doctor immediately if you have**")
            for x in kb["red_flags"]:
                st.markdown(f"- {x}")
        with c2:
            st.markdown("**Tests to ask about**")
            for x in kb["tests"]:
                st.markdown(f"- {x}")

    with tabs[4]:
        lines = [f"# {cfg['name']} check", "", f"Estimated risk: {p * 100:.0f}% ({level})", "", "## Your values"]
        for f in cfg["features"]:
            v = values[f["name"]]
            shown = f["options"][v] if f["kind"] == "cat" else f"{v:g} {f['unit']}".strip()
            lines.append(f"- {f['label']}: {shown}")
        lines += ["", "## Needs attention"] + ([f"- [{LEVEL_LABEL[x['level']]}] {x['message']}" for x in flags] or ["- Nothing flagged"])
        lines += ["", "## Home-care suggestions"] + [f"- {t}" for t in kb["remedies"][level.lower()]]
        lines += ["", "---", "Student ML project for education only. Not medical advice."]
        report = "\n".join(lines)
        st.download_button("Download this report", report, file_name=f"{key}_report.md", mime="text/markdown", width="stretch")
        st.code(report, language="markdown")

st.write("")
disclaimer()

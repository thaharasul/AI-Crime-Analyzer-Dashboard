

from services import gemini_service

SYSTEM_INSTRUCTION = (
    "You are a public-safety planning assistant for a city police "
    "department. Given structured crime statistics, produce concise, "
    "practical recommendations covering patrol allocation, CCTV "
    "deployment, and community awareness. Be specific about zones and "
    "categories mentioned in the data. Keep it under 200 words and use "
    "short bullet points."
)


def _fallback_recommendations(analysis: dict) -> str:
    lines = ["Recommendations (rule-based fallback - no Gemini key configured):"]
    for zone_info in analysis.get("zone_anomalies", [])[:3]:
        lines.append(
            f"- Increase patrol frequency in {zone_info['zone']} "
            f"(incident rate up {zone_info['increase_pct']}% vs baseline)."
        )
    for cat_info in analysis.get("top_categories", [])[:2]:
        lines.append(
            f"- Run targeted awareness campaigns for {cat_info['category']} "
            f"prevention, the leading category with {cat_info['count']} cases."
        )
    for hour_info in analysis.get("peak_hours", [])[:1]:
        lines.append(
            f"- Prioritize CCTV/patrol coverage around {hour_info['hour']}:00, "
            "the peak incident hour citywide."
        )
    return "\n".join(lines)


def run(analysis: dict) -> str:
    if not gemini_service.is_configured():
        return _fallback_recommendations(analysis)

    prompt = (
        "Crime analysis data (JSON):\n"
        f"{analysis}\n\n"
        "Produce prioritized, actionable recommendations for police "
        "leadership based on this data."
    )
    try:
        return gemini_service.generate(prompt, system_instruction=SYSTEM_INSTRUCTION)
    except Exception as exc:
        return _fallback_recommendations(analysis) + f"\n\n(Gemini call failed: {exc})"

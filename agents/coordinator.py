

from agents import analyst_agent, prediction_agent, recommendation_agent


def handle_request(intent: str, payload: dict | None = None) -> dict:
    """
    intent: one of "analysis", "prediction", "recommendation", "full_briefing"
    payload: extra input the relevant agent needs (e.g. a prediction scenario)
    """
    payload = payload or {}

    if intent == "analysis":
        analysis = analyst_agent.run_full_analysis()
        return {"intent": intent, "analysis": analysis}

    if intent == "prediction":
        scenario = payload.get("scenario", {})
        prediction = prediction_agent.run(scenario)
        return {"intent": intent, "prediction": prediction}

    if intent == "recommendation":
        analysis = analyst_agent.run_full_analysis()
        recommendation = recommendation_agent.run(analysis)
        return {"intent": intent, "analysis": analysis, "recommendation": recommendation}

    if intent == "full_briefing":
        # Runs every specialist agent and combines them - this is what
        # backs the "Report Generator" executive summary.
        analysis = analyst_agent.run_full_analysis()
        recommendation = recommendation_agent.run(analysis)

        prediction = None
        if payload.get("scenario"):
            prediction = prediction_agent.run(payload["scenario"])

        return {
            "intent": intent,
            "analysis": analysis,
            "recommendation": recommendation,
            "prediction": prediction,
        }

    raise ValueError(f"Unknown intent: {intent}")

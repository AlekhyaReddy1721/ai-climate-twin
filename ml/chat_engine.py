"""
AI Climate Chat Engine — rule-based NLP with keyword matching.
Replace with OpenAI/Gemini API call in production.
"""

KNOWLEDGE_BASE = {
    "global warming": (
        "Global warming refers to the long-term rise in Earth's average surface temperature due to human activities, "
        "primarily burning fossil fuels. Since pre-industrial times, the planet has warmed by approximately 1.1°C. "
        "At current rates, we are projected to exceed 1.5°C by 2040."
    ),
    "co2": (
        "CO2 (carbon dioxide) is the primary greenhouse gas driving climate change. Atmospheric CO2 has risen from "
        "280 ppm pre-industrial to over 421 ppm today — the highest in 3 million years. Every 1 ppm increase "
        "traps additional heat equivalent to 1.5 billion tons of TNT annually."
    ),
    "sea level": (
        "Global sea levels have risen ~20cm since 1900, with the rate accelerating. Current projections suggest "
        "0.3–1.0m rise by 2100 under moderate scenarios, threatening 1 billion coastal residents. "
        "Thermal expansion and ice melt are the two main drivers."
    ),
    "flood": (
        "Climate change intensifies flooding through heavier rainfall events and sea level rise. "
        "Flood frequency has increased 4x since 1980. South Asia, West Africa, and Southeast Asia "
        "face the highest flood risks. Urban flooding is worsened by impervious surfaces."
    ),
    "drought": (
        "Droughts are becoming more frequent and severe due to rising temperatures increasing evaporation. "
        "The Mediterranean, Sub-Saharan Africa, and western North America are drought hotspots. "
        "By 2050, up to 40% of the global population may face water scarcity."
    ),
    "cyclone": (
        "While total cyclone frequency may not increase, climate change is intensifying the strongest storms. "
        "Warmer ocean temperatures fuel rapid intensification. Category 4-5 hurricanes have increased 25% "
        "since the 1980s. Storm surge is amplified by sea level rise."
    ),
    "wildfire": (
        "Wildfires are increasing in frequency and intensity due to hotter, drier conditions. "
        "Australia, California, Siberia, and the Amazon have seen record fires. "
        "Fire seasons are now 20% longer globally. Smoke from wildfires creates secondary health crises."
    ),
    "arctic": (
        "The Arctic is warming 4x faster than the global average — a phenomenon called Arctic amplification. "
        "Arctic sea ice extent has declined 13% per decade since 1979. "
        "Summer ice-free Arctic conditions are projected by 2050, disrupting global weather patterns."
    ),
    "renewable energy": (
        "Renewable energy (solar, wind, hydro) now accounts for ~30% of global electricity. "
        "Solar costs have dropped 90% since 2010. To limit warming to 1.5°C, renewables must reach "
        "70-85% of electricity by 2050. The transition also creates millions of jobs."
    ),
    "paris agreement": (
        "The Paris Agreement (2015) commits nations to limit warming to well below 2°C, ideally 1.5°C. "
        "Current national pledges put us on track for ~2.7°C. The agreement requires net-zero emissions "
        "by 2050 globally. Annual COP summits track progress."
    ),
    "deforestation": (
        "Forests absorb ~2.6 billion tons of CO2 annually. Deforestation releases stored carbon and "
        "reduces this sink capacity. The Amazon has lost 17% of its forest in 50 years. "
        "Deforestation accounts for ~10% of global greenhouse gas emissions."
    ),
    "carbon footprint": (
        "The average global carbon footprint is ~4 tons CO2 per person per year. "
        "To limit warming to 1.5°C, this must fall to ~2.5 tons by 2030. "
        "The biggest contributors are transportation (29%), electricity (25%), and industry (23%)."
    ),
}

DEFAULT_RESPONSE = (
    "That's a great climate question. The Earth's climate system is complex and interconnected. "
    "Key factors include greenhouse gas concentrations, ocean heat content, albedo effects, and "
    "atmospheric circulation patterns. I recommend exploring the dashboard for real-time data "
    "and the prediction tools for future projections. Ask me about specific topics like "
    "'global warming', 'sea level', 'floods', 'droughts', 'arctic', or 'renewable energy'."
)


def ask(question: str) -> dict:
    q = question.lower()
    matched_topics = []
    response_parts = []

    for keyword, answer in KNOWLEDGE_BASE.items():
        if keyword in q:
            matched_topics.append(keyword)
            response_parts.append(answer)

    if response_parts:
        response = " ".join(response_parts[:2])  # max 2 topics per response
    else:
        response = DEFAULT_RESPONSE

    return {
        "question": question,
        "answer": response,
        "topics_detected": matched_topics,
        "confidence": "high" if matched_topics else "general",
        "sources": ["IPCC AR6 Report", "NASA GISS", "NOAA Climate.gov"],
    }

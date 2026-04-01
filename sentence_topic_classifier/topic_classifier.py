import textwrap


def get_topic_on_sentences(sentences):
    if not isinstance(sentences, list):
        raise TypeError("sentences must be a list of strings")

    formatted_sentences = "\n".join(
        f"- {str(sentence)}" for sentence in sentences
    )
    formatted_sentences = textwrap.indent(formatted_sentences, '    ')
    prompt = f"""You are a financial language expert specialising in earnings call analysis.
    
    Your job is to label sentences as belonging to a specific topic, given a list of 10 topics. 
    
    TOPICS:
    1. Financial performance (revenue, EPS, margins, guidance, cash flow)
    2. Products & hardware (chips, devices, platforms, product launches)
    3. Cloud & infrastructure (cloud services, data centres, networking, IaaS/PaaS)
    4. AI & software (AI/ML products, SaaS, software platforms, models)
    5. Supply chain & ops (manufacturing, sourcing, inventory, capacity)
    6. Market & competition (market share, pricing, competitive dynamics)
    7. R&D and innovation (research spend, roadmaps, IP, future tech bets)
    8. Macro & geopolitics (trade policy, export controls, FX, demand environment)
    9. Customers & partners (enterprise deals, hyperscalers, partnerships, verticals)
    10. ESG & governance (sustainability, regulation, workforce, ethics)
    
    EXAMPLES:
    We delivered revenue of $35.1 billion, up 17% year over year, driven by strong performance across all segments. (Label = 1)
    The Ryzen 9000 series saw strong attach rates in the enthusiast desktop segment, gaining roughly 4 points of unit share. (Label = 2)
    CoWoS packaging capacity constraints at TSMC continue to limit our ability to fulfil demand for H100 modules. (Label = 5)
    The October 2023 export control regulations continue to restrict our ability to sell A800 and H800 products to customers in China. (Label = 8)
    We reduced our Scope 1 and Scope 2 carbon emissions by 18% year over year, ahead of our 2025 target. (Label = 10)
    Our partnership with SAP to embed Joule AI across the S/4HANA suite is now live at over 200 enterprise customers. (Label = 9)
    Google Cloud reached a $12 billion annualised run rate, with infrastructure and platform services driving the majority of growth. (Label = 3)
    Our AI-powered security portfolio, including Cisco AI Defense, grew bookings 40% in the quarter. (Label = 4)
    We are seeing increased price competition in the commodity NAND market as Chinese manufacturers expand capacity. (Label = 6)
    Project Stargate represents a multi-year bet on optical interconnect technology that we believe will define the post-copper era. (Label = 7)
    
    AMBIGUOUS EXAMPLES:
    These sentences could fit multiple topics. Use the tiebreaker rules (outlined after this section) to assign the correct label.
    - We are investing $20 billion in data centre capacity this year, weighted towards the second half. (Label = 3, not 1 — capex with a stated strategic purpose belongs to cloud & infrastructure)
    - We took a $2.1 billion inventory write-down related to legacy DDR4 products. (Label = 5, not 1 — operationally caused financial event belongs to supply chain)
    - Amazon, Google, and Microsoft accounted for 42% of our GPU revenue this quarter. (Label = 9, not 1 — named customers present, so prefer customers & partners)
    - Our Rubin GPU architecture, targeting 2026 delivery, will feature a new NVLink fabric. (Label = 7, not 2 — no confirmed launch, still roadmap stage)
    - Our China revenue declined to 9% of total sales following the imposition of export restrictions. (Label = 8, not 6 — geopolitical factors are the primary subject, not competitive dynamics)
    
    TIE BREAKER RULES:
    If a sentence could belong to multiple topics, apply these rules in order (top to bottom):
    - If a specific customer or partner is named, prefer topic 9 over topic 1
    - If a sentence explains an operational/manufacturing cause, prefer topic 5 over topic 1
    - If a sentence mentions research-stage work with no launch date, prefer topic 7 over topic 2
    - If a sentence describes capex or investment with a stated infrastructure purpose, prefer topic 3 over topic 1.
    - Assign by primary subject (what is the sentence about, not what it mentions)
    
    ANSWER FORMAT:
    - do NOT give any explanation, punctuation or extra text. just comma-separated labels
    - give your labels to each sentence in the form "1,4,3,5,9,..." (comma-separated and without any spacing) in the order they are given to you 
    
    SENTENCES TO LABEL:
{formatted_sentences}
    """
    return prompt
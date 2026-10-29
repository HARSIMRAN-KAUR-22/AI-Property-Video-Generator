def generate_property_script(property_data: dict) -> dict:
    name = property_data.get("name", "Exclusive Property")
    location = property_data.get("location", "Prime Location")
    price = property_data.get("price", "Contact for Price")
    prop_type = property_data.get("type", "Residential Property")
    features = property_data.get("features", [])
    contact = property_data.get("contact", "Contact us today for details!")

    feature_text = ", ".join(features) if features else "Spacious living area, premium amenities"

    voiceover_intro = f"Welcome to {name}, located in {location}."
    voiceover_details = f"This magnificent {prop_type} is offered at {price}."
    voiceover_features = f"Key highlights include: {feature_text}."
    voiceover_cta = f"For more information or to schedule a tour: {contact}"

    full_voiceover = f"{voiceover_intro} {voiceover_details} {voiceover_features} {voiceover_cta}"

    scenes = [
        {
            "title": "Welcome Home",
            "caption": f"{name}\n{location}",
            "voiceover_segment": voiceover_intro
        },
        {
            "title": "Property Overview",
            "caption": f"{prop_type} - {price}",
            "voiceover_segment": voiceover_details
        }
    ]

    if features:
        for idx, feat in enumerate(features[:3]):
            scenes.append({
                "title": f"Feature {idx+1}",
                "caption": feat,
                "voiceover_segment": f"Featured here: {feat}"
            })

    scenes.append({
        "title": "Enquire Now",
        "caption": f"Interested?\n{contact}",
        "voiceover_segment": voiceover_cta
    })

    return {
        "full_voiceover": full_voiceover,
        "scenes": scenes
    }

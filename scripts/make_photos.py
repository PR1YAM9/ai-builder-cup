"""Generate synthetic claim photos with Gemini image generation on Vertex AI.

Run: python scripts/make_photos.py   (needs gcloud ADC; set GOOGLE_CLOUD_PROJECT)
Writes JPGs into samples/. Every photo is synthetic and labelled as such in the UI.
"""

import io
import os
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "samples"
MODEL = "gemini-2.5-flash-image"
STYLE = (" Realistic smartphone photo taken by an ordinary person for an insurance claim, "
         "natural daylight, slightly off-centre framing, no people, no text, no watermark, "
         "no visible licence plate characters.")

PHOTOS = {
    # Matches the narrative: rear-end impact.
    "s1_damage_rear.jpg": "The rear of a silver compact four-door sedan stopped on a city street. "
                          "The rear bumper is cracked and pushed in on the right side and the right "
                          "tail lamp is shattered, with plastic fragments on the road.",
    # Deliberately contradicts the narrative (claimant says rear damage).
    "s2_damage_front.jpg": "The front of a white compact SUV in an outdoor parking lot. The front "
                           "bumper is crushed, the hood is crumpled upward, and both headlamps are "
                           "broken. The rear of the vehicle is not visible.",
    "s4_kitchen_water.jpg": "A small apartment kitchen after a leak under the sink. The lower cabinet "
                            "doors are swollen and warped at the bottom, the laminate floor planks "
                            "are lifted and stained, and there is a damp tide mark on the cabinet base.",
}


def main():
    client = genai.Client(vertexai=True, project=os.environ["GOOGLE_CLOUD_PROJECT"], location="global")
    for name, prompt in PHOTOS.items():
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt + STYLE,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
        data = next(p.inline_data.data for p in resp.candidates[0].content.parts if p.inline_data)
        img = Image.open(io.BytesIO(data)).convert("RGB")
        img.thumbnail((1280, 1280))
        img.save(OUT / name, quality=86)
        print("wrote", name, img.size)


if __name__ == "__main__":
    main()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy
import logging
from typing import Optional, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Load the English NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.info("Downloading spaCy model...")
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class PromptRequest(BaseModel):
    prompt: str

class ParsedInfo(BaseModel):
    hotel_name: str
    location: Optional[str] = None
    confidence: float

@app.post("/parse-prompt", response_model=ParsedInfo)
async def parse_prompt(request: PromptRequest):
    try:
        # Process the text with spaCy
        doc = nlp(request.prompt)
        
        # Initialize variables
        hotel_name = ""
        location = ""
        confidence = 0.0
        
        # First pass: Look for organization entities (potential hotel names)
        org_ents = [ent for ent in doc.ents if ent.label_ in ["ORG", "FAC"]]
        
        # Second pass: Look for location entities
        loc_ents = [ent for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        
        # If we found both organization and location
        if org_ents and loc_ents:
            hotel_name = org_ents[0].text
            location = loc_ents[0].text
            confidence = 0.9
        
        # If we only found organization
        elif org_ents:
            hotel_name = org_ents[0].text
            # Try to find location after "in" preposition
            for token in doc:
                if token.text.lower() == "in" and token.i + 1 < len(doc):
                    location = doc[token.i + 1:].text.strip()
                    break
            confidence = 0.7
        
        # If no clear entities found, fall back to rule-based approach
        if not hotel_name:
            # Remove common prefixes
            text = request.prompt.lower()
            for prefix in ["generate", "create", "make", "design"]:
                if text.startswith(prefix):
                    text = text.replace(prefix, "", 1).strip()
            
            # Remove "a brochure for" and similar phrases
            for phrase in ["a brochure for", "brochure for", "a brochure of", "brochure of"]:
                if phrase in text:
                    text = text.split(phrase)[-1].strip()
            
            # Split by "in" to separate hotel and location
            parts = text.split(" in ")
            if len(parts) >= 2:
                hotel_name = parts[0].strip().title()
                location = parts[1].strip().title()
                confidence = 0.5
            else:
                hotel_name = text.strip().title()
                confidence = 0.3
        
        return ParsedInfo(
            hotel_name=hotel_name,
            location=location,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Error parsing prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)

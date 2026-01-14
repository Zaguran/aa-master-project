import streamlit as st
import requests
import json
import base64
import io
from pdf2image import convert_from_bytes
from PIL import Image

# --- APP CONFIGURATION ---
APP_VERSION = "1.0.1"
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL_NAME = "llava"

st.set_page_config(
    page_title=f"AI Requirements Extractor v{APP_VERSION}",
    page_icon="📄",
    layout="wide"
)

# --- HELPER FUNCTIONS ---
def check_ollama_status():
    """Check if Ollama service is running and responsive."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            has_llava = any("llava" in name.lower() for name in model_names)
            return True, has_llava
        return False, False
    except Exception:
        return False, False


def reset_session():
    """Reset all session state variables."""
    keys_to_clear = ["extraction_results", "processed_images", "messages"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def convert_pdf_to_images(pdf_bytes, dpi=150):
    """Convert PDF bytes to list of PIL Images."""
    try:
        images = convert_from_bytes(pdf_bytes, dpi=dpi)
        return images
    except Exception as e:
        st.error(f"PDF conversion error: {str(e)}")
        return []


def image_to_base64(image):
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def extract_requirements_from_image(image_base64, customer_id, custom_instructions=""):
    """Send image to Ollama llava model for requirements extraction."""

    # STRICT PROMPT - Forbids hallucination and outside knowledge
    system_prompt = f"""You are a strict document text extractor. Your ONLY task is to extract text that is VISIBLY present in the provided image.

CRITICAL RULES:
1. ONLY extract text that you can SEE in the image. Do NOT invent, assume, or hallucinate any content.
2. If you cannot read text clearly, mark it as [UNCLEAR].
3. If no requirements are visible, respond with "NO REQUIREMENTS FOUND IN IMAGE".
4. Do NOT use any outside knowledge. Do NOT add explanations or interpretations.
5. Extract EXACTLY what is written - do not paraphrase or summarize.

Customer ID: {customer_id}

Output format - Use this EXACT markdown table structure:
| Req ID | Requirement Text | Status |
|--------|------------------|--------|
| [ID from image or AUTO-001] | [Exact text from image] | Extracted |

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

REMEMBER: If text is not visible in the image, do NOT make it up. Only report what you can actually see."""

    payload = {
        "model": MODEL_NAME,
        "prompt": system_prompt,
        "images": [image_base64],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_ctx": 4096,
            "num_thread": 8
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response received")
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out. Please try again."
    except Exception as e:
        return f"ERROR: {str(e)}"


# --- SIDEBAR ---
st.sidebar.title("AI Requirements Extractor")
st.sidebar.markdown(f"**Version:** `{APP_VERSION}`")
st.sidebar.markdown("---")

# Ollama Status Check
ollama_online, llava_available = check_ollama_status()

if ollama_online:
    st.sidebar.success("Ollama: Online")
    if llava_available:
        st.sidebar.success(f"Model: {MODEL_NAME} Ready")
    else:
        st.sidebar.warning(f"Model: {MODEL_NAME} Not Found")
else:
    st.sidebar.error("Ollama: Offline")

st.sidebar.markdown("---")

# Reset Session Button
if st.sidebar.button("Reset Session", type="primary", use_container_width=True):
    reset_session()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Settings:**")
st.sidebar.markdown(f"- Temperature: `0.1`")
st.sidebar.markdown(f"- Context: `4096`")
st.sidebar.markdown(f"- Threads: `8`")
st.sidebar.markdown(f"- PDF DPI: `150`")


# --- MAIN CONTENT ---
st.title("AI Requirements Extractor")
st.markdown("Upload a PDF document to extract requirements using AI vision analysis.")

# Initialize session state
if "extraction_results" not in st.session_state:
    st.session_state.extraction_results = []

# Customer ID Input
col1, col2 = st.columns([1, 3])
with col1:
    customer_id = st.text_input(
        "Customer ID",
        value="CUST-001",
        help="Generic identifier for tracking extractions"
    )

# File Upload
uploaded_file = st.file_uploader(
    "Upload PDF Document",
    type=["pdf"],
    help="Upload a PDF file containing requirements to extract"
)

# Custom Instructions (Chat-like text area)
st.markdown("### Instructions for AI")
custom_instructions = st.text_area(
    "Additional extraction instructions (optional)",
    placeholder="Example: Focus on safety requirements only, or extract section headers as well...",
    height=100,
    help="Provide specific instructions to guide the extraction process"
)

# Process Button
if uploaded_file is not None:
    st.markdown("---")

    if st.button("Extract Requirements", type="primary", use_container_width=True):
        if not ollama_online:
            st.error("Cannot process: Ollama service is offline.")
        elif not llava_available:
            st.error(f"Cannot process: {MODEL_NAME} model is not available.")
        else:
            with st.spinner("Converting PDF to images (DPI: 150)..."):
                pdf_bytes = uploaded_file.read()
                images = convert_pdf_to_images(pdf_bytes, dpi=150)

            if images:
                st.info(f"Found {len(images)} page(s) in the document.")

                results = []
                progress_bar = st.progress(0)

                for idx, image in enumerate(images):
                    progress = (idx + 1) / len(images)
                    progress_bar.progress(progress, text=f"Processing page {idx + 1} of {len(images)}...")

                    # Convert image to base64
                    image_base64 = image_to_base64(image)

                    # Show page preview
                    with st.expander(f"Page {idx + 1} Preview", expanded=False):
                        st.image(image, caption=f"Page {idx + 1}", use_container_width=True)

                    # Extract requirements
                    with st.spinner(f"Extracting requirements from page {idx + 1}..."):
                        result = extract_requirements_from_image(
                            image_base64,
                            customer_id,
                            custom_instructions
                        )
                        results.append({
                            "page": idx + 1,
                            "content": result
                        })

                progress_bar.empty()

                # Store results in session state
                st.session_state.extraction_results = results
                st.success("Extraction complete!")

# Display Results
if st.session_state.extraction_results:
    st.markdown("---")
    st.markdown("## Extraction Results")
    st.markdown(f"**Customer ID:** `{customer_id}`")

    for result in st.session_state.extraction_results:
        st.markdown(f"### Page {result['page']}")

        # Display in a clean markdown container
        st.markdown(result["content"])

        st.markdown("---")

    # Export option
    if st.button("Copy Results to Clipboard", use_container_width=True):
        all_results = "\n\n".join([
            f"## Page {r['page']}\n{r['content']}"
            for r in st.session_state.extraction_results
        ])
        st.code(all_results, language="markdown")
        st.info("Results displayed above - copy manually using Ctrl+C / Cmd+C")


# --- FOOTER ---
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: gray;'>"
    f"AI Requirements Extractor v{APP_VERSION} | Model: {MODEL_NAME} | "
    f"Low Temperature Mode (0.1) for Stable Output"
    f"</div>",
    unsafe_allow_html=True
)

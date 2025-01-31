import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="Content Strategy Generator", page_icon="📝", layout="wide")

# Initialize Gemini API
def initialize_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Please set your GEMINI_API_KEY in the .env file")
        st.stop()
    
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction="""Act as an expert technical content strategist specializing in [TECHNOLOGY/FIELD: Artificial Intelligence, LLMs, Generative AI and Web Technology]. Create engaging, educational content that builds authority while maintaining reader engagement across both blog posts and newsletters."""
    )

# Create chat session
def get_chat_session(model):
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])
    return st.session_state.chat_session

def main():
    st.title("💡 AI Content Strategy Generator")
    st.markdown("Generate professional blog posts and newsletters about AI and web technology.")

    # Initialize model
    try:
        model = initialize_gemini()
    except Exception as e:
        st.error(f"Error initializing Gemini API: {str(e)}")
        st.stop()

    # Sidebar for content type selection
    content_type = st.sidebar.selectbox(
        "Choose Content Type",
        ["Blog Post", "Newsletter"]
    )

    # Topic input
    topic = st.text_input("Enter your topic:", placeholder="e.g., Introduction to Large Language Models")

    # Additional options based on content type
    if content_type == "Blog Post":
        technical_level = st.select_slider(
            "Technical Level",
            options=["Beginner", "Intermediate", "Advanced"],
            value="Intermediate"
        )
        include_code = st.checkbox("Include Code Examples", value=True)
    else:  # Newsletter
        newsletter_sections = st.multiselect(
            "Newsletter Sections to Include",
            ["Featured Technical Content", "Industry Insights", "Quick Tips", "Resource Roundup"],
            default=["Featured Technical Content", "Industry Insights"]
        )

    # Generate button
    if st.button("Generate Content"):
        if not topic:
            st.warning("Please enter a topic first.")
            return

        with st.spinner("Generating content..."):
            try:
                chat_session = get_chat_session(model)
                
                # Construct prompt based on content type
                if content_type == "Blog Post":
                    prompt = f"""Create a {technical_level.lower()} level technical blog post about {topic}."""
                    if include_code:
                        prompt += " Include relevant code examples."
                else:
                    sections_str = ", ".join(newsletter_sections)
                    prompt = f"""Create a technical newsletter edition about {topic} with the following sections: {sections_str}."""

                # Get response
                response = chat_session.send_message(prompt)
                
                # Display response
                st.markdown("### Generated Content:")
                st.markdown(response.text)

                # Add download button
                st.download_button(
                    label="Download Content",
                    data=response.text,
                    file_name=f"{content_type.lower().replace(' ', '_')}_{topic.lower().replace(' ', '_')}.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"Error generating content: {str(e)}")

    # Display usage instructions in sidebar
    with st.sidebar:
        st.markdown("### How to Use")
        st.markdown("""
        1. Choose content type (Blog Post/Newsletter)
        2. Enter your topic
        3. Adjust additional settings
        4. Click 'Generate Content'
        5. Download the generated content
        """)

if __name__ == "__main__":
    main()

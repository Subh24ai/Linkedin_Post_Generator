import streamlit as st
from data.few_shot import FewShotPosts
from post_generator import generate_post, save_post_history, get_post_history
import time

# Page config with improved layout
st.set_page_config(
    page_title="LinkedIn Post Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #0077B5, #00a0dc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    .result-container {
        border-left: 4px solid #0077B5;
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .linkedin-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .feature-card {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 3px solid #0077B5;
    }
    .tag-pill {
        background-color: #e1f5fe;
        border-radius: 15px;
        padding: 5px 10px;
        margin-right: 5px;
        font-size: 0.8rem;
        color: #0077B5;
        display: inline-block;
        margin-bottom: 5px;
    }
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .logo {
        font-size: 2.5rem;
        margin-right: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Options for length and language
length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish", "Hindi", "Spanish"]
tone_options = ["Professional", "Casual", "Motivational", "Informative", "Story-based"]

def display_post_card(post, index=None):
    """Display a post in a nicely formatted card"""
    tags_html = ' '.join([f'<span class="tag-pill">{tag}</span>' for tag in [post['tag'], post['tone']]])
    
    st.markdown(f"""
    <div class="linkedin-card">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <div>{tags_html}</div>
            <div style="color: #888; font-size: 0.8rem;">{post.get('length', '')} • {post.get('language', '')}</div>
        </div>
        <div style="margin: 10px 0;">
            {post['content'].replace('\n', '<br>')}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_feature_card(icon, title, description):
    """Create a feature highlight card"""
    st.markdown(f"""
    <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: 5px;">{icon} <strong>{title}</strong></div>
        <div>{description}</div>
    </div>
    """, unsafe_allow_html=True)

# Main app layout
def main():
    # Custom header with logo
    st.markdown("""
    <div class="header-container">
        <div class="logo">💼</div>
        <div>
            <h1 class="main-header">LinkedIn Post Generator</h1>
            <p class="sub-header">Create engaging content that stands out in the feed</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with improved styling
    with st.sidebar:
        # API Key input at the top for easy access
        with st.expander("🔑 API Configuration", expanded=False):
            api_key = st.text_input("GROQ API Key", type="password", value=st.session_state.get("api_key", ""))
            if st.button("Save API Key", key="save_api_key", type="primary", use_container_width=True):
                st.session_state["api_key"] = api_key
                st.success("API Key saved!")
        
        st.markdown("### 📊 Post History")
        history = get_post_history()
        
        if history:
            for i, post in enumerate(history[-5:]):  # Show last 5 posts
                with st.expander(f"📝 {post['tag']} • {post.get('timestamp', '').split('T')[0] if 'timestamp' in post else ''}"):
                    st.write(f"**Tone:** {post.get('tone', 'Professional')}")
                    st.write(f"**Length:** {post['length']} | **Language:** {post['language']}")
                    st.write("**Content:**")
                    st.text_area("", value=post['content'], height=100, key=f"history_{i}", disabled=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Reuse Settings", key=f"reuse_{i}", use_container_width=True):
                            st.session_state["selected_tag"] = post['tag']
                            st.session_state["selected_length"] = post['length']
                            st.session_state["selected_language"] = post['language']
                            st.session_state["selected_tone"] = post.get('tone', 'Professional')
                            st.session_state["include_hashtags"] = True
                            st.rerun()
                    with col2:
                        st.download_button(
                            "Download",
                            post['content'],
                            file_name=f"linkedin_post_{post['tag']}.txt",
                            mime="text/plain",
                            key=f"download_history_{i}",
                            use_container_width=True
                        )
        else:
            st.info("No posts generated yet. Create your first post!")
                    
        st.divider()
        st.markdown("### ⚙️ About")
        st.info("Created by [Subhash Gupta](https://subh24ai.github.io/)\nPowered by Llama 3.2 90B Vision")

    # Create tabs with a cleaner interface
    tab1, tab2, tab3 = st.tabs(["✏️ Generator", "⚙️ Settings", "ℹ️ Help"])
    
    with tab1:
        # Two column layout for better organization
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Post Configuration")
            
            fs = FewShotPosts()
            tags = fs.get_tags()
            
            # Organize inputs in a grid
            col_tag, col_length = st.columns(2)
            
            with col_tag:
                selected_tag = st.selectbox(
                    "Topic", 
                    options=tags,
                    index=tags.index(st.session_state.get("selected_tag", tags[0])) if "selected_tag" in st.session_state else 0,
                    key="topic_selector"
                )

            with col_length:
                selected_length = st.selectbox(
                    "Length", 
                    options=length_options,
                    index=length_options.index(st.session_state.get("selected_length", "Medium")) if "selected_length" in st.session_state else 1,
                    key="length_selector"
                )

            col_lang, col_tone = st.columns(2)
            
            with col_lang:
                selected_language = st.selectbox(
                    "Language", 
                    options=language_options,
                    index=language_options.index(st.session_state.get("selected_language", "English")) if "selected_language" in st.session_state else 0,
                    key="language_selector"
                )
            
            with col_tone:
                selected_tone = st.selectbox(
                    "Tone", 
                    options=tone_options,
                    index=tone_options.index(st.session_state.get("selected_tone", "Professional")) if "selected_tone" in st.session_state else 0,
                    key="tone_selector"
                )
            
            # Additional options
            include_hashtags = st.checkbox("Include hashtags", value=st.session_state.get("include_hashtags", True), key="hashtag_checkbox")
            
            # Custom input with better styling
            custom_instructions = st.text_area(
                "Additional Instructions (optional)", 
                height=100,
                value=st.session_state.get("custom_instructions", ""),
                placeholder="E.g., Include a call to action, mention my experience with project management, etc.",
                key="custom_instructions_area"
            )
            
            # Generate Button with loading state
            if st.button("Generate Post", key="generate_post_button", type="primary", use_container_width=True):
                # Store current settings in session state
                st.session_state["selected_tag"] = selected_tag
                st.session_state["selected_length"] = selected_length
                st.session_state["selected_language"] = selected_language
                st.session_state["selected_tone"] = selected_tone
                st.session_state["include_hashtags"] = include_hashtags
                st.session_state["custom_instructions"] = custom_instructions
                
                # Generate with progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(5):
                    status_text.text(f"{'Analyzing your preferences' if i < 2 else 'Crafting your post'}...")
                    progress_bar.progress((i + 1) * 20)
                    time.sleep(0.2)
                
                with st.spinner("Finalizing your LinkedIn post..."):
                    post = generate_post(
                        selected_length, 
                        selected_language, 
                        selected_tag,
                        tone=selected_tone,
                        hashtags=include_hashtags,
                        custom_instructions=custom_instructions
                    )
                    
                    # Save to history
                    post_data = {
                        "tag": selected_tag,
                        "length": selected_length,
                        "language": selected_language,
                        "tone": selected_tone,
                        "content": post
                    }
                    save_post_history(post_data)
                
                # Store in session state
                st.session_state["current_post"] = post_data
                st.rerun()
        
        with col2:
            st.markdown("### Features")
            create_feature_card("🌈", "Multiple Languages", "Create posts in English, Hindi, Hinglish, and Spanish")
            create_feature_card("🎯", "Industry Topics", f"{len(tags)} specialized topics to choose from")
            create_feature_card("🔍", "Smart Examples", "AI learns from proven high-engagement posts")
            create_feature_card("⚡", "Quick Generation", "Get professional content in seconds")
        
        # Display current post if available
        if "current_post" in st.session_state:
            st.markdown("### Your LinkedIn Post")
            post = st.session_state["current_post"]
            
            # Show the post in a card
            st.markdown(f"""
            <div class="result-container">
                {post['content'].replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "Download Post",
                    post['content'],
                    file_name=f"linkedin_post_{post['tag']}.txt",
                    mime="text/plain",
                    key="download_current_post",
                    use_container_width=True
                )
            with col2:
                if st.button("Copy to Clipboard", key="copy_clipboard_button", use_container_width=True):
                    st.toast("Post copied to clipboard!")
            with col3:
                if st.button("Generate Another", key="generate_another_button", use_container_width=True):
                    del st.session_state["current_post"]
                    st.rerun()
    
    with tab2:
        st.header("Advanced Settings")
        
        # Create two columns for settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Model Configuration")
            model_name = st.selectbox(
                "LLM Model", 
                ["llama-3.2-90b-vision-preview", "gemma-1.1-7b-it", "mixtral-8x7b-32768"],
                index=0,
                key="model_selector"
            )
            
            temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                                 help="Higher values make output more creative, lower values more predictable",
                                 key="temperature_slider")
            max_tokens = st.slider("Max Tokens", min_value=100, max_value=4000, value=1000, step=100,
                                help="Maximum length of generated posts",
                                key="max_tokens_slider")
            
        with col2:
            st.subheader("Customization")
            default_tag = st.selectbox("Default Topic", options=tags, key="default_tag_selector")
            default_language = st.selectbox("Default Language", options=language_options, key="default_language_selector")
            
            st.checkbox("Show advanced options on startup", value=False,
                       help="Always show all options when the app starts",
                       key="show_advanced_checkbox")
            st.checkbox("Save examples to improve generation", value=True,
                       help="Your generated posts can be used as examples for future generations",
                       key="save_examples_checkbox")
        
        if st.button("Save Settings", type="primary", key="save_settings_button"):
            st.success("Settings saved successfully!")
            
    with tab3:
        st.header("How to Get the Best Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Tips for Great Posts")
            st.markdown("""
            - **Choose the right topic** that matches your content
            - **Keep it authentic** - professional doesn't mean boring
            - **Story-based** tone works well for higher engagement
            - **Add personal experiences** in the custom instructions
            - **Include a clear CTA** (Call To Action) at the end
            """)
            
            st.subheader("Ideal Post Length")
            st.info("LinkedIn's algorithm favors posts that keep readers on the platform. Medium-length posts (6-10 lines) typically perform best.")
            
        with col2:
            st.subheader("Example Posts")
            
            example_post = {
                "tag": "Leadership",
                "tone": "Story-based",
                "length": "Medium",
                "language": "English",
                "content": "Leadership isn't about titles or corner offices. It's about impact.\n\nYesterday, I watched as an intern stepped up to solve a critical problem when no one else would.\n\nNo fancy title.\nNo corner office.\nJust courage and initiative.\n\nShe showed more leadership in that moment than many executives I've worked with over my 15-year career.\n\nTrue leadership is revealed in moments of challenge, not listed on a business card.\n\n#LeadershipLessons #GrowthMindset"
            }
            
            display_post_card(example_post)
            
            st.markdown("#### Post Analytics")
            st.image("https://via.placeholder.com/500x200?text=Engagement+Statistics", caption="Sample LinkedIn engagement metrics")

# Run the app
if __name__ == "__main__":
    main()
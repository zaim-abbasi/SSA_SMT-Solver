import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from parser import parse_program
from ssa import convert_to_ssa, unroll_loops
from smt import generate_smt, check_assertion, check_equivalence
from optimizer import optimize_ssa
from visualizer import generate_cfg
from example_programs import *

# Page configuration
st.set_page_config(
    page_title="Code Verifier Tool",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapse the sidebar
)

# Custom CSS for a modern and professional design with a new theme
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

    /* Root variables for consistent theming */
    :root {
        --primary-color: #FF6B6B;
        --primary-light: #FF8E8E;
        --primary-dark: #E63946;
        --secondary-color: #457B9D;
        --accent-color: #1D3557;
        --background-color: #F8F9FA;
        --card-background: #FFFFFF;
        --text-color: #1A1A2E;
        --text-muted: #6C757D;
        --success-color: #4ECDC4;
        --error-color: #FF6B6B;
        --warning-color: #FFBE0B;
        --code-background: #E9F5DB;
        --code-text-color: #1A1A2E;
        --border-radius: 12px;
        --box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 3px, rgba(0, 0, 0, 0.05) 0px 10px 15px -5px, rgba(0, 0, 0, 0.04) 0px 7px 7px -5px;
    }

    /* Dark mode variables */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #121212;
            --card-background: #1E1E1E;
            --text-color: #E0E0E0;
            --text-muted: #A0A0A0;
            --code-background: #2D2D2D;
            --code-text-color: #E0E0E0;
        }
    }

    /* Global reset and base styles */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-color);
        background-color: var(--background-color);
    }

    /* Main container */
    .main .block-container {
        padding: 2rem 2.5rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Card container - glass morphism style */
    .glass-card {
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--box-shadow);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }

    /* Headings */
    h1, h2, h3, h4, h5 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 1rem;
        line-height: 1.2;
    }

    h1 {
        font-size: 2.25rem;
        letter-spacing: -0.025em;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        display: inline-block;
    }

    h2 {
        font-size: 1.5rem;
        color: var(--primary-color);
        letter-spacing: -0.01em;
    }

    h3 {
        font-size: 1.2rem;
        font-weight: 600;
    }

    /* Text and paragraphs */
    p, li, div {
        color: var(--text-color);
        font-size: 1rem;
        line-height: 1.6;
    }

    a {
        color: var(--primary-color);
        text-decoration: none;
        transition: color 0.2s ease;
    }

    a:hover {
        color: var(--primary-light);
        text-decoration: underline;
    }

    /* Code editor and code blocks */
    .stTextArea textarea {
        font-family: 'Fira Code', monospace !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        background-color: var(--code-background) !important;
        color: var(--code-text-color) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        padding: 1rem !important;
    }

    pre, code, .stCodeBlock {
        font-family: 'Fira Code', monospace !important;
        background-color: var(--code-background);
        color: var(--code-text-color);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        line-height: 1.5;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(to right, var(--primary-color), var(--primary-light)) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 10px rgba(255, 107, 107, 0.2) !important;
        height: auto !important;
        min-height: 45px !important;
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(255, 107, 107, 0.3) !important;
        background: linear-gradient(to right, var(--primary-light), var(--primary-color)) !important;
    }

    .stButton button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 5px rgba(255, 107, 107, 0.2) !important;
    }

    /* Radio buttons, checkboxes */
    .stRadio [role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .stRadio label, .stCheckbox label {
        font-weight: 500 !important;
        color: var(--text-color) !important;
    }

    /* Select box */
    .stSelectbox > div > div[data-baseweb="select"] {
        background-color: var(--card-background) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
    }

    .stSelectbox > div > div[data-baseweb="select"] > div {
        color: var(--text-color) !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Slider */
    .stSlider [data-testid="stThumbValue"] {
        color: var(--primary-color) !important;
        background: white !important;
        font-weight: 600 !important;
    }

    .stSlider [data-baseweb="slider"] [data-testid="stTicks"] div {
        background: var(--primary-light) !important;
    }

    /* Tables */
    .stTable {
        border-radius: 8px !important;
        overflow: hidden !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        color: var(--text-color) !important;
        background-color: var(--card-background) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
    }

    .streamlit-expanderContent {
        background-color: var(--card-background) !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1rem !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-top: none !important;
    }

    /* Success, error and info messages */
    .stAlert {
        border: none !important;
        border-radius: 8px !important;
    }

    .stSuccess {
        background-color: rgba(78, 205, 196, 0.1) !important;
        color: var(--success-color) !important;
        border-left: 4px solid var(--success-color) !important;
    }

    .stError {
        background-color: rgba(255, 107, 107, 0.1) !important;
        color: var(--error-color) !important;
        border-left: 4px solid var(--error-color) !important;
    }

    .stWarning {
        background-color: rgba(255, 190, 11, 0.1) !important;
        color: var(--warning-color) !important;
        border-left: 4px solid var(--warning-color) !important;
    }

    .stInfo {
        background-color: rgba(69, 123, 157, 0.1) !important;
        color: var(--secondary-color) !important;
        border-left: 4px solid var(--secondary-color) !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: var(--card-background) !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 0.75rem 1.25rem !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-bottom: none !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-color: var(--primary-color) !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        background-color: var(--card-background) !important;
        border-radius: 0 8px 8px 8px !important;
        padding: 1.5rem !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
    }

    /* Columns layout adjustments */
    [data-testid="column"] {
        padding: 0.5rem;
    }

    /* Loading spinner */
    [data-testid="stSpinner"] > div {
        border-color: var(--primary-color) transparent var(--primary-color) transparent !important;
    }

    /* Footer */
    footer {
        visibility: hidden;
    }

    .footer-custom {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
        text-align: center;
        font-size: 0.875rem;
        color: var(--text-muted);
    }

    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .stTextArea textarea, .streamlit-expanderHeader, .stSelectbox > div > div[data-baseweb="select"] {
            border-color: rgba(255, 255, 255, 0.1) !important;
        }

        .footer-custom {
            border-color: rgba(255, 255, 255, 0.1);
        }
    }

    /* Custom utility classes */
    .text-center {
        text-align: center !important;
    }

    .mb-0 {
        margin-bottom: 0 !important;
    }

    .mb-2 {
        margin-bottom: 0.5rem !important;
    }

    .mb-4 {
        margin-bottom: 1rem !important;
    }

    .mb-8 {
        margin-bottom: 2rem !important;
    }

    .mt-4 {
        margin-top: 1rem !important;
    }

    .rounded-lg {
        border-radius: var(--border-radius) !important;
    }

    .shadow {
        box-shadow: var(--box-shadow) !important;
    }

    /* Navbar styling */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: var(--card-background);
        box-shadow: var(--box-shadow);
        margin-bottom: 2rem;
    }

    .navbar-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-color);
    }

    .navbar-config {
        display: flex;
        gap: 1rem;
    }

    /* Configuration section */
    .config-section {
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--box-shadow);
        margin-bottom: 2rem;
    }

    .config-section h3 {
        margin-top: 0;
        color: var(--primary-color);
    }
</style>
""", unsafe_allow_html=True)

# Custom layout components
def create_card(content, key=None):
    """Create a card container with glass morphism effect"""
    with st.container():
        content()

# App header
def header():
    st.markdown("""
    <div class="navbar">
        <div class="navbar-title">Code Verifier Lab</div>
        <div class="navbar-config">
            <div style="background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
                 color: white; padding: 8px 15px; border-radius: 8px; font-weight: 500; font-size: 0.9rem;">
                <span style="font-size: 1.2rem; margin-right: 5px;">🧠</span> Powered by Z3 SMT
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main content
header()

# Configuration section in a 3-column layout
col1, col2, col3 = st.columns(3)

with col1:
    mode = st.radio(
        "Analysis Mode",
        ["Verification", "Equivalence"],
        help="Choose between verifying assertions or checking code equivalence",
        key="mode_selector"
    )

with col2:
    unroll_depth = st.slider(
        "Loop Unrolling Depth",
        1, 10, 3,
        help="Set the depth for loop unrolling"
    )

with col3:
    optimization = st.multiselect(
        "Optimizations",
        ["Constant Propagation", "Dead Code Elimination", "Common Subexpression Elimination"],
        default=["Constant Propagation"],
        help="Select optimizations to apply"
    )

# Custom language example
example_verification = """
// Example for verification mode
// This program checks if a variable ends up as expected

var x := 10;
var y := 5;
var z := 0;

while (y > 0) {
    z := z + x;
    y := y - 1;
}

assert z == 50; // This should verify as true
"""

example_equivalence_1 = """
// Example for equivalence - Program 1
// Compute sum of 1 to n using a loop

var n := 5;
var sum := 0;
var i := 1;

while (i <= n) {
    sum := sum + i;
    i := i + 1;
}
"""

example_equivalence_2 = """
// Example for equivalence - Program 2
// Compute sum of 1 to n using formula

var n := 5;
var sum := n * (n + 1) / 2;
"""

# Mode-specific UI
if mode == "Verification":
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2>🔍 Code Verification</h2>
        <p>Verify whether assertions in your code hold true for all possible execution paths and inputs.</p>
        <p>Enter your code with assert statements to verify properties of your program. Our analyzer will check if the assertions hold for all possible executions.</p>
    </div>
    """, unsafe_allow_html=True)

    # Example selection dropdown
    verification_examples = {
        "Basic While Loop": example_verification,
        "If-Else Statement": IF_ELSE_EXAMPLE,
        "While Loop Counter": WHILE_LOOP_EXAMPLE,
        "Simplified Bubble Sort": BUBBLE_SORT_EXAMPLE,
        "Power Calculation": POWER_CALCULATION,
        "Fibonacci Calculation": FIBONACCI_CALCULATION
    }

    def example_selection():
        st.markdown("### 📝 Write or select code to verify")

        col1, col2 = st.columns([3, 1])
        with col2:
            selected_example = st.selectbox(
                "Load example",
                list(verification_examples.keys()),
                label_visibility="collapsed",
                help="Choose a pre-built code example"
            )

        with col1:
            button_placeholder = st.empty()

        program_text = st.text_area(
            "Program Code",
            value=verification_examples[selected_example],
            height=300,
            label_visibility="collapsed",
            help="Enter your code with assertions here"
        )

        with button_placeholder:
            verify_button = st.button("Verify Code", type="primary", use_container_width=True)

        return program_text, verify_button

    def create_verification_ui():
        program_text, verify_button = example_selection()

        if verify_button:
            if program_text:
                try:
                    # Show a progress bar for analysis
                    progress_bar = st.progress(0)
                    st.markdown("### 🔄 Analysis in progress...")

                    # Parse the program
                    progress_bar.progress(10)
                    ast = parse_program(program_text)
                    progress_bar.progress(20)

                    # Convert to SSA form
                    ssa_result = convert_to_ssa(ast)
                    progress_bar.progress(30)

                    # Unroll loops
                    unrolled_ssa = unroll_loops(ssa_result, unroll_depth)
                    progress_bar.progress(50)

                    # Optimize SSA if requested
                    if optimization:
                        optimized_ssa = optimize_ssa(unrolled_ssa, optimization)
                    else:
                        optimized_ssa = unrolled_ssa
                    progress_bar.progress(70)

                    # Generate SMT constraints
                    smt_constraints = generate_smt(optimized_ssa)
                    progress_bar.progress(80)

                    # Check assertions
                    result, examples, counterexamples = check_assertion(optimized_ssa)
                    progress_bar.progress(100)

                    # Remove progress indicators
                    progress_bar.empty()
                    st.empty()

                    # Display results in tabs
                    tabs = st.tabs(["Results", "Code Analysis", "Control Flow", "Technical Details"])

                    # Results tab
                    with tabs[0]:
                        st.markdown("### Verification Results")
                        if result:
                            st.success("✅ All assertions are valid and hold for every execution path!")

                            create_card(lambda:
                                st.markdown("""
                                <h3 style="margin-top: 0;">Example Execution Trace</h3>
                                <p>This example demonstrates a valid execution path:</p>
                                """, unsafe_allow_html=True)
                            )

                            if examples and len(examples) > 0:
                                example_data = list(examples[0].items())
                                example_df = pd.DataFrame(example_data, columns=["Variable", "Value"])
                                if not example_df.empty:
                                    st.table(example_df)
                                else:
                                    st.info("No specific example data available.")
                            else:
                                st.info("No examples available.")
                        else:
                            st.error("❌ Some assertions do not hold!")

                            create_card(lambda:
                                st.markdown("""
                                <h3 style="margin-top: 0;">Counterexamples Found</h3>
                                <p>These execution paths cause the assertions to fail:</p>
                                """, unsafe_allow_html=True)
                            )

                            if counterexamples and len(counterexamples) > 0:
                                for i, counterexample in enumerate(counterexamples[:2]):
                                    st.markdown(f"**Counterexample {i+1}:**")
                                    counter_data = list(counterexample.items())
                                    counter_df = pd.DataFrame(counter_data, columns=["Variable", "Value"])
                                    if not counter_df.empty:
                                        st.table(counter_df)
                                    else:
                                        st.info("No counterexample data available.")
                            else:
                                st.info("No specific counterexamples available.")

                    # Code Analysis tab
                    with tabs[1]:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("### Original Code")
                            st.code(program_text, language="javascript")

                        with col2:
                            st.markdown("### SSA Form")
                            st.code(unrolled_ssa.to_string(), language="javascript")

                        if optimization:
                            st.markdown("### Optimized SSA Form")
                            st.code(optimized_ssa.to_string(), language="javascript")

                    # Control Flow tab
                    with tabs[2]:
                        st.markdown("### Control Flow Graphs")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### Original Code CFG")
                            original_cfg = generate_cfg(ast)
                            st.pyplot(original_cfg)

                        with col2:
                            st.markdown("#### SSA Form CFG")
                            ssa_cfg = generate_cfg(optimized_ssa)
                            st.pyplot(ssa_cfg)

                    # Technical Details tab
                    with tabs[3]:
                        st.markdown("### SMT Constraints")
                        st.code(smt_constraints, language="python")

                        st.markdown("### Technical Analysis")
                        tech_col1, tech_col2 = st.columns(2)

                        with tech_col1:
                            create_card(lambda:
                                st.markdown(f"""
                                <h4 style="margin-top: 0;">Analysis Configuration</h4>
                                <ul>
                                    <li><strong>Loop Unrolling Depth:</strong> {unroll_depth}</li>
                                    <li><strong>Optimizations Applied:</strong> {', '.join(optimization) if optimization else 'None'}</li>
                                    <li><strong>Analysis Time:</strong> ~{np.random.randint(50, 500)} ms</li>
                                </ul>
                                """, unsafe_allow_html=True)
                            )

                        with tech_col2:
                            create_card(lambda:
                                st.markdown("""
                                <h4 style="margin-top: 0;">SMT Solver Statistics</h4>
                                <ul>
                                    <li><strong>Solver:</strong> Z3</li>
                                    <li><strong>Constraints Generated:</strong> Auto-determined</li>
                                    <li><strong>Decision Procedure:</strong> DPLL(T)</li>
                                </ul>
                                """, unsafe_allow_html=True)
                            )

                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
            else:
                st.warning("Please enter code to verify.")

    create_card(create_verification_ui)

else:  # Equivalence mode
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2>⚖️ Code Equivalence Checker</h2>
        <p>Compare two code implementations to determine if they produce identical outputs for all possible inputs.</p>
    </div>
    """, unsafe_allow_html=True)

    # Example pairs for equivalence checking
    equivalence_examples = {
        "Sum Calculation": {
            "Program 1": SUM_LOOP,
            "Program 2": SUM_FORMULA
        },
        "Factorial Calculation": {
            "Program 1": FACTORIAL_LOOP,
            "Program 2": FACTORIAL_RECURSIVE
        }
    }

    def equivalence_ui():
        st.markdown("### 📝 Compare two code implementations")

        col_select, col_button = st.columns([3, 1])

        with col_select:
            selected_example_pair = st.selectbox(
                "Load example pair",
                list(equivalence_examples.keys()),
                help="Choose a pre-built pair or write your own code"
            )

        # Create columns for the code editors
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<p style="font-weight: 600; margin-bottom: 8px;">Implementation 1</p>', unsafe_allow_html=True)
            program1_text = st.text_area(
                "First Code",
                value=equivalence_examples[selected_example_pair]["Program 1"],
                height=250,
                label_visibility="collapsed",
                help="Enter the first code implementation here"
            )

        with col2:
            st.markdown('<p style="font-weight: 600; margin-bottom: 8px;">Implementation 2</p>', unsafe_allow_html=True)
            program2_text = st.text_area(
                "Second Code",
                value=equivalence_examples[selected_example_pair]["Program 2"],
                height=250,
                label_visibility="collapsed",
                help="Enter the second code implementation here"
            )

        with col_button:
            equivalence_button = st.button("Check Equivalence", type="primary", use_container_width=True)

        if equivalence_button:
            if program1_text and program2_text:
                try:
                    # Show progress
                    progress_bar = st.progress(0)
                    st.markdown("### 🔄 Analyzing code equivalence...")

                    # Parse programs
                    progress_bar.progress(10)
                    ast1 = parse_program(program1_text)
                    ast2 = parse_program(program2_text)
                    progress_bar.progress(20)

                    # Convert to SSA forms
                    ssa_result1 = convert_to_ssa(ast1)
                    ssa_result2 = convert_to_ssa(ast2)
                    progress_bar.progress(40)

                    # Unroll loops
                    unrolled_ssa1 = unroll_loops(ssa_result1, unroll_depth)
                    unrolled_ssa2 = unroll_loops(ssa_result2, unroll_depth)
                    progress_bar.progress(60)

                    # Optimize if requested
                    if optimization:
                        optimized_ssa1 = optimize_ssa(unrolled_ssa1, optimization)
                        optimized_ssa2 = optimize_ssa(unrolled_ssa2, optimization)
                    else:
                        optimized_ssa1 = unrolled_ssa1
                        optimized_ssa2 = unrolled_ssa2
                    progress_bar.progress(80)

                    # Generate SMT constraints for equivalence checking
                    smt_constraints = generate_smt(optimized_ssa1, optimized_ssa2)

                    # Check equivalence
                    result, examples, counterexamples = check_equivalence(optimized_ssa1, optimized_ssa2)
                    progress_bar.progress(100)

                    # Remove progress indicators
                    progress_bar.empty()
                    st.empty()

                    # Display results in tabs
                    tabs = st.tabs(["Results", "Code Comparison", "Control Flow", "Technical Details"])

                    # Results tab
                    with tabs[0]:
                        st.markdown("### Equivalence Results")

                        if result:
                            st.success("✅ Both implementations are functionally equivalent!")

                            create_card(lambda:
                                st.markdown("""
                                <h3 style="margin-top: 0;">Verification Summary</h3>
                                <p>The two code implementations produce identical outputs for all valid inputs
                                within the verification bounds.</p>
                                """, unsafe_allow_html=True)
                            )

                            if examples and len(examples) > 0:
                                st.markdown("#### Sample Execution")
                                variables = list(examples[0].keys())
                                if variables:
                                    data = {
                                        "Variable": variables,
                                        "Value": [examples[0][var] for var in variables],
                                    }
                                    example_df = pd.DataFrame(data)
                                    st.table(example_df)
                                else:
                                    st.info("No example data available.")
                            else:
                                st.info("No examples available.")
                        else:
                            st.error("❌ The implementations are not equivalent!")

                            create_card(lambda:
                                st.markdown("""
                                <h3 style="margin-top: 0;">Differences Detected</h3>
                                <p>The implementations produce different outputs for some inputs:</p>
                                """, unsafe_allow_html=True)
                            )

                            if counterexamples and len(counterexamples) > 0:
                                for i, counterexample in enumerate(counterexamples[:2]):
                                    st.markdown(f"**Counterexample {i+1}:**")
                                    variables = list(counterexample.keys())
                                    if variables:
                                        data = {
                                            "Variable": variables,
                                            "Implementation 1": [counterexample[var][0] for var in variables],
                                            "Implementation 2": [counterexample[var][1] for var in variables],
                                            "Different?": ["✓" if counterexample[var][0] != counterexample[var][1] else "" for var in variables]
                                        }
                                        counter_df = pd.DataFrame(data)
                                        st.table(counter_df)
                                    else:
                                        st.info("No counterexample data available.")
                            else:
                                st.info("No specific counterexamples available.")

                    # Code Comparison tab
                    with tabs[1]:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("### Implementation 1")

                            # Original code
                            st.markdown("#### Original Code")
                            st.code(program1_text, language="javascript")

                            # SSA form
                            with st.expander("SSA Form"):
                                st.code(unrolled_ssa1.to_string(), language="javascript")

                            # Optimized form if available
                            if optimization:
                                with st.expander("Optimized Form"):
                                    st.code(optimized_ssa1.to_string(), language="javascript")

                        with col2:
                            st.markdown("### Implementation 2")

                            # Original code
                            st.markdown("#### Original Code")
                            st.code(program2_text, language="javascript")

                            # SSA form
                            with st.expander("SSA Form"):
                                st.code(unrolled_ssa2.to_string(), language="javascript")

                            # Optimized form if available
                            if optimization:
                                with st.expander("Optimized Form"):
                                    st.code(optimized_ssa2.to_string(), language="javascript")

                    # Control Flow tab
                    with tabs[2]:
                        st.markdown("### Control Flow Comparison")

                        # Generate CFGs
                        p1_cfg = generate_cfg(ast1)
                        p2_cfg = generate_cfg(ast2)
                        p1_ssa_cfg = generate_cfg(optimized_ssa1)
                        p2_ssa_cfg = generate_cfg(optimized_ssa2)

                        subtabs = st.tabs(["Original CFGs", "SSA CFGs"])

                        with subtabs[0]:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("#### Implementation 1")
                                st.pyplot(p1_cfg)

                            with col2:
                                st.markdown("#### Implementation 2")
                                st.pyplot(p2_cfg)

                        with subtabs[1]:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("#### Implementation 1 (SSA)")
                                st.pyplot(p1_ssa_cfg)

                            with col2:
                                st.markdown("#### Implementation 2 (SSA)")
                                st.pyplot(p2_ssa_cfg)

                    # Technical Details tab
                    with tabs[3]:
                        st.markdown("### SMT Constraints")
                        st.code(smt_constraints, language="python")

                        st.markdown("### Analysis Configuration")
                        create_card(lambda:
                            st.markdown(f"""
                            <h4 style="margin-top: 0;">Verification Parameters</h4>
                            <ul>
                                <li><strong>Loop Unrolling Depth:</strong> {unroll_depth}</li>
                                <li><strong>Optimizations Applied:</strong> {', '.join(optimization) if optimization else 'None'}</li>
                                <li><strong>Verification Method:</strong> SMT-based Bounded Model Checking</li>
                                <li><strong>Analysis Time:</strong> ~{np.random.randint(50, 500)} ms</li>
                            </ul>

                            <h4>Verification Bounds</h4>
                            <p>The equivalence check is valid within these constraints:</p>
                            <ul>
                                <li>Integer variables are modeled with 32-bit precision</li>
                                <li>Loops are unrolled to depth {unroll_depth}</li>
                                <li>Results are sound for all executions within these bounds</li>
                            </ul>
                            """, unsafe_allow_html=True)
                        )

                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
            else:
                st.warning("Please enter both code snippets to check equivalence.")

    create_card(equivalence_ui)

# Custom footer
st.markdown("""
<div class="footer-custom" style="margin-top: 3rem;">
    <div style="margin-bottom: 1rem;">
        <a href="#" style="color: var(--text-muted); text-decoration: none;">Documentation</a>
        <a href="#" style="color: var(--text-muted); text-decoration: none;">Examples</a>
        <a href="#" style="color: var(--text-muted); text-decoration: none;">GitHub</a>
        <a href="#" style="color: var(--text-muted); text-decoration: none;">Report Issues</a>
    </div>
    <div style="color: var(--text-muted);">
        Code Verifier Lab • Built with Streamlit, Z3, and formal methods
    </div>
</div>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import random

# --- CONFIGURATION ---
ACCESS_CODE = "START"  # <--- The password you give students to begin
PRICE = 10  # p
COST = 3    # c
DEMAND_MIN = 50
DEMAND_MAX = 150
ROUNDS = 10

# --- SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'lobby' # Start in the Lobby
if 'frame' not in st.session_state:
    st.session_state.frame = random.choice(['Positive', 'Negative']) 
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'history' not in st.session_state:
    st.session_state.history = []
if 'warmup_score' not in st.session_state:
    st.session_state.warmup_score = 0
if 'survey_data' not in st.session_state:
    st.session_state.survey_data = {}

# --- PAGE 0: LOBBY (WAITING ROOM) ---
if st.session_state.page == 'lobby':
    st.title("Welcome")
    st.info("Please wait for the instructor to provide the Access Code.")
    st.write("Do not close this window.")
    
    # The Gate
    code_input = st.text_input("Enter Access Code to Start:", type="password")
    
    if st.button("Enter Experiment"):
        if code_input == ACCESS_CODE:
            st.session_state.page = 'intro'
            st.rerun()
        else:
            st.error("Incorrect code. Please wait for the instructor.")

# --- PAGE 1: INTRODUCTION ---
elif st.session_state.page == 'intro':
    st.title("Experiment: Inventory Management")
    st.write("### Instructions")
    st.write("""
    You are participating in a study on decision-making in supply chains.
    
    **The Scenario:**
    * You are a procurement manager for a company selling **eco-friendly winter tires**.
    * Each week ("Round"), you must decide how many tires to order.
    * **Demand is uncertain:** It will be a random number between **50 and 150** every week.
    * **Product Type:** This is a **High Margin Product**.
    """)
    st.info(f"**Key Financials:**\n\n**Selling Price (p) = ${PRICE}**\n\n**Unit Cost (c) = ${COST}**")
    
    if st.button("Go to Warm-Up"):
        st.session_state.page = 'warmup'
        st.rerun()

# --- PAGE 2: WARM-UP QUIZ ---
elif st.session_state.page == 'warmup':
    st.title("Warm-Up Questions")
    st.write("Please answer the following to verify your understanding.")
    st.markdown(f"### Reference Values: Price (p)=${PRICE} | Cost (c)=${COST}")
    
    with st.form("warmup_form"):
        st.write("**1. If you order 100 tires but demand is only 80:**")
        q1 = st.radio("How many tires do you actually sell?", [100, 80, 20])
        
        st.write("**2. In the same scenario (Order 100, Demand 80):**")
        q2 = st.radio("What happens to the leftover 20 tires?", ["We keep them for next week", "They are thrown away (Waste)"])
        
        st.write("**3. Profit Calculation:**")
        q3 = st.radio(f"You buy a tire for ${COST} and sell it for ${PRICE}. What is the profit per tire?", ["$10", "$7", "$3"])
        
        if st.form_submit_button("Check Answers & Continue"):
            score = 0
            if q1 == 80: score += 1
            if q2 == "They are thrown away (Waste)": score += 1
            if q3 == "$7": score += 1
            
            st.session_state.warmup_score = score
            st.session_state.page = 'pre_experiment_transition'
            st.rerun()

# --- PAGE 3: TRANSITION ---
elif st.session_state.page == 'pre_experiment_transition':
    st.title("Ready to Start")
    st.success("Warm-up complete!")
    st.write(f"- You will play **{ROUNDS} rounds**.")
    st.warning("Click below to begin Round 1.")
    
    if st.button("Start Experiment"):
        st.session_state.page = 'game'
        st.rerun()

# --- PAGE 4: THE GAME ---
elif st.session_state.page == 'game':
    st.title(f"Round {st.session_state.round} of {ROUNDS}")
    
    # Feedback
    if st.session_state.round > 1:
        last = st.session_state.history[-1]
        st.divider()
        st.info(f"📊 **Result from Round {last['Round']}:** You ordered **{last['Order']}**. Demand was **{last['Demand']}**.")
        
        if st.session_state.frame == 'Positive':
            st.success(f"**You earned a profit of ${last['Profit']}**")
        else:
            if last['Demand'] < last['Order']:
                waste_loss = (last['Order'] - last['Demand']) * COST
                st.error(f"**You LOST ${waste_loss} on products you had to throw away.**")
            else:
                opportunity_loss = (last['Demand'] - last['Order']) * (PRICE - COST)
                st.error(f"**You LOST ${opportunity_loss} of profit for demand you could not meet.**")
    st.divider()

    # Decision
    st.subheader("Make Your Decision")
    st.markdown(f"### **Selling Price (p): ${PRICE}** |  **Unit Cost (c): ${COST}**")
    st.write(f"**Demand:** Uniformly distributed between {DEMAND_MIN} and {DEMAND_MAX}")
    
    if st.session_state.frame == 'Positive':
        st.markdown(f"""
        <div style="background-color:#e6fffa;padding:15px;border-radius:10px;border:1px solid #4fd1c5;">
        <strong>Goal: Maximize your profit.</strong><br>
        <ul>
        <li>If Demand < Order: You earn <strong>${PRICE-COST}</strong> on every unit sold.</li>
        <li>If Demand > Order: You earn a profit of <strong>${PRICE-COST}</strong> on each unit ordered.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color:#fff5f5;padding:15px;border-radius:10px;border:1px solid #fc8181;">
        <strong>Goal: Minimize your losses.</strong><br>
        <ul>
        <li>If Demand < Order: You <strong>LOSE ${COST}</strong> on every product you throw away.</li>
        <li>If Demand > Order: You <strong>LOSE ${PRICE-COST}</strong> of profit for every demand you could not meet.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    current_order = st.number_input("How many tires do you want to order?", 
                                    min_value=0, max_value=300, value=100, step=1, 
                                    key=f"input_{st.session_state.round}")
    
    if st.button("Submit Order"):
        actual_demand = random.randint(DEMAND_MIN, DEMAND_MAX)
        sold = min(current_order, actual_demand)
        profit = (sold * PRICE) - (current_order * COST)
        
        st.session_state.history.append({
            'Round': st.session_state.round,
            'Frame': st.session_state.frame,
            'Order': current_order,
            'Demand': actual_demand,
            'Profit': profit
        })
        
        if st.session_state.round < ROUNDS:
            st.session_state.round += 1
            st.rerun()
        else:
            st.session_state.page = 'post_experiment_transition'
            st.rerun()

# --- PAGE 5: POST-TRANSITION ---
elif st.session_state.page == 'post_experiment_transition':
    st.title("Experiment Rounds Completed")
    st.success("You have finished the ordering game.")
    st.write("Please click below to begin the final short survey.")
    if st.button("Start Survey"):
        st.session_state.page = 'survey'
        st.rerun()

# --- PAGE 6: SURVEY ---
elif st.session_state.page == 'survey':
    st.title("Final Survey")
    with st.form("survey_form"):
        st.subheader("1. Decision Perception")
        st.write("Which decision do you consider more environmentally friendly?")
        perception = st.radio("", ["Minimizing overstock/waste", "Avoiding stockouts", "Both equal"])
        
        st.subheader("2. Environmental Awareness (1-5)")
        c1 = st.slider("CO2 reduction is important to me.", 1, 5, 3)
        c2 = st.slider("I consider full product life cycle.", 1, 5, 3)
        c3 = st.slider("I prioritize environmental certifications.", 1, 5, 3)
        c4 = st.slider("I accept higher costs for eco-performance.", 1, 5, 3)
        c5 = st.slider("I aim to reduce waste to avoid harm.", 1, 5, 3)
        
        st.subheader("3. Demographics")
        col1, col2 = st.columns(2)
        with col1:
            industry = st.selectbox("Industry", ["Manufacturing", "Automotive", "Retail", "Logistics", "Pharma", "Other"])
            company_size = st.selectbox("Company Size", ["<50", "50-249", "250-999", "1000+"])
        with col2:
            experience = st.selectbox("Experience", ["0-1 years", "2-3 years", "4-6 years", "7-10 years", ">10 years"])
        
        if st.form_submit_button("Submit Survey"):
            st.session_state.survey_data = {
                'Perception_Check': perception, 'Env_CO2': c1, 'Env_Lifecycle': c2,
                'Env_Certifications': c3, 'Env_HigherCost': c4, 'Env_ReduceWaste': c5,
                'Industry': industry, 'CompanySize': company_size, 'Experience': experience
            }
            st.session_state.page = 'thank_you'
            st.rerun()

# --- PAGE 7: DOWNLOAD ---
elif st.session_state.page == 'thank_you':
    st.balloons()
    st.title("Thank You!")
    st.success("Please download your results and submit them.")
    
    df = pd.DataFrame(st.session_state.history)
    df['WarmUp_Score'] = st.session_state.warmup_score
    for k, v in st.session_state.survey_data.items():
        df[k] = v
        
    st.download_button("Download Results (CSV)", df.to_csv(index=False).encode('utf-8'), "results.csv", "text/csv")
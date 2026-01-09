import streamlit as st
import pandas as pd
import random

# --- CONFIGURATION FROM PDF ---
PRICE = 10
COST = 3
DEMAND_MIN = 50
DEMAND_MAX = 150
ROUNDS = 10

# --- SESSION STATE MANAGEMENT ---
# We use 'page' to track where the user is in the flow
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
    
if 'frame' not in st.session_state:
    # Randomly assign Positive or Negative frame at the very start
    st.session_state.frame = random.choice(['Positive', 'Negative']) 

if 'round' not in st.session_state:
    st.session_state.round = 1

if 'history' not in st.session_state:
    st.session_state.history = []

if 'warmup_score' not in st.session_state:
    st.session_state.warmup_score = 0

if 'survey_data' not in st.session_state:
    st.session_state.survey_data = {}

# --- PAGE 1: INTRODUCTION ---
if st.session_state.page == 'intro':
    st.title("Experiment: Inventory Management")
    st.write("### Welcome")
    st.write("""
    You are participating in a study on decision-making in supply chains.
    
    **The Scenario:**
    * [cite_start]You are a procurement manager for a company selling **eco-friendly winter tires**[cite: 19].
    * Each week ("Round"), you must decide how many tires to order.
    * [cite_start]**Demand is uncertain:** It will be a random number between **50 and 150** every week[cite: 20].
    
    Your goal is to manage your inventory levels effectively based on the costs and prices provided.
    """)
    st.info("First, we will ask you 3 quick questions to make sure you understand the math.")
    
    if st.button("Go to Warm-Up"):
        st.session_state.page = 'warmup'
        st.rerun()

# --- PAGE 2: WARM-UP QUIZ ---
elif st.session_state.page == 'warmup':
    st.title("Warm-Up Questions")
    st.write("Please answer the following to verify your understanding of the costs.")
    st.write(f"**Selling Price:** ${PRICE} | **Cost:** ${COST}")
    
    with st.form("warmup_form"):
        st.write("**1. If you order 100 tires but demand is only 80:**")
        q1 = st.radio("How many tires do you actually sell?", [100, 80, 20])
        
        st.write("**2. In the same scenario (Order 100, Demand 80):**")
        q2 = st.radio("What happens to the leftover 20 tires?", ["We keep them for next week", "They are thrown away (Waste)"])
        
        st.write("**3. Profit Calculation:**")
        q3 = st.radio(f"You buy a tire for ${COST} and sell it for ${PRICE}. What is the profit per tire?", ["$10", "$7", "$3"])
        
        if st.form_submit_button("Check Answers & Continue"):
            # Simple scoring
            score = 0
            if q1 == 80: score += 1
            if q2 == "They are thrown away (Waste)": score += 1
            if q3 == "$7": score += 1
            
            st.session_state.warmup_score = score
            st.session_state.page = 'pre_experiment_transition'
            st.rerun()

# --- PAGE 3: TRANSITION TO EXPERIMENT ---
elif st.session_state.page == 'pre_experiment_transition':
    st.title("Ready to Start")
    st.success("Warm-up complete!")
    
    st.write("### The Experiment")
    st.write(f"- You will now play **{ROUNDS} rounds** of the ordering game.")
    st.write("- In each round, enter your order quantity.")
    st.write("- After you order, you will see the actual demand and your result.")
    
    st.warning("Click the button below when you are ready to begin Round 1.")
    
    if st.button("Start Experiment"):
        st.session_state.page = 'game'
        st.rerun()

# --- PAGE 4: THE GAME ROUNDS ---
elif st.session_state.page == 'game':
    st.title(f"Round {st.session_state.round} of {ROUNDS}")
    
    # --- 1. Show Feedback from Previous Round (if not round 1) ---
    if st.session_state.round > 1:
        last = st.session_state.history[-1]
        st.divider()
        st.info(f"📊 **Result from Round {last['Round']}:** You ordered **{last['Order']}**. Demand was **{last['Demand']}**.")
        
        # Feedback depends on Framing
        if st.session_state.frame == 'Positive':
            st.success(f"**You earned a profit of ${last['Profit']}**")
        else:
            # [cite_start]Calculate specific loss types for the Negative Frame text [cite: 41-42]
            if last['Demand'] < last['Order']:
                waste_loss = (last['Order'] - last['Demand']) * COST
                st.error(f"**You LOST ${waste_loss} on products you had to throw away.**")
            else:
                opportunity_loss = (last['Demand'] - last['Order']) * (PRICE - COST)
                st.error(f"**You LOST ${opportunity_loss} of profit for demand you could not meet.**")
    
    st.divider()

    # --- 2. Show Framing Text (Instructions for this round) ---
    # We show this every round so the "Framing Effect" is persistent
    st.subheader("Make Your Decision")
    st.write(f"**Unit Cost:** ${COST} | **Selling Price:** ${PRICE}")
    st.write(f"**Demand:** Uniformly distributed between {DEMAND_MIN} and {DEMAND_MAX}")
    
    if st.session_state.frame == 'Positive':
        # [cite_start]Positive Frame Text [cite: 22-23]
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
        # [cite_start]Negative Frame Text [cite: 41-42]
        st.markdown(f"""
        <div style="background-color:#fff5f5;padding:15px;border-radius:10px;border:1px solid #fc8181;">
        <strong>Goal: Minimize your losses.</strong><br>
        <ul>
        <li>If Demand < Order: You <strong>LOSE ${COST}</strong> on every product you throw away.</li>
        <li>If Demand > Order: You <strong>LOSE ${PRICE-COST}</strong> of profit for every demand you could not meet.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    # --- 3. Input ---
    # We use a unique key for each round so the number box resets or stays clean
    current_order = st.number_input("How many tires do you want to order?", 
                                    min_value=0, max_value=300, value=100, step=1, 
                                    key=f"input_{st.session_state.round}")
    
    if st.button("Submit Order"):
        # Logic
        actual_demand = random.randint(DEMAND_MIN, DEMAND_MAX)
        
        # Calculate standard profit (Revenue - Cost)
        sold = min(current_order, actual_demand)
        profit = (sold * PRICE) - (current_order * COST)
        
        # Save to history
        st.session_state.history.append({
            'Round': st.session_state.round,
            'Frame': st.session_state.frame,
            'Order': current_order,
            'Demand': actual_demand,
            'Profit': profit
        })
        
        # Move to next round OR finish
        if st.session_state.round < ROUNDS:
            st.session_state.round += 1
            st.rerun()
        else:
            st.session_state.page = 'post_experiment_transition'
            st.rerun()

# --- PAGE 5: TRANSITION TO SURVEY ---
elif st.session_state.page == 'post_experiment_transition':
    st.title("Experiment Rounds Completed")
    st.success("You have finished the ordering game.")
    st.write("You completed this part of the experiment.")
    st.write("Please click below to begin the final short survey.")
    
    if st.button("Start Survey"):
        st.session_state.page = 'survey'
        st.rerun()

# --- PAGE 6: POST-EXPERIMENT SURVEY ---
elif st.session_state.page == 'survey':
    st.title("Final Survey")
    st.write("Please answer the following questions regarding your decisions and demographics.")
    
    with st.form("survey_form"):
        # [cite_start]Section B: Perception Check [cite: 98-103]
        st.subheader("1. Decision Perception")
        st.write("Without analyzing it carefully, which of the following inventory decisions do you consider to be more environmentally friendly?")
        perception = st.radio("", 
                              ["Ordering a quantity that minimizes overstock and waste",
                               "Ordering a larger quantity to fully avoid stockouts",
                               "Both decisions are equally environmentally friendly"])
        
        # [cite_start]Section C: Environmental Awareness [cite: 104-116]
        st.subheader("2. Environmental Awareness")
        st.write("Rate your agreement (1 = Not important, 5 = Extremely important):")
        
        c1 = st.slider("When purchasing tires, CO2 reduction is an important decision criterion.", 1, 5, 3)
        c2 = st.slider("I consider the environmental impact over the full product life cycle.", 1, 5, 3)
        c3 = st.slider("I prioritize suppliers with environmental certifications (e.g., ISO 14001).", 1, 5, 3)
        c4 = st.slider("I am willing to accept higher costs for better environmental performance.", 1, 5, 3)
        c5 = st.slider("I actively aim to reduce waste and overstock to avoid environmental harm.", 1, 5, 3)
        
        # [cite_start]Section A: Demographics [cite: 70-97]
        st.subheader("3. Demographics")
        col1, col2 = st.columns(2)
        with col1:
            industry = st.selectbox("Industry", ["Manufacturing", "Automotive", "Retail/Wholesale", "Logistics", "Pharma", "Other"])
            company_size = st.selectbox("Company Size", ["Fewer than 50", "50-249", "250-999", "1,000 or more"])
        with col2:
            experience = st.selectbox("Experience", ["0-1 years", "2-3 years", "4-6 years", "7-10 years", "More than 10 years"])
        
        if st.form_submit_button("Submit Survey"):
            # Save Survey Data
            st.session_state.survey_data = {
                'Perception_Check': perception,
                'Env_CO2': c1,
                'Env_Lifecycle': c2,
                'Env_Certifications': c3,
                'Env_HigherCost': c4,
                'Env_ReduceWaste': c5,
                'Industry': industry,
                'CompanySize': company_size,
                'Experience': experience
            }
            st.session_state.page = 'thank_you'
            st.rerun()

# --- PAGE 7: THANK YOU & DOWNLOAD ---
elif st.session_state.page == 'thank_you':
    st.balloons()
    st.title("Thank You!")
    st.success("You have completed the experiment.")
    st.write("Please download your results below and submit them as instructed.")
    
    # --- PREPARE DATA FOR DOWNLOAD ---
    # 1. Convert game history to DataFrame
    df = pd.DataFrame(st.session_state.history)
    
    # 2. Add Warm-up Score
    df['WarmUp_Score'] = st.session_state.warmup_score
    
    # 3. Add Survey Data (Replicate across all rows for this user)
    for key, value in st.session_state.survey_data.items():
        df[key] = value
        
    # 4. Create CSV
    csv_data = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="Download Results (CSV)",
        data=csv_data,
        file_name="experiment_results.csv",
        mime="text/csv"
    )
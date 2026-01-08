import streamlit as st
import pandas as pd
import random

# --- CONFIGURATION ---
PRICE = 10
COST = 3
DEMAND_MIN = 50
DEMAND_MAX = 150
ROUNDS = 10

# --- SETUP SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
if 'frame' not in st.session_state:
    st.session_state.frame = random.choice(['Positive', 'Negative']) # Random Assignment
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'history' not in st.session_state:
    st.session_state.history = []
if 'warmup_score' not in st.session_state:
    st.session_state.warmup_score = 0

# --- PAGE 1: INTRO ---
if st.session_state.page == 'intro':
    st.title("Inventory Decision Experiment")
    st.write("Welcome! You are a procurement manager for a company selling eco-friendly winter tires.")
    st.info(f"**Instructions:** You will play for {ROUNDS} rounds. Your goal is to manage inventory efficiently.")
    
    if st.button("Start Warm-Up Quiz"):
        st.session_state.page = 'warmup'
        st.rerun()

# --- PAGE 2: WARM-UP (Comprehension Check) ---
elif st.session_state.page == 'warmup':
    st.title("Warm-Up: Understanding the Rules")
    st.write("Please answer these questions to ensure you understand the math.")
    
    with st.form("warmup_form"):
        q1 = st.radio("1. You order 100 tires. Demand is 80. How many do you sell?", [100, 80, 20])
        q2 = st.radio("2. In the case above (Order 100, Demand 80), what happens to the remaining 20?", ["Kept for next week", "Thrown away (Waste)"])
        q3 = st.radio("3. Price is $10, Cost is $3. If you sell one tire, what is the profit?", ["$10", "$7", "$3"])
        
        if st.form_submit_button("Submit Answers"):
            # Check answers
            score = 0
            if q1 == 80: score += 1
            if q2 == "Thrown away (Waste)": score += 1
            if q3 == "$7": score += 1
            
            st.session_state.warmup_score = score
            st.session_state.page = 'game'
            st.rerun()

# --- PAGE 3: THE EXPERIMENT (10 Rounds) ---
elif st.session_state.page == 'game':
    st.title(f"Round {st.session_state.round} of {ROUNDS}")
    
    # Show previous results
    if st.session_state.round > 1:
        last = st.session_state.history[-1]
        st.info(f"📊 **Last Round:** You ordered {last['Order']}. Demand was {last['Demand']}.")
        
        if st.session_state.frame == 'Positive':
            st.success(f"Result: You earned a profit of **${last['Profit']}**.")
        else:
            # Negative Framing Display
            if last['Demand'] < last['Order']:
                loss = (last['Order'] - last['Demand']) * COST
                st.error(f"Result: You **LOST ${loss}** due to waste.")
            else:
                loss = (last['Demand'] - last['Order']) * (PRICE - COST)
                st.error(f"Result: You **LOST ${loss}** in missed opportunity.")

    st.markdown("---")
    
    # FRAMING TEXT (Changes based on group)
    if st.session_state.frame == 'Positive':
        st.subheader("Goal: Maximize Profit")
        st.write(f"Earn **${PRICE-COST}** per sale. Avoid waste.")
    else:
        st.subheader("Goal: Minimize Losses")
        st.write(f"Lose **${COST}** per waste. Lose **${PRICE-COST}** per missed sale.")
        
    # Input
    order = st.number_input("How many units do you want to order?", min_value=0, max_value=300, value=100)
    
    if st.button("Submit Decision"):
        # Logic
        demand = random.randint(DEMAND_MIN, DEMAND_MAX)
        sold = min(order, demand)
        profit = (sold * PRICE) - (order * COST)
        
        # Save Data
        st.session_state.history.append({
            'Round': st.session_state.round,
            'Frame': st.session_state.frame,
            'Order': order,
            'Demand': demand,
            'Profit': profit
        })
        
        # Advance Round
        if st.session_state.round < ROUNDS:
            st.session_state.round += 1
        else:
            st.session_state.page = 'survey'
        st.rerun()

# --- PAGE 4: SURVEY & DOWNLOAD ---
elif st.session_state.page == 'survey':
    st.title("Final Survey")
    
    with st.form("survey"):
        st.write("Please answer the following demographic questions.")
        ind = st.selectbox("Industry", ["Manufacturing", "Automotive", "Retail", "Other"])
        exp = st.selectbox("Experience", ["0-1 years", "2-5 years", "5+ years"])
        eco = st.slider("How important is CO2 reduction to you? (1-5)", 1, 5, 3)
        
        if st.form_submit_button("Finish Experiment"):
            st.session_state.survey_results = {'Industry': ind, 'Experience': exp, 'Eco_Score': eco}
            st.session_state.page = 'results'
            st.rerun()

elif st.session_state.page == 'results':
    st.success("Experiment Complete! Please download your results below.")
    
    # Compile Data
    df = pd.DataFrame(st.session_state.history)
    # Add survey data to every row
    for k, v in st.session_state.survey_results.items():
        df[k] = v
    df['WarmUp_Score'] = st.session_state.warmup_score
    
    # Download Button
    st.download_button("Download My Data (CSV)", df.to_csv(index=False), "my_experiment_results.csv")
    st.write("Please upload this file to the submission folder.")
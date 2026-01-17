import streamlit as st
import pandas as pd
import random
import requests
import json

# --- CONFIGURATION ---
SHEETDB_URL = "https://sheetdb.io/api/v1/YOUR_EXACT_CODE_HERE" 

ACCESS_CODE = "START" 
PRICE = 10 
COST = 3 
ROUNDS = 10
DEMAND_MIN = 50
DEMAND_MAX = 150

# --- GİZLİ SABİT DEMAND LİSTESİ ---
FIXED_DEMAND_VALUES = [123, 67, 142, 89, 55, 110, 95, 134, 72, 101]

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state: st.session_state.page = 'lobby'
if 'frame' not in st.session_state: st.session_state.frame = None 
if 'round' not in st.session_state: st.session_state.round = 1
if 'history' not in st.session_state: st.session_state.history = []
if 'warmup_score' not in st.session_state: st.session_state.warmup_score = 0
if 'survey_data' not in st.session_state: st.session_state.survey_data = {}
if 'data_sent' not in st.session_state: st.session_state.data_sent = False 

# --- PAGE 0: LOBBY ---
if st.session_state.page == 'lobby':
    st.title("Welcome")
    st.info("Please wait for the instructor to provide the Access Code.")
    
    group_num = st.text_input("Enter your Group Number (1 or 2):")
    code_input = st.text_input("Enter Access Code:", type="password")
    
    if st.button("Enter"):
        if code_input == ACCESS_CODE:
            if group_num == "1":
                st.session_state.frame = 'Negative'
                st.session_state.page = 'intro'
                st.rerun()
            elif group_num == "2":
                st.session_state.frame = 'Positive'
                st.session_state.page = 'intro'
                st.rerun()
            else:
                st.error("Invalid Group Number! Please enter 1 or 2.")
        else:
            st.error("Incorrect Access Code.")

# --- PAGE 1: INTRODUCTION ---
elif st.session_state.page == 'intro':
    st.title("Experiment: Inventory Management")
    st.write("### Instructions")
    
    st.info("""
    **Role:** You will act as a **procurement manager** for 10 rounds, deciding on 
    weekly order quantities for **eco-friendly winter tires**.
    """)
    
    st.write(f"""
    **The Scenario:**
    * **Demand is uncertain:** It will be a random number between **{DEMAND_MIN} and {DEMAND_MAX}** every week.
    * **Product Type:** This is a **High Margin Product**.
    """)
    
    st.write(f"Selling Price (p) = ${PRICE} | Unit Cost (c) = ${COST}")
    
    st.divider()
    
    # --- EKSTRA AÇIKLAMA ---
    st.subheader("How your result is calculated:")
    st.markdown("""
    Your goal is to find the right balance between ordering too much and ordering too little.
    
    **1. If Demand < Order (Too much inventory):**
    * You sell what is demanded.
    * The leftover tires are waste. You **lose the Cost ($3)** for every unsold tire.
    
    **2. If Demand > Order (Too little inventory):**
    * You sell everything you ordered.
    * You miss out on potential customers. You **lose the potential Profit ($7)** for every sale you missed.
    """)
    st.divider()
    
    if st.button("Start Warm-Up"):
        st.session_state.page = 'warmup'
        st.rerun()

# --- PAGE 2: WARM-UP ---
elif st.session_state.page == 'warmup':
    st.title("Warm-Up")
    st.write("Please answer the following scenarios to ensure you understand the profit and loss logic.")
    st.info(f"Reference: Selling Price = ${PRICE} | Unit Cost = ${COST}")
    
    with st.form("warmup"):
        st.write("### Scenario A: You order 100 tires, but Demand is only 80.")
        q1 = st.radio("1. How many tires do you actually sell?", 
                      ["100 (All my order)", "80 (Only the demand)", "20 (The difference)"])
        
        st.write("2. You have 20 leftover tires. Since the Cost is $3, what is the financial impact?")
        q2 = st.radio("", 
                      ["I lose $60 (20 tires * $3 cost)", 
                       "I gain $60", 
                       "Nothing happens"])
        
        st.markdown("---")
        
        st.write("### Scenario B: You order 100 tires, but Demand is 120.")
        st.write("3. You missed 20 sales. Since the Profit is $7 ($10 Price - $3 Cost), what is the impact?")
        q3 = st.radio("", 
                      ["I saved money by ordering less", 
                       "I missed out on $140 of potential profit (20 tires * $7 profit)", 
                       "I lost $60"])
        
        if st.form_submit_button("Submit Answers"):
            score = 0
            if "80" in q1: score += 1
            if "lose $60" in q2: score += 1
            if "missed out on $140" in q3: score += 1
            
            st.session_state.warmup_score = score
            st.session_state.page = 'pre_experiment_transition'
            st.rerun()

# --- PAGE 3: TRANSITION ---
elif st.session_state.page == 'pre_experiment_transition':
    st.title("Ready to Start")
    st.success("Warm-up complete!")
    st.write(f"You will now play **{ROUNDS} rounds**.")
    st.warning("Click below to begin Round 1.")
    if st.button("Start Experiment"):
        st.session_state.page = 'game'
        st.rerun()

# --- PAGE 4: GAME ---
elif st.session_state.page == 'game':
    st.title(f"Round {st.session_state.round}/{ROUNDS}")
    
    # --- FEEDBACK ---
    if st.session_state.round > 1:
        last = st.session_state.history[-1]
        
        st.info(f"You ordered {last['Order']} at a cost of ${last['Order'] * COST}. Demand was {last['Demand']}.")
        
        if st.session_state.frame == 'Positive':
            st.success(f"You earned ${last['Profit']}.")
            st.caption("Any inventory remaining has become obsolete. You should order for this week, conditions have not changed.")
        else:
            if last['Demand'] < last['Order']:
                loss_val = (last['Order'] - last['Demand']) * COST
                st.error(f"You lost ${loss_val}.")
            else:
                loss_val = (last['Demand'] - last['Order']) * (PRICE - COST)
                st.error(f"You lost ${loss_val}.")
            
            st.caption("Any inventory remaining has become obsolete. You should order for this week, conditions have not changed.")

    st.divider()

    # --- INSTRUCTION (Font Fixed) ---
    st.write(f"Your company sells eco-friendly winter tires. You order them for **${COST}** each every week and sell them for **${PRICE}**.")
    
    st.write(f"""
    Leftover products will not be utilized for the next periods, and will be thrown away. 
    Demand is uniformly distributed (U[{DEMAND_MIN},{DEMAND_MAX}]). 
    You will decide on the number of products to be ordered each round.
    """)

    if st.session_state.frame == 'Positive':
        st.markdown(f"""
        <div style="background-color:#e6fffa;padding:15px;border-radius:10px;border:1px solid #4fd1c5;">
        <ul>
        <li>[ In case of Demand < Ordered Quantity ] You will <strong>earn ${PRICE-COST}</strong> on every demand you sell.</li>
        <li>[ In case of Demand > Ordered Quantity ] You will <strong>earn a profit of ${PRICE-COST}</strong> on each quantity you ordered.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        input_label = "How many products would you like to order?" if st.session_state.round > 1 else "How many products would you like to order in the first week?"

    else: # Negative Frame
        st.markdown(f"""
        <div style="background-color:#fff5f5;padding:15px;border-radius:10px;border:1px solid #fc8181;">
        <ul>
        <li>[ In case of Demand < Ordered Quantity ] You will <strong>lose ${COST}</strong> on every product you throw away.</li>
        <li>[ In case of Demand > Ordered Quantity ] You will <strong>lose ${PRICE-COST}</strong> of profit for every demand you could not meet.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        input_label = "How many products would you like to order?" if st.session_state.round > 1 else "How many products would you like to order in the first week?"

    # --- INPUT ---
    order = st.number_input(input_label, 0, 300, 100, key=f"q_{st.session_state.round}")
    
    if st.button("Submit Order"):
        demand = FIXED_DEMAND_VALUES[st.session_state.round - 1]
        sold = min(order, demand)
        profit = (sold * PRICE) - (order * COST)
        st.session_state.history.append({
            'Round': st.session_state.round, 'Frame': st.session_state.frame,
            'Order': order, 'Demand': demand, 'Profit': profit
        })
        if st.session_state.round < ROUNDS:
            st.session_state.round += 1
            st.rerun()
        else:
            st.session_state.page = 'post_experiment_transition'
            st.rerun()

# --- PAGE 5: POST-TRANSITION ---
elif st.session_state.page == 'post_experiment_transition':
    st.title("Experiment Completed")
    st.write("You have finished the ordering game.")
    st.write("Please click below to begin the final survey.")
    if st.button("Start Survey"):
        st.session_state.page = 'survey'
        st.rerun()

# --- PAGE 6: SURVEY ---
elif st.session_state.page == 'survey':
    st.title("Final Survey")
    
    st.info("""
    **Instructions:** In the following questions, please assume the role of a **procurement manager** working for a company that purchases products for business use. Your task is to evaluate purchasing 
    decisions at the firm level, considering factors such as cost efficiency, operational requirements, 
    and environmental impact. All questions refer to decisions made in your **professional role** as a 
    procurement manager, not as a private consumer.
    """)
    
    with st.form("survey_form"):
        st.subheader("Section A: Perception Check")
        perc_1 = st.radio("1. Which statement best reflects the role you were asked to take?", 
                          ["I was asked to evaluate marketing strategies", "I was asked to make purchasing decisions as a procurement manager", "I was asked to make decisions as a final consumer"])
        perc_2 = st.radio("2. Which consideration best characterizes the decision context?", 
                          ["Individual consumer choice based on personal values", "Long-term corporate sustainability strategy", "Short-term purchasing decisions balancing cost efficiency and environmental responsibility"])
        perc_3 = st.radio("3. Without analyzing it carefully, which inventory decision do you consider more environmentally friendly?", 
                          ["Ordering a quantity that minimizes overstock and waste", "Ordering a larger quantity to fully avoid stockouts", "Both decisions are equally environmentally friendly"])

        st.markdown("---")

        st.subheader("Section B: Demographics")
        # --- BURASI DÜZELTİLDİ: ARTIK HEPSİ OPEN QUESTION (TEXT INPUT) ---
        industry = st.text_input("4. Industry / Sector:")
        experience = st.text_input("5. Years of experience in procurement / purchasing / operations:")
        company_size = st.text_input("6. Company size (approximate number of employees):")

        st.markdown("---")

        st.subheader("Section C: Environmental Awareness")
        st.caption("Rate 1 (Strongly Disagree) to 5 (Strongly Agree).")
        
        eccb_1 = st.slider("1. It is important to me that the products I use do not harm the environment.", 1, 5, 3)
        eccb_2 = st.slider("2. I consider the potential environmental impact of my actions when making many of my decisions.", 1, 5, 3)
        eccb_3 = st.slider("3. My purchase habits are affected by my concern for our environment.", 1, 5, 3)
        eccb_4 = st.slider("4. I am concerned about wasting the resources of our planet.", 1, 5, 3)
        eccb_5 = st.slider("5. I would describe myself as environmentally responsible.", 1, 5, 3)
        eccb_6 = st.slider("6. I am willing to be inconvenienced in order to take actions that are more environmentally friendly.", 1, 5, 3)
        
        if st.form_submit_button("Submit Survey"):
            st.session_state.survey_data = {
                'Perception_Role': perc_1, 'Perception_Context': perc_2, 'Perception_Inventory': perc_3,
                'Industry': industry, 'Experience': experience, 'CompanySize': company_size,
                'ECCB_1': eccb_1, 'ECCB_2': eccb_2, 'ECCB_3': eccb_3,
                'ECCB_4': eccb_4, 'ECCB_5': eccb_5, 'ECCB_6': eccb_6
            }
            st.session_state.page = 'thank_you'
            st.rerun()

# --- PAGE 7: AUTO-SAVE ---
elif st.session_state.page == 'thank_you':
    st.balloons()
    st.title("Processing Results...")

    df = pd.DataFrame(st.session_state.history)
    df['WarmUp_Score'] = st.session_state.warmup_score
    for k, v in st.session_state.survey_data.items():
        df[k] = v
    
    if not st.session_state.data_sent:
        with st.spinner("Saving your data..."):
            try:
                data_payload = df.to_dict(orient='records')
                headers = {'Content-Type': 'application/json'}
                requests.post("https://sheetdb.io/api/v1/7tr3fchy6qvq5", json={"data": data_payload}, headers=headers)
                st.session_state.data_sent = True
                st.success("✅ Success! Data saved.")
            except Exception as e:
                st.error("Auto-save failed.")

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV (Backup)", csv, "results.csv", "text/csv")
import streamlit as st
import pandas as pd
import random
import requests
import json

# --- CONFIGURATION ---
# Kendi SheetDB URL'nizi buraya yapıştırın:
SHEETDB_URL = "https://sheetdb.io/api/v1/YOUR_EXACT_CODE_HERE" 

ACCESS_CODE = "START" 
PRICE = 10 
COST = 3 
ROUNDS = 10
DEMAND_MIN = 50
DEMAND_MAX = 150

# --- GİZLİ SABİT DEMAND LİSTESİ ---
# Öğrenciler bunu bilmeyecek, "Rastgele" sanacaklar.
# Bu sayılar 50-150 aralığından seçilmiş sabit sayılardır.
FIXED_DEMAND_VALUES = [123, 67, 142, 89, 55, 110, 95, 134, 72, 101]

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state: st.session_state.page = 'lobby'
if 'frame' not in st.session_state: st.session_state.frame = None 
if 'round' not in st.session_state: st.session_state.round = 1
if 'history' not in st.session_state: st.session_state.history = []
if 'warmup_score' not in st.session_state: st.session_state.warmup_score = 0
if 'survey_data' not in st.session_state: st.session_state.survey_data = {}
if 'data_sent' not in st.session_state: st.session_state.data_sent = False 

# --- PAGE 0: LOBBY (1-2 GRUP SİSTEMİ) ---
if st.session_state.page == 'lobby':
    st.title("Welcome")
    st.info("Please wait for the instructor to provide the Access Code.")
    
    # Grup Numarası Girişi (1 veya 2)
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
    
    # BURADA ÖĞRENCİYE "DEMAND IS UNCERTAIN" DİYEREK HİKAYEYİ KORUYORUZ
    st.write(f"""
    **The Scenario:**
    * **Demand is uncertain:** It will be a random number between **{DEMAND_MIN} and {DEMAND_MAX}** every week.
    * **Product Type:** This is a **High Margin Product**.
    """)
    
    st.write(f"**Selling Price (p) = ${PRICE}** | **Unit Cost (c) = ${COST}**")
    
    if st.button("Start Warm-Up"):
        st.session_state.page = 'warmup'
        st.rerun()

# --- PAGE 2: WARM-UP ---
elif st.session_state.page == 'warmup':
    st.title("Warm-Up")
    st.write("Please answer the following to verify your understanding.")
    st.markdown(f"### Reference Values: Price=${PRICE} | Cost=${COST}")
    
    with st.form("warmup"):
        q1 = st.radio("1. You order 100, Demand is 80. How many do you sell?", [100, 80, 20])
        q2 = st.radio("2. What happens to the leftover 20 units?", ["Kept for next week", "Thrown away (Waste)"])
        q3 = st.radio("3. What is the profit per unit sold?", ["$10", "$7", "$3"])
        
        if st.form_submit_button("Submit"):
            score = 0
            if q1 == 80: score += 1
            if q2 == "Thrown away (Waste)": score += 1
            if q3 == "$7": score += 1
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
    
    # Önceki Turun Sonuçlarını Göster
    if st.session_state.round > 1:
        last = st.session_state.history[-1]
        st.info(f"Last Round: Order {last['Order']} | Demand {last['Demand']}")
        if st.session_state.frame == 'Positive':
            st.success(f"Result: Profit of ${last['Profit']}")
        else:
            loss = (last['Order']-last['Demand'])*COST if last['Demand']<last['Order'] else (last['Demand']-last['Order'])*(PRICE-COST)
            st.error(f"Result: You LOST ${loss}")

    # Framing Display (Hedef Gösterimi)
    st.write(f"**Price: ${PRICE} | Cost: ${COST}**")
    
    # Öğrenci burada talebin 50-150 arası rastgele dağıldığını okuyor
    st.write(f"**Demand:** Uniformly distributed between {DEMAND_MIN} and {DEMAND_MAX}")

    if st.session_state.frame == 'Positive':
        st.success("Goal: Maximize Profit. Earn $7 per sale.")
    else:
        st.error("Goal: Minimize Losses. Lose $3 per waste or $7 per missed sale.")

    order = st.number_input("Order Quantity:", 0, 300, 100, key=f"q_{st.session_state.round}")
    
    if st.button("Submit Order"):
        # --- ARKA PLAN (GİZLİ) ---
        # Burada rastgele sayı değil, sabit listeden sıradaki sayıyı çekiyoruz.
        # Öğrenci bunu görmez.
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
    
    with st.form("survey_form"):
        # Section A: Perception
        st.subheader("Section A: Perception Check")
        perc_1 = st.radio("1. Role?", ["Evaluate marketing", "Procurement manager", "Final consumer"])
        perc_2 = st.radio("2. Context?", ["Individual choice", "Long-term strategy", "Short-term purchasing"])
        perc_3 = st.radio("3. Eco-friendly decision?", ["Minimizing waste", "Avoiding stockouts", "Equal"])

        st.markdown("---")
        # Section B: Demographics
        st.subheader("Section B: Demographics")
        industry = st.text_input("4. Industry / Sector:")
        experience = st.selectbox("5. Experience:", ["0-1 years", "2-3 years", "4-6 years", "7-10 years", "More than 10 years"])
        company_size = st.selectbox("6. Company size:", ["Fewer than 50", "50-249", "250-999", "1,000 or more"])

        st.markdown("---")
        # Section C: Environmental (GREEN Scale)
        st.subheader("Section C: Environmental Awareness")
        st.caption("Rate 1 (Strongly Disagree) to 5 (Strongly Agree).")
        
        eccb_1 = st.slider("1. No harm to environment", 1, 5, 3)
        eccb_2 = st.slider("2. Consider impact in decisions", 1, 5, 3)
        eccb_3 = st.slider("3. Purchase habits affected", 1, 5, 3)
        eccb_4 = st.slider("4. Concerned about waste", 1, 5, 3)
        eccb_5 = st.slider("5. Environmentally responsible", 1, 5, 3)
        eccb_6 = st.slider("6. Willing to be inconvenienced", 1, 5, 3)
        
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
    
    # Auto-Save to SheetDB
    if not st.session_state.data_sent:
        with st.spinner("Saving your data..."):
            try:
                data_payload = df.to_dict(orient='records')
                headers = {'Content-Type': 'application/json'}
                requests.post(https://sheetdb.io/api/v1/7tr3fchy6qvq5, json={"data": data_payload}, headers=headers)
                st.session_state.data_sent = True
                st.success("✅ Success! Data saved.")
            except Exception as e:
                st.error("Auto-save failed.")

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV (Backup)", csv, "results.csv", "text/csv")
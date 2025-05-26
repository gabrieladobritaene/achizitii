import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Analiză Achiziții per An")

uploaded_file = st.file_uploader("Încarcă fișierul combinat (Agent, Produs, Cantitate, An)", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df = df.dropna(subset=['Agent', 'Produs', 'Cantitate', 'An'])
    df['An'] = df['An'].astype(str)

    ani_disponibili = sorted(df['An'].unique())
    ani_selectati = st.multiselect("Selectează anii pentru analiză", ani_disponibili, default=ani_disponibili)

    if ani_selectati:
        agenti_disponibili = sorted(df['Agent'].unique())
        agent_selectat = st.selectbox("Selectează un agent pentru detalii (sau Toți)", ["Toți"] + agenti_disponibili)

        df_filtrat = df[df['An'].isin(ani_selectati)]

        if agent_selectat != "Toți":
            df_filtrat = df_filtrat[df_filtrat['Agent'] == agent_selectat]

        produs_selectat = st.selectbox("Selectează un produs (sau Toate)", ["Toate"] + sorted(df_filtrat['Produs'].unique()))
        if produs_selectat != "Toate":
            df_filtrat = df_filtrat[df_filtrat['Produs'] == produs_selectat]

        st.subheader("👥 Cantitate totală per agent - Comparativ per an")
        for an in ani_selectati:
            df_an = df_filtrat[df_filtrat['An'] == an]
            total_agent = df_an.groupby('Agent')['Cantitate'].sum().reset_index().sort_values('Cantitate', ascending=False)
            suma_totala = total_agent['Cantitate'].sum()
            st.markdown(f"### Total cantitate achiziționată în {an}: **{suma_totala:,.2f}** unități")
            fig = px.bar(
                total_agent,
                x='Cantitate',
                y='Agent',
                orientation='h',
                title=f"Total Cantitate per Agent în {an}",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📦 Cantitate totală per produs - Comparativ per an")
        ordonare_produse = df_filtrat.groupby('Produs')['Cantitate'].sum().sort_values(ascending=False).index.tolist()

        for an in ani_selectati:
            df_an = df_filtrat[df_filtrat['An'] == an]
            total_produs = df_an.groupby('Produs')['Cantitate'].sum().reset_index()
            total_produs['Produs'] = pd.Categorical(total_produs['Produs'], categories=ordonare_produse, ordered=True)
            total_produs = total_produs.sort_values('Produs')
            suma_totala = total_produs['Cantitate'].sum()
            st.markdown(f"### Total cantitate pe produse în {an}: **{suma_totala:,.2f}** unități")

            fig = px.bar(
                total_produs,
                x='Produs',
                y='Cantitate',
                title=f"Total Cantitate per Produs în {an}",
                color='Produs',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🔍 Comparație directă între doi agenți pe același produs")
        an_comp = st.selectbox("Alege anul pentru comparație", ani_disponibili, key="an_comparatie")
        produs_comp = st.selectbox("Alege produsul pentru comparație", sorted(df['Produs'].unique()), key="produs_comparatie")
        agent_1 = st.selectbox("Agent 1", agenti_disponibili, key="agent1")
        agent_2 = st.selectbox("Agent 2", [a for a in agenti_disponibili if a != agent_1], key="agent2")

        df_comp = df[(df['An'] == an_comp) & (df['Produs'] == produs_comp) & (df['Agent'].isin([agent_1, agent_2]))]
        total_comparatie = df_comp.groupby('Agent')['Cantitate'].sum().reset_index()

        st.markdown(f"### Comparație pentru produsul **{produs_comp}** în anul **{an_comp}**")
        fig_comp = px.bar(
            total_comparatie,
            x='Agent',
            y='Cantitate',
            color='Agent',
            title=f"Comparație între {agent_1} și {agent_2} pentru {produs_comp} în {an_comp}",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown("---")
        st.markdown("Aplicație interactivă cu grafice moderne realizată cu 💙 Streamlit + Plotly.")

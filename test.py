import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Analiză Achiziții per An")

uploaded_file = st.file_uploader("Încarcă fișierul combinat (Agent, Produs, Cantitate, An, Regiune, URL_Poza - opțional)", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df = df.dropna(subset=['Agent', 'Produs', 'Cantitate', 'An'])
    df['An'] = df['An'].astype(str).str.replace(".0", "", regex=False)

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
            st.markdown(f"### Total cantitate achiziționată în {an}: **{suma_totala:,.2f} tone**")
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
            st.markdown(f"### Total cantitate pe produse în {an}: **{suma_totala:,.2f} tone**")

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
        st.subheader("📍 Analiză detaliată per agent")
        for agent in sorted(df['Agent'].unique()):
            st.markdown(f"### Agent: **{agent}**")
            agent_df = df[df['Agent'] == agent]
            fig = px.bar(agent_df, x='Produs', y='Cantitate', color='An', barmode='group',
                         title=f"Cantitate pe produs în timp - {agent}",
                         color_discrete_map={'2023': 'steelblue', '2024': 'orange', '2025': 'green'})
            st.plotly_chart(fig, use_container_width=True)
            tabel = agent_df.groupby('An')['Cantitate'].sum().reset_index().rename(columns={'Cantitate': 'Total tone'})
            st.dataframe(tabel)

        st.markdown("---")
        st.subheader("📊 Comparație Regiuni SUD vs VEST")
        if 'Regiune' in df.columns:
            regiune_total = df.groupby('Regiune')['Cantitate'].sum().reset_index()
            fig_pie = px.pie(regiune_total, names='Regiune', values='Cantitate', title="Total achiziții per regiune (tone și %)", hole=0.4)
            fig_pie.update_traces(textinfo='percent+value', textfont_size=14)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("🏆 Top 5 agenți după cantitate totală")
        if 'Regiune' in df.columns:
            top5 = df.groupby(['Agent', 'Regiune'])['Cantitate'].sum().reset_index()
        else:
            top5 = df.groupby(['Agent'])['Cantitate'].sum().reset_index()
            top5['Regiune'] = 'Necunoscut'
        top5 = top5.sort_values('Cantitate', ascending=False).head(5)
        top5.columns = ['Agent', 'Regiune', 'Total cantitate (t)']
        st.dataframe(top5)

        st.subheader("📋 Tabel pivot: Agenți × Produse")
        pivot = df.pivot_table(index='Agent', columns='Produs', values='Cantitate', aggfunc='sum', fill_value=0)
        st.dataframe(pivot)

        st.subheader("📈 Evoluție produse principale: SUD vs VEST")
        if 'Regiune' in df.columns:
            produse_principale = ['WHEAT', 'BARLEY', 'RAPESEED', 'SUNFLOWER']
            df_filtrat_prod = df[df['Produs'].isin(produse_principale)]
            for produs in produse_principale:
                df_prod = df_filtrat_prod[df_filtrat_prod['Produs'] == produs]
                grup = df_prod.groupby(['An', 'Regiune'])['Cantitate'].sum().reset_index()
                fig = px.line(grup, x='An', y='Cantitate', color='Regiune', markers=True,
                              title=f"{produs} - evoluție în timp pe regiuni")
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("🧠 Insight-uri AI (beta)")
        with st.expander("🔍 Interpretare automată"):
            if 'Regiune' in df.columns:
                sud_total = df[df['Regiune'] == 'SUD'].groupby('An')['Cantitate'].sum()
                vest_total = df[df['Regiune'] == 'VEST'].groupby('An')['Cantitate'].sum()

                delta_sud = sud_total.pct_change().fillna(0).mean()
                delta_vest = vest_total.pct_change().fillna(0).mean()

                prod_dom_sud = df[df['Regiune'] == 'SUD'].groupby('Produs')['Cantitate'].sum().idxmax()
                prod_dom_vest = df[df['Regiune'] == 'VEST'].groupby('Produs')['Cantitate'].sum().idxmax()

                echilibru = df.groupby('Agent')['Produs'].nunique().sort_values(ascending=False)
                agent_echilibrat = echilibru.idxmax()

                st.markdown(f"- 📈 Regiunea cu cea mai mare creștere medie: **{'SUD' if delta_sud > delta_vest else 'VEST'}**")
                st.markdown(f"- 🌾 Produsul dominant în SUD: **{prod_dom_sud}**")
                st.markdown(f"- 🌻 Produsul dominant în VEST: **{prod_dom_vest}**")
                st.markdown(f"- 🧮 Agentul cu portofoliu cel mai diversificat: **{agent_echilibrat}**")

        st.markdown("---")
        st.subheader("🔍 Comparație directă între doi agenți pe același produs")
        an_comp = st.selectbox("Alege anul pentru comparație", ani_disponibili, key="an_comparatie")
        produs_comp = st.selectbox("Alege produsul pentru comparație", sorted(df['Produs'].unique()), key="produs_comparatie")
        agent_1 = st.selectbox("Agent 1", agenti_disponibili, key="agent1")
        agent_2 = st.selectbox("Agent 2", [a for a in agenti_disponibili if a != agent_1], key="agent2")

        df_comp = df[(df['An'] == an_comp) & (df['Produs'] == produs_comp) & (df['Agent'].isin([agent_1, agent_2]))]
        total_comparatie = df_comp.groupby('Agent')['Cantitate'].sum().reset_index()

        st.markdown(f"### Comparație pentru produsul **{produs_comp}** în anul **{an_comp}**")

        cols = st.columns(2)
        for i, agent in enumerate([agent_1, agent_2]):
            url_col = 'URL_Poza'
            if url_col in df.columns:
                url = df[df['Agent'] == agent][url_col].dropna().unique()
                if len(url) > 0:
                    cols[i].image(url[0], caption=agent, width=180)

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
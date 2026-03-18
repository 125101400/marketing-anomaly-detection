import pandas as pd
import matplotlib.pyplot as plt

# ── 1. Load data ──────────────────────────────────────────
df = pd.read_csv('marketing_campaign.csv', sep=',')

# ── 2. Strip spaces from column names ────────────────────
df.columns = df.columns.str.strip()

# ── 3. Check columns and clean ───────────────────────────
print("Columns:", df.columns.tolist())
print("Shape:", df.shape)
print("Nulls:\n", df.isnull().sum())

# Drop rows with missing income
df = df.dropna(subset=['Income'])

# ── 4. Focus on key spend columns ─────────────────────────
spend_cols = ['MntWines', 'MntFruits', 'MntMeatProducts',
              'MntFishProducts', 'MntSweetProducts', 'MntGoldProds']

df['Total_Spend'] = df[spend_cols].sum(axis=1)

# ── 5. Statistical anomaly detection ──────────────────────
mean_spend  = df['Total_Spend'].mean()
std_spend   = df['Total_Spend'].std()
upper_limit = mean_spend + 2 * std_spend
lower_limit = mean_spend - 2 * std_spend

print(f"\nMean Total Spend:    ${mean_spend:,.2f}")
print(f"Std Deviation:       ${std_spend:,.2f}")
print(f"Upper Threshold:     ${upper_limit:,.2f}")
print(f"Lower Threshold:     ${lower_limit:,.2f}")

# ── 6. Flag anomalies ─────────────────────────────────────
df['Anomaly'] = df['Total_Spend'].apply(
    lambda x: 'High Spender' if x > upper_limit else
              'Low Spender'  if x < lower_limit else 'Normal'
)

df['Risk_Score'] = ((df['Total_Spend'] - mean_spend) / std_spend).round(2)

print(f"\nAnomaly breakdown:")
print(df['Anomaly'].value_counts())

# ── 7. Export top 10 high spenders ────────────────────────
top_anomalies = (df[df['Anomaly'] == 'High Spender']
                 .sort_values('Risk_Score', ascending=False)
                 .head(10)
                 [['Income', 'Total_Spend', 'Risk_Score',
                   'MntWines', 'MntMeatProducts', 'Anomaly']])

top_anomalies.to_csv('top_anomalies.csv', index=False)
print("\nTop 10 High-Spend Anomalies:")
print(top_anomalies.to_string(index=False))

# ── 8. Scatter plot ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))

normal     = df[df['Anomaly'] == 'Normal']
high_spend = df[df['Anomaly'] == 'High Spender']
low_spend  = df[df['Anomaly'] == 'Low Spender']

ax.scatter(normal.index, normal['Total_Spend'],
           color='#378ADD', alpha=0.4, s=15, label='Normal')
ax.scatter(high_spend.index, high_spend['Total_Spend'],
           color='#C00000', alpha=0.8, s=40, label='High Spend Anomaly')
ax.scatter(low_spend.index, low_spend['Total_Spend'],
           color='#EF9F27', alpha=0.8, s=40, label='Low Spend Anomaly')

ax.axhline(y=upper_limit, color='#C00000', linestyle='--',
           linewidth=1.2, label=f'Upper Threshold (${upper_limit:,.0f})')
ax.axhline(y=mean_spend, color='grey', linestyle=':',
           linewidth=1.0, label=f'Mean (${mean_spend:,.0f})')

ax.set_title('Marketing Spend Anomaly Detection — Customer Risk Analysis',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Customer Index', fontsize=11)
ax.set_ylabel('Total Spend (USD)', fontsize=11)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('anomaly_chart.png', dpi=150)
plt.show()
print("\nChart saved as anomaly_chart.png")
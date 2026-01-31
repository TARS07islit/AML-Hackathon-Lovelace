import pandas as pd

wallet_scores = pd.read_csv("wallet_scores.csv")

def get_all_wallets():
    return wallet_scores

def get_top_wallets(n=5):
    return (
        wallet_scores
        .sort_values("wallet_score", ascending=False)
        .head(n)
        .to_dict(orient="records")
    )

def get_wallet_by_id(wallet_id: str):
    result = wallet_scores[wallet_scores["wallet_id"] == wallet_id]
    if result.empty:
        return None
    return result.iloc[0].to_dict()

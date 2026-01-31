from fastapi import FastAPI, HTTPException
from data import get_all_wallets, get_top_wallets, get_wallet_by_id

app = FastAPI(
    title="AML Wallet Risk API",
    description="Explainable backend service for blockchain AML risk scoring",
    version="2.0"
)

# --------------------
# Helper functions
# --------------------

def risk_label(score: float):
    if score >= 10:
        return "High"
    elif score >= 5:
        return "Medium"
    return "Low"

def explain_wallet_logic(wallet):
    reasons = []

    if wallet["illicit_ratio"] > 0.3:
        reasons.append("High exposure to illicit transactions")

    if wallet["max_score"] > 8:
        reasons.append("Connected to high-risk transaction clusters")

    if wallet["wallet_score"] > 10:
        reasons.append("Overall elevated graph-based risk")

    if not reasons:
        reasons.append("No strong laundering indicators detected")

    return reasons

# --------------------
# Core endpoints
# --------------------

@app.get("/")
def root():
    return {"message": "AML Backend is running"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "AML Backend"}

@app.get("/wallets")
def all_wallets():
    return get_all_wallets().to_dict(orient="records")

@app.get("/wallets/top")
def top_wallets(n: int = 5):
    wallets = get_top_wallets(n)

    for w in wallets:
        w["risk_level"] = risk_label(w["wallet_score"])

    return wallets

@app.get("/wallet/{wallet_id}")
def wallet_details(wallet_id: str):
    wallet = get_wallet_by_id(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    wallet["risk_level"] = risk_label(wallet["wallet_score"])
    return wallet

@app.get("/wallet/{wallet_id}/explain")
def wallet_explanation(wallet_id: str):
    wallet = get_wallet_by_id(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {
        "wallet_id": wallet_id,
        "risk_score": wallet["wallet_score"],
        "risk_level": risk_label(wallet["wallet_score"]),
        "reasons": explain_wallet_logic(wallet)
    }

@app.get("/summary")
def summary():
    df = get_all_wallets()

    return {
        "total_wallets": len(df),
        "high_risk": int((df["wallet_score"] >= 10).sum()),
        "medium_risk": int(((df["wallet_score"] >= 5) & (df["wallet_score"] < 10)).sum()),
        "low_risk": int((df["wallet_score"] < 5).sum())
    }

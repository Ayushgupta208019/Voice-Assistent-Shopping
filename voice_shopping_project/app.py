from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import spacy

app = Flask(__name__)
CORS(app)

nlp = spacy.load("en_core_web_sm")

# Simple in-memory cart
shopping_cart = []  # each item: {id, title, price, quantity}

# --- Intent detection ---
ADD_PATTERNS = [r"\b(add|buy|purchase|include|get)\b", r"\b(i\s+want\s+to\s+buy)\b"]
REMOVE_PATTERNS = [r"\b(remove|delete|discard|drop|take\s+away)\b"]

def detect_intent(text: str) -> str:
    t = text.lower()
    for pat in ADD_PATTERNS:
        if re.search(pat, t): return "add"
    for pat in REMOVE_PATTERNS:
        if re.search(pat, t): return "remove"
    return "find"

def extract_item(text: str):
    doc = nlp(text.lower())
    nouns = [t.text for t in doc if t.pos_ in ("NOUN","PROPN")]
    return " ".join(nouns) if nouns else text

def fetch_all_products():
    r = requests.get("https://fakestoreapi.in/api/products", timeout=15)
    r.raise_for_status()
    return r.json().get("products", [])

def token_overlap_score(a,b):
    A = set(re.findall(r"[a-z0-9]+", a.lower()))
    B = set(re.findall(r"[a-z0-9]+", b.lower()))
    return len(A & B)

def best_match(products, query):
    best,score=None,0
    for p in products:
        s=token_overlap_score(p.get("title",""),query)
        if s>score: best,score=p,s
    return best

@app.route("/products", methods=["GET"])
def products_proxy():
    try:
        return jsonify({"products": fetch_all_products()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/cart", methods=["GET"])
def get_cart():
    total = sum(item["price"]*item["quantity"] for item in shopping_cart)
    return jsonify({"cart": shopping_cart,"total":round(total,2)})

@app.route("/process_voice", methods=["POST"])
def process_voice():
    data=request.get_json(force=True,silent=True) or {}
    text=(data.get("text") or "").strip()
    if not text: return jsonify({"error":"No text"}),400

    action=detect_intent(text)
    item=extract_item(text)

    try: products=fetch_all_products()
    except Exception as e: return jsonify({"error":f"API error {e}"}),502

    if action=="add":
        match=best_match(products,item)
        if match:
            found=False
            for c in shopping_cart:
                if c["id"]==match["id"]:
                    c["quantity"]+=1
                    found=True
            if not found:
                shopping_cart.append({
                    "id":match["id"],"title":match["title"],
                    "price":match["price"],"quantity":1
                })
            return jsonify({"intent":"add","added":match["title"],"cart":shopping_cart})
        return jsonify({"intent":"add","added":None,"cart":shopping_cart})

    if action=="remove":
        removed=None
        for c in shopping_cart:
            if token_overlap_score(c["title"],item)>0:
                if c["quantity"]>1: c["quantity"]-=1
                else: shopping_cart.remove(c)
                removed=c["title"]; break
        return jsonify({"intent":"remove","removed":removed,"cart":shopping_cart})

    # find intent (suggestions)
    q=item.lower()
    suggestions=[p["title"] for p in products if q in p["title"].lower()]
    if not suggestions: suggestions=[p["title"] for p in products[:10]]
    return jsonify({"intent":"find","suggestions":suggestions})

if __name__=="__main__":
    app.run(debug=True)

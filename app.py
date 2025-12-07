from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# ==============================
# ✅ YOUR RECOMMENDER CLASS
# ==============================
class SmartElectronicsRecommender:
    def __init__(self, dataset_path):
        self.data = pd.read_csv(dataset_path)
        self.prepare_data()

    def prepare_data(self):
        self.data.columns = [col.strip().lower() for col in self.data.columns]

        self.data.fillna({
            'rating': 0,
            'price': self.data['price'].median(),
            'reviews': 0,
            'manufactured_in': 'Unknown'
        }, inplace=True)

        self.data['manufactured_in'] = self.data['manufactured_in'].str.strip().str.title()

    def recommend(self, user_input):
        try:
            product_name, company = user_input.split(" by ")
        except ValueError:
            return "Please enter input in format: <product> by <company>", None

        product_name = product_name.strip().lower()
        company = company.strip().lower()

        match = self.data[
            (self.data['product_name'].str.lower().str.contains(product_name)) &
            (self.data['company'].str.lower().str.contains(company))
        ]

        if match.empty:
            return f"No matching product found for '{user_input}'", None

        recommendations = []

        for _, product in match.iterrows():
            score = self.calculate_score(product)
            decision = "BUY" if score >= 60 else "NOT BUY"

            result = {
                "name": product['product_name'],
                "company": product['company'],
                "price": product['price'],
                "rating": product['rating'],
                "reviews": product['reviews'],
                "manufactured": product['manufactured_in'],
                "score": round(score, 1),
                "decision": decision
            }

            recommendations.append(result)

        return None, recommendations

    def calculate_score(self, product):
        score = 0

        score += (product['rating'] / 5) * 40

        if product['reviews'] > 500:
            score += 10
        elif product['reviews'] > 100:
            score += 5

        if product['price'] < 20000:
            score += 10
        elif 20000 <= product['price'] <= 60000:
            score += 15
        else:
            score += 5

        if 'india' in product['manufactured_in'].lower():
            score += 20

        return min(score, 100)


# ==============================
# ✅ LOAD DATASET
# ==============================
recommender = SmartElectronicsRecommender("electronics_dataset.csv")

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    results = None

    if request.method == "POST":
        user_input = request.form.get("product")
        error, results = recommender.recommend(user_input)

    return render_template("index.html", error=error, results=results)

if __name__ == "__main__":
    app.run(debug=True)

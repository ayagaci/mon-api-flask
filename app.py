import os
import logging
from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from flask_cors import CORS

# Configuration des logs
logging.basicConfig(
    filename="error.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = Flask(__name__)
CORS(app)
def calculer_statistiques(data):
    try:
        data_array = np.array(data)
        s = pd.Series(data_array)

        mode_list = s.mode().tolist()
        if len(mode_list) == len(data_array):  # Si tous les nombres sont uniques
           mode_list = ["Aucun mode"]
        quartiles = np.percentile(data_array, [25, 50, 75])

        statistiques = {
            "moyenne": float(np.mean(data_array)),  # 🔹 Conversion en float
            "mediane": float(np.median(data_array)),
            "mode": mode_list,
            "variance": float(np.var(data_array, ddof=1)),
            "ecart_type": float(np.std(data_array, ddof=1)),
            "min": float(np.min(data_array)),
            "max": float(np.max(data_array)),
            "amplitude": float(np.max(data_array) - np.min(data_array)),
            "skewness": float(skew(data_array)),
            "kurtosis": float(kurtosis(data_array)),
            "quartiles": {
                "Q1": float(quartiles[0]),
                "Q2": float(quartiles[1]),
                "Q3": float(quartiles[2])
            }
        }

        return statistiques
    except Exception as e:
        logging.error(f"Erreur lors du calcul des statistiques: {str(e)}")
        return {"error": "Erreur interne du serveur, consultez les logs."}

@app.route('/calculer', methods=['POST'])
def calculer():
    try:
        data = request.get_json().get("data")  #  Correction de l'indentation

        if data is None:
            return jsonify({"error": "Aucune donnée fournie"}), 400

        if not isinstance(data, list) or not all(isinstance(i, (int, float)) for i in data):
            return jsonify({"error": "Les données doivent être une liste de nombres"}), 400

        if len(data) == 0:
            return jsonify({"error": "La liste de nombres est vide"}), 400

        logging.info(f"Requête reçue avec {len(data)} éléments.")

        result = calculer_statistiques(data)

        if "error" in result:
            return jsonify(result), 500

        return jsonify(result)
    except Exception as e:
        logging.error(f"Erreur interne du serveur: {str(e)}")
        return jsonify({"error": "Erreur interne du serveur, veuillez réessayer plus tard."}), 500

@app.route("/")
def home():
    return "Bienvenue sur Flask !"

@app.route('/stats')
def stats():
    return "Voici les statistiques"


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print("Serveur en cours d'exécution sur http://127.0.0.1:5001")
    app.run(debug=debug_mode, port=5001)



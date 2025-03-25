import os
import sys
import logging
from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from flask_cors import CORS

# Configuration des logs (console + fichier)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("error.log"),  # Log dans un fichier
        logging.StreamHandler(sys.stdout)  # Log dans la console
    ]
)

app = Flask(__name__)
CORS(app)

def calculer_statistiques(data): 
    try:
        data_array = np.array(data)
        s = pd.Series(data_array)

        mode_list = s.mode().tolist()
        mode_list = None if len(mode_list) == len(data_array) else mode_list  # Gère le cas où tous les nombres sont uniques
        quartiles = np.percentile(data_array, [25, 50, 75])
        iqr = float(quartiles[2] - quartiles[0])  # IQR = Q3 - Q1

        # Gestion de la variance et de l'écart-type si un seul élément est présent
        if len(data_array) == 1:
            variance = 0
            ecart_type = 0
        else:
            variance = float(np.var(data_array, ddof=1))
            ecart_type = float(np.std(data_array, ddof=1))

        statistiques = {
            "moyenne": float(np.mean(data_array)),
            "mediane": float(np.median(data_array)),
            "mode": mode_list,
            "variance": variance,
            "ecart_type": ecart_type,
            "min": float(np.min(data_array)),
            "max": float(np.max(data_array)),
            "amplitude": float(np.max(data_array) - np.min(data_array)),
            "skewness": float(skew(data_array)),
            "kurtosis": float(kurtosis(data_array)),
            "quartiles": {
                "Q1": float(quartiles[0]),
                "Q2": float(quartiles[1]),
                "Q3": float(quartiles[2])
            },
            "iqr": iqr  # 🔹 Ajout de l'IQR dans les résultats
        }

        print(statistiques)  # Debug pour voir si "iqr" est bien calculé et renvoyé
        return statistiques

    except Exception as e:
        logging.error(f"Erreur lors du calcul des statistiques: {str(e)}")
        return {"error": "Erreur interne du serveur, consultez les logs."}

@app.route('/calculer', methods=['POST'], strict_slashes=False)
def calculer():
    try:
        json_data = request.get_json()
        print("Données reçues brutes :", json_data)  # Debug

        if json_data is None:
            return jsonify({"error": "Aucune donnée fournie"}), 400

        data = json_data.get("valeurs")
        if data is None:
            return jsonify({"error": "Clé 'valeurs' absente du JSON"}), 400

        print("Valeurs extraites :", data)  # Debug

        # Vérification du type des données
        if not isinstance(data, list) or not all(isinstance(i, (int, float)) for i in data):
            return jsonify({"error": "Les données doivent être une liste de nombres"}), 400

        if len(data) == 0:
            return jsonify({"error": "La liste de nombres est vide"}), 400

        result = calculer_statistiques(data)

        return jsonify({
            **result,
            "q1": result["quartiles"]["Q1"],  # 🔹 Correction ici
            "q3": result["quartiles"]["Q3"]   # 🔹 Correction ici
        })

    except Exception as e:
        logging.error(f"Erreur interne du serveur: {str(e)}")
        return jsonify({"error": "Erreur interne du serveur, veuillez réessayer plus tard."}), 500


@app.route("/", strict_slashes=False)
def home():
    return "Bienvenue sur Flask !"

@app.route('/stats', strict_slashes=False)
def stats():
    return jsonify({"message": "Statistiques générées avec succès"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


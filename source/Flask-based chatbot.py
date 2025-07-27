
from flask import Flask, request, jsonify
import psycopg2

# Initialisation du serveur Flask
app = Flask(__name__)

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    dbname="PFE",
    user="postgres",
    password="0000",
    options="-c client_encoding=UTF8"
)
cursor = conn.cursor() #permet d’exécuter des requêtes SQL

#Définition du webhook (crée une route POST) (c’est une API personnalisée.)

@app.route("/webhook", methods=["POST"])
def webhook():
    print(" Fonction webhook déclenchée !")

    try:
        print(" Webhook reçu !")
        #Lecture de la requête reçue (Récupère le contenu de la requête envoyée par Dialogflow.)
        req = request.get_json(force=True)
        print(" JSON reçu :", req)
        print(" Intent brut dans la requête : {}".format(req['queryResult']['intent']['displayName']))
        intent = req["queryResult"]["intent"]["displayName"].strip() #Extrait le nom de l’intent déclenché
        print(" Intent reçu : '{}' (longueur : {})".format(intent, len(intent)))

        if intent == "Nombre_Anomalies":
            cursor.execute('SELECT COUNT(*) FROM "BANQUE"."TB_TRANSACTION" WHERE "IS_FRAUD" = 1')
            result = cursor.fetchone()
            if result:
                count = result[0]
                response_text = f"🔍 Il y a eu {count} anomalies détectées dans les transactions."
            else:
                response_text = "Aucune donnée trouvée."

        elif intent == "Total_Transactions":
            cursor.execute('SELECT SUM("MONTANT") FROM "BANQUE"."TB_TRANSACTION"')
            result = cursor.fetchone()
            if result and result[0] is not None:
                total = round(result[0], 2)
                response_text = f"💰 Le montant total des transactions est de {total} TND."
            else:
                response_text = "Aucune transaction enregistrée."

        elif intent == "Transactions_Etranger":
            print(" Bloc Transactions_Etranger déclenché")
            cursor.execute('SELECT COUNT(*) FROM "BANQUE"."TB_TRANSACTION" WHERE "PAYS" != %s', ("TN",))
            result = cursor.fetchone()
            print(" Résultat SQL Transactions_Etranger :", result)
            if result and result[0] is not None:
                count = result[0]
                response_text = f"🌍 Il y a eu {count} transactions effectuées depuis un pays autre que la Tunisie."
            else:
                response_text = "Aucune transaction étrangère détectée."

        elif intent == "Aide_Utilisation":
            print(" Bloc Aide_Utilisation déclenché")
            response_text = (
                "Je suis là pour vous aider à analyser les transactions bancaires ! 😊\n"
                "Voici quelques exemples de ce que vous pouvez me demander :\n"
                "- \"Quel est le montant total des transactions ?\"\n"
                "- \"Quelles agences sont les plus actives ?\"\n"
                "- \"Transactions_Etrange ?\"\n"
                "- \"Comptes_Bloqués?\"\n"
                "- \"Top_Packs?\"\n"
                "- \"Quel est le type de transaction le plus fréquent ?\"\n"
                "Vous pouvez aussi taper \"Explorer les données\" pour voir d'autres suggestions."
            )
        elif intent == "Explorer_Données":
            print(" Bloc Explorer_Données déclenché")
            response_text = (
                "Voici quelques analyses disponibles 📊 :\n\n"
                "🔸 Clients & Comptes :\n"
                "- \"Quels sont les clients avec le plus d’anomalies ?\"\n"
                "- \"Quel est le profil moyen des clients ?\"\n\n"
                "🔸 Transactions :\n"
                "- \"Combien de transactions ont eu lieu la nuit ?\"\n"
                "- \"Quel est le pays avec le plus de fraudes ?\"\n\n"
                "🔸 Agences & Performances :\n"
                "- \"Compare les agences actives\"\n"
                "- \"Quelle agence a traité le plus d'opérations ?\"\n\n"
                "🔸 Anomalies :\n"
                "- \"Quel est le taux d'anomalies ?\"\n"
                "- \"Montre-moi les fraudes par type de transaction\"\n\n"
                "Et bien plus encore ! Essayez de poser une question "
            )
        
        elif intent == "Comptes_Bloqués":
            print(" Bloc Comptes_Bloqués déclenché")
            try:
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM "BANQUE"."TB_COMPTE"
                    WHERE("ETAT") IN ('C')
                ''')
                result = cursor.fetchone()
                print(" Résultat SQL Comptes_Bloqués :", result)

                if result and result[0] is not None:
                    nb_bloc = result[0]
                    response_text = f"🔒 Il y a actuellement {nb_bloc} comptes bloqués dans le système."
                else:
                    response_text = "Aucun compte bloqué n'a été trouvée."
            except Exception as e:
                response_text = f"Erreur lors de la récupération des comptes bloqués : {e}"

        elif "nuit" in intent.lower():
            print(" Bloc Transactions_Nuit déclenché")
            cursor.execute('''
                SELECT COUNT(*) 
                FROM "BANQUE"."TB_TRANSACTION" 
                WHERE "heure_transaction" >= 21 OR "heure_transaction" < 7
            ''')
            result = cursor.fetchone()
            print(" Résultat SQL Transactions_Nuit :", result)
            if result and result[0] is not None:
                count = result[0]
                response_text = f"🌒 Il y a eu {count} transactions effectuées à des heures inhabituelles (nuit)."
            else:
                response_text = "Aucune transaction nocturne détectée."

        elif intent == "Montant le plus élevé":
            print(" Bloc Transaction_Max déclenché")
            cursor.execute('SELECT MAX("MONTANT") FROM "BANQUE"."TB_TRANSACTION"')
            result = cursor.fetchone()
            print(" Résultat SQL Transaction_Max :", result)
            if result and result[0] is not None:
                max_montant = round(result[0], 2)
                response_text = f"💸 La plus grosse transaction enregistrée est de {max_montant} TND."
            else:
                response_text = "Aucune transaction trouvée."

        elif intent == "Type_Transaction_Frequent":
            print(" Bloc Type_Transaction_Frequent déclenché")
            cursor.execute('''
                SELECT "TYPE_TRANSAC", COUNT(*) AS nb 
                FROM "BANQUE"."TB_TRANSACTION"
                GROUP BY "TYPE_TRANSAC"
                ORDER BY nb DESC
                LIMIT 1
            ''')
            result = cursor.fetchone()
            print(" Résultat SQL Type_Transaction_Frequent :", result)
            if result:
                type_transac, count = result
                response_text = f" Le type de transaction le plus fréquent est '{type_transac}' avec {count} occurrences."
            else:
                response_text = "Aucune donnée sur les types de transaction."

        elif intent == "Canal_Le_Plus_Utilise":
            print(" Bloc Canal_Le_Plus_Utilise déclenché")
            cursor.execute('''
                SELECT "CANAL", COUNT(*) AS nb
                FROM "BANQUE"."TB_TRANSACTION"
                GROUP BY "CANAL"
                ORDER BY nb DESC
                LIMIT 1
            ''')
            result = cursor.fetchone()
            print(" Résultat SQL Canal_Le_Plus_Utilise :", result)
            if result:
                canal, count = result
                response_text = f" Le canal de transaction le plus utilisé est : {canal} ({count} opérations)."
            else:
                response_text = "Aucune donnée sur les canaux de transaction."

        elif intent == "Top_Packs":
            print(" Bloc Top_Packs déclenché")
            cursor.execute('''
                SELECT p."LIB_PACK", COUNT(f."ID_TRANSAC") AS nb
                FROM "dwh_banque"."FACT_TABLE_TRANSACTION" f
                JOIN "dwh_banque"."Dim_pack" p 
                ON f."ID_PACK_DIM"::TEXT = p."ID_PACK_DIM"
                GROUP BY p."LIB_PACK"
                ORDER BY nb DESC
                LIMIT 3
            ''')
            results = cursor.fetchall()
            print(" Résultat SQL Top_Packs :", results)

            if results:
                lines = [f"- {lib}: {count} transactions" for lib, count in results]
                response_text = " Voici les 3 packs les plus utilisés :\n" + "\n".join(lines)
            else:
                response_text = "Aucune donnée disponible sur les packs."

        elif intent == "Agences_Actives":
            print(" Bloc Agences_Actives déclenché")
            cursor.execute('''
                SELECT a."agence", COUNT(f."ID_TRANSAC") AS nb
                FROM "dwh_banque"."FACT_TABLE_TRANSACTION" f
                JOIN "dwh_banque"."Dim_agence" a ON f."ID_AGENCE" = a."ID_AGENCE"
                GROUP BY a."agence"
                ORDER BY nb DESC
                LIMIT 3
            ''')
            results = cursor.fetchall()
            print(" Résultat SQL Agences_Actives :", results)

            if results:
                lines = [f"- {agence} : {count} transactions" for agence, count in results]
                response_text = " Les agences ayant la plus forte activité sont :\n" + "\n".join(lines)
            else:
                response_text = "Aucune donnée sur les agences trouvée."

        elif intent == "Fraudes_Par_Type":
            print(" Bloc Fraudes_Par_Type déclenché")
            cursor.execute('''
                SELECT "TYPE_TRANSAC", COUNT(*) AS nb_fraudes
                FROM "BANQUE"."TB_TRANSACTION"
                WHERE "IS_FRAUD" = 1
                GROUP BY "TYPE_TRANSAC"
                ORDER BY nb_fraudes DESC
            ''')
            results = cursor.fetchall()
            print(" Résultat SQL Fraudes_Par_Type :", results)

            if results:
                lines = [f"- {type_transac} : {count} fraudes" for type_transac, count in results]
                response_text = "🚨 Répartition des fraudes par type de transaction :\n" + "\n".join(lines)
            else:
                response_text = "Aucune fraude enregistrée par type de transaction."

        elif intent == "Montant_Pertes_Fraudes":
            print("💸 Bloc Montant_Pertes_Fraudes déclenché")
            cursor.execute('''
                SELECT SUM("MONTANT") 
                FROM "BANQUE"."TB_TRANSACTION" 
                WHERE "IS_FRAUD" = 1
            ''')
            result = cursor.fetchone()
            print(" Résultat SQL Montant_Pertes_Fraudes :", result)

            if result and result[0] is not None:
                perte_total = round(result[0], 2)
                response_text = f"💸 Le montant total des pertes dues aux fraudes est de {perte_total} TND."
            else:
                response_text = "Aucune perte liée à la fraude n'a été enregistrée."

        elif intent == "Taux_Anomalies":
            print(" Bloc Taux_Anomalies déclenché")
            cursor.execute('SELECT COUNT(*) FROM "BANQUE"."TB_TRANSACTION" WHERE "IS_FRAUD" = 1')
            anomalies = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM "BANQUE"."TB_TRANSACTION"')
            total_transactions = cursor.fetchone()[0]

            if total_transactions > 0:
                taux_anomalies = round((anomalies / total_transactions) * 100, 2)
                response_text = f"📊 Le taux d'anomalies est de {taux_anomalies} %."
            else:
                response_text = "Impossible de calculer le taux d'anomalies car il n'y a pas de transactions."

        elif intent == "Pays_Risques":
            print("🌍 Bloc Pays_Risques déclenché")
            cursor.execute('''
                SELECT "PAYS", COUNT(*) AS nb_fraudes
                FROM "BANQUE"."TB_TRANSACTION"
                WHERE "IS_FRAUD" = 1
                GROUP BY "PAYS"
                ORDER BY nb_fraudes DESC
                LIMIT 3
            ''')
            results = cursor.fetchall()
            print(" Résultat SQL Pays_Risques :", results)

            if results:
                lines = [f"- {pays} : {count} fraudes" for pays, count in results]
                response_text = "🌍 Les pays les plus risqués sont :\n" + "\n".join(lines)
            else:
                response_text = "Aucun pays risqué détecté."

        elif intent == "Plages_d_Horaires_Risquees":
            print(" Bloc Plages_d_Horaires_Risquees déclenché")
            cursor.execute('''
                SELECT
                    CASE
                        WHEN "heure_transaction" BETWEEN 0 AND 6 THEN 'Nuit'
                        WHEN "heure_transaction" BETWEEN 7 AND 11 THEN 'Matinée'
                        WHEN "heure_transaction" BETWEEN 12 AND 17 THEN 'Après-midi'
                        WHEN "heure_transaction" BETWEEN 18 AND 23 THEN 'Soirée'
                        ELSE 'Inconnue'
                    END AS plage_horaire,
                    COUNT(*) AS nb_fraudes
                FROM "BANQUE"."TB_TRANSACTION"
                WHERE "IS_FRAUD" = 1
                GROUP BY plage_horaire
                ORDER BY nb_fraudes DESC
                LIMIT 1
            ''')
            result = cursor.fetchone()
            print(" Résultat SQL Plages_d_Horaires_Risquees :", result)

            if result:
                plage, nb_fraudes = result
                response_text = f"⏰ La plage horaire la plus risquée est : {plage} avec {nb_fraudes} fraudes."
            else:
                response_text = "Aucune fraude enregistrée pour déterminer une plage horaire risquée."

        elif intent == "Agences_À_Surveiller":
            print(" Bloc Agences_À_Surveiller déclenché")
            try:
                cursor.execute('''
                    SELECT a."agence",
                        COUNT(*) FILTER (WHERE t."ID_HIST_FRAUD" IS NOT NULL AND t."ID_HIST_FRAUD" != 0)::FLOAT / COUNT(*) * 100 AS taux_fraude
                    FROM "dwh_banque"."FACT_TABLE_TRANSACTION" t
                    JOIN "dwh_banque"."Dim_agence" a ON t."ID_AGENCE" = a."ID_AGENCE"
                    GROUP BY a."agence"
                    HAVING COUNT(*) >= 50
                    ORDER BY taux_fraude DESC
                    LIMIT 5
                ''')
                results = cursor.fetchall()
                print(" Résultat SQL Agences_À_Surveiller :", results)

                if results:
                    lignes = [f"- {agence} : {round(taux, 2)} % de fraudes" for agence, taux in results]
                    response_text = (
                        "⚠️ Voici les agences à surveiller en raison d’un taux de fraude élevé :\n" +
                        "\n".join(lignes)
                    )
                else:
                    response_text = " Aucune agence ne présente un taux de fraude élevé actuellement."
            except Exception as e:
                response_text = f"Erreur lors de la détection des agences à surveiller : {e}"



        elif intent == "Classement_Agences":
            print(" Bloc Classement_Agences déclenché")
            try:
                cursor.execute('''
                    SELECT a."agence", COUNT(f."ID_TRANSAC") AS nb_transactions
                    FROM "dwh_banque"."FACT_TABLE_TRANSACTION" f
                    JOIN "dwh_banque"."Dim_agence" a ON f."ID_AGENCE" = a."ID_AGENCE"
                    GROUP BY a."agence"
                    ORDER BY nb_transactions DESC
                    
                ''')
                results = cursor.fetchall()
                print(" Résultat SQL Classement_Agences :", results)

                if results:
                    lines = [f"{i+1}. {agence} : {count} transactions" for i, (agence, count) in enumerate(results)]
                    response_text = "🏅 Voici le classement des agences par nombre de transactions :\n" + "\n".join(lines)
                else:
                    response_text = "Aucune donnée sur les agences n'a été trouvée."
            except Exception as e:
                response_text = f"Erreur lors du classement des agences : {e}"

        elif intent == "Comparer_Agences":
            print(" Bloc Comparer_Agences déclenché")

            # Extraction des paramètres depuis Dialogflow
            parameters = req["queryResult"]["parameters"]
            agence1 = parameters.get("agence1")
            agence2 = parameters.get("agence2")

            if agence1 and agence2:
                print(f"Comparaison entre {agence1} et {agence2}")

                # Requête pour récupérer le nombre de transactions pour chaque agence
                cursor.execute('''
                    SELECT "agence", COUNT(*) AS nb_transactions
                    FROM "dwh_banque"."FACT_TABLE_TRANSACTION" f
                    JOIN "dwh_banque"."Dim_agence" a ON f."ID_AGENCE" = a."ID_AGENCE"
                    WHERE a."agence" IN (%s, %s)
                    GROUP BY a."agence"
                ''', (agence1, agence2))

                results = cursor.fetchall()
                print(" Résultat SQL Comparer_Agences :", results)

                if len(results) == 2:
                    agence_a, nb_a = results[0]
                    agence_b, nb_b = results[1]

                    if nb_a > nb_b:
                        gagnante = agence_a
                        ecart = nb_a - nb_b
                    else:
                        gagnante = agence_b
                        ecart = nb_b - nb_a

                    response_text = (
                        f"🏆 L'agence **{gagnante}** a généré plus de transactions "
                        f"avec une différence de {ecart} opérations."
                    )
                elif len(results) == 1:
                    agence_unique, nb = results[0]
                    response_text = f"ℹ️ Seule l'agence '{agence_unique}' a des transactions enregistrées ({nb} opérations)."
                else:
                    response_text = "Aucune donnée trouvée pour les deux agences spécifiées."
            else:
                response_text = "❗ Veuillez spécifier deux agences à comparer."


        return jsonify({"fulfillmentText": response_text})
    #Gestion des erreurs: 
    except Exception as e:
        conn.rollback()
        print(" ERREUR WEBHOOK :", e)
        #Envoi de la réponse à Dialogflow / fulfillmentText est le champ que Dialogflow affiche dans le chat.
        return jsonify({"fulfillmentText": f"Erreur serveur : {str(e)}"}), 500

#Lancement du serveur Flask
if __name__ == "__main__":
    print(" Serveur Flask avec PostgreSQL prêt !")
    app.run(port=5000) #Démarre le serveur en local à l’adresse localhost:5000
                       #cette adresse qu'on va donner à Dialogflow dans la section "Fulfillment → Webhook"



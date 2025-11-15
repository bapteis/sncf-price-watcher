# 🚄 SNCF Price Watcher

Surveillez automatiquement les prix de vos billets SNCF et recevez des notifications Telegram quand un prix inférieur est disponible.

## ✨ Fonctionnalités

- ✅ Surveillance automatique 4x/jour (6h, 12h, 18h, 22h)
- ✅ Prise en compte de votre **carte Avantage Adulte**
- ✅ Recherche aller-retour pour bénéficier de la réduction 30%
- ✅ Flexibilité horaire configurable (±X heures)
- ✅ Notifications Telegram instantanées
- ✅ 100% gratuit via GitHub Actions

## 🚀 Installation

### 1. Créer votre bot Telegram

1. Ouvrez Telegram et cherchez **@BotFather**
2. Envoyez `/newbot` et suivez les instructions
3. Notez le **token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Pour obtenir votre **Chat ID**:
   - Cherchez **@userinfobot** sur Telegram
   - Démarrez une conversation, il vous donnera votre ID

### 2. Configurer le repository GitHub

```bash
# Cloner ce repository
git clone https://github.com/VOTRE_USERNAME/sncf-price-watcher.git
cd sncf-price-watcher

# Créer la structure de fichiers
mkdir -p .github/workflows data src
```

### 3. Ajouter vos secrets GitHub

1. Allez sur votre repository GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Cliquez sur **New repository secret**
4. Ajoutez ces 2 secrets:
   - `TELEGRAM_BOT_TOKEN` : votre token du bot
   - `TELEGRAM_CHAT_ID` : votre chat ID

### 4. Configurer vos trajets

Éditez le fichier `data/my_trips.json` :

```json
{
  "trips": [
    {
      "origin": "Paris",
      "destination": "Bordeaux",
      "outbound_date": "2025-12-15",
      "outbound_time": "14:30",
      "return_date": "2025-12-18",
      "return_time": "18:00",
      "current_price": 65.00,
      "flexibility_hours": 3,
      "notes": "Weekend à Bordeaux"
    }
  ]
}
```

**⚠️ TRÈS IMPORTANT :**
- Utilisez les **noms de VILLES simples** : `Paris`, `Lyon`, `Marseille` (PAS les noms de gares)
- Le `current_price` est le prix de l'**ALLER SIMPLE** (pas l'aller-retour total)
- Exemples : `Paris` (pas "Paris Montparnasse"), `Lyon` (pas "Lyon Part-Dieu")

### 5. Activer GitHub Actions

1. Allez dans l'onglet **Actions** de votre repository
2. Cliquez sur **I understand my workflows, go ahead and enable them**

## 📝 Ajouter un nouveau trajet

Quand vous achetez un nouveau billet :

1. Éditez `data/my_trips.json`
2. Ajoutez votre trajet dans le tableau `trips`
3. Commit et push :

```bash
git add data/my_trips.json
git commit -m "Ajout trajet Paris-Lyon"
git push
```

## 🧪 Tester manuellement

Sur GitHub :
1. **Actions** → **Check SNCF Prices**
2. Cliquez sur **Run workflow**
3. Vous recevrez une notification Telegram immédiatement

En local :
```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="votre_token"
export TELEGRAM_CHAT_ID="votre_chat_id"
python src/main.py
```

## ⏰ Fréquence des vérifications

Le script tourne automatiquement :
- **6h00** - Tôt le matin (nouveaux tarifs)
- **12h00** - Midi
- **18h00** - Soirée (pics de réservation)
- **22h00** - Nuit

Pour changer la fréquence, modifiez la ligne `cron` dans `.github/workflows/check_prices.yml`

## 🔧 Configuration avancée

### Modifier la flexibilité horaire

Dans `my_trips.json`, le paramètre `flexibility_hours` définit la plage acceptable :
- `3` = accepte les trains entre ±3h de votre horaire
- `0` = seulement le train exact

### Notifications

Vous recevrez une notification Telegram uniquement si :
- Un prix **inférieur** est trouvé
- Dans votre plage horaire de flexibilité
- Avec votre carte Avantage Adulte appliquée

## ⚠️ Limitations et notes

### API SNCF non-officielle
Le script utilise l'API publique de SNCF Connect. Quelques points à noter :

1. **L'API peut changer** : SNCF peut modifier sa structure à tout moment
2. **Rate limiting** : Le script respecte des pauses (3 secondes entre requêtes)
3. **Noms de gares** : Utilisez les noms exacts (inspectez les requêtes sur sncf-connect.com)

### Comment trouver le nom exact d'une gare ?

1. Allez sur https://www.sncf-connect.com
2. Ouvrez les **DevTools** (F12)
3. Onglet **Network**
4. Faites une recherche de trajet
5. Cherchez la requête `search` ou `train`
6. Regardez le payload pour voir le format exact des gares

### Prochaines améliorations possibles

- [ ] Support Trainline en parallèle
- [ ] Détection automatique du nom des gares
- [ ] Historique des prix
- [ ] Graphique d'évolution
- [ ] Support aller simple

## 🐛 Dépannage

### Pas de notification reçue ?

1. Vérifiez que les secrets sont bien configurés
2. Regardez les logs dans **Actions** → dernier run
3. Testez manuellement avec `Run workflow`

### Erreur "Gare non trouvée" ?

Vérifiez le nom exact de la gare dans les requêtes SNCF (voir section ci-dessus)

### Le script ne trouve jamais de meilleurs prix ?

- Les prix SNCF changent surtout pour les départs lointains
- Pour les trajets dans moins de 2 semaines, les prix sont généralement fixes
- Vérifiez que `flexibility_hours` n'est pas à 0

## 📜 Licence

MIT - Utilisez comme vous voulez !

## 🤝 Contribution

Les Pull Requests sont bienvenues pour :
- Améliorer le parsing de l'API SNCF
- Ajouter le support d'autres sites (Trainline, Omio...)
- Optimiser les performances

---

**💡 Astuce :** Pour économiser encore plus, activez aussi l'alerte "Petit Prix" native sur SNCF Connect en parallèle !

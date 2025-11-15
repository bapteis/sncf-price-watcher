import requests
import os
from typing import List, Dict

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialise le notifier Telegram
        
        Args:
            bot_token: Token de votre bot Telegram
            chat_id: Votre chat ID Telegram
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Envoie un message Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur Telegram: {e}")
            return False
    
    def notify_better_price(self, trip: Dict, new_price: float, savings: float):
        """Envoie une notification pour un meilleur prix trouvé"""
        message = f"""
🎉 *MEILLEUR PRIX TROUVÉ !*

🚄 *Trajet:* {trip['origin']} → {trip['destination']}

📅 *Dates:*
• Aller: {trip['outbound_date']} à {trip['outbound_time']}
• Retour: {trip['return_date']} à {trip['return_time']}

💰 *Prix:*
• Votre prix actuel: {trip['current_price']}€
• Nouveau prix: {new_price}€
• *Économie: {savings:.2f}€* 💸

🔗 Allez sur SNCF Connect pour réserver !
        """.strip()
        
        self.send_message(message)
    
    def notify_multiple_deals(self, deals: List[Dict]):
        """Envoie une notification groupée pour plusieurs bons plans"""
        if not deals:
            return
        
        total_savings = sum(deal['savings'] for deal in deals)
        
        message = f"🎉 *{len(deals)} MEILLEUR(S) PRIX TROUVÉ(S) !*\n\n"
        
        for i, deal in enumerate(deals, 1):
            trip = deal['trip']
            message += f"*{i}.* {trip['origin']} → {trip['destination']}\n"
            message += f"   📅 {trip['outbound_date']}\n"
            message += f"   💰 {deal['new_price']}€ au lieu de {trip['current_price']}€\n"
            message += f"   ✅ Économie: {deal['savings']:.2f}€\n\n"
        
        message += f"💸 *Économie totale: {total_savings:.2f}€*"
        
        self.send_message(message)
    
    def send_daily_summary(self, trips_checked: int, deals_found: int):
        """Envoie un résumé quotidien"""
        message = f"""
📊 *Résumé quotidien*

✅ {trips_checked} trajet(s) vérifiés
{'🎉 ' + str(deals_found) + ' meilleur(s) prix trouvé(s)' if deals_found > 0 else '😊 Aucun meilleur prix aujourd\'hui'}

_Prochaine vérification dans 6h_
        """.strip()
        
        self.send_message(message)


def get_notifier_from_env() -> TelegramNotifier:
    """Récupère le notifier depuis les variables d'environnement"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID doivent être définis "
            "dans les secrets GitHub"
        )
    
    return TelegramNotifier(bot_token, chat_id)


if __name__ == "__main__":
    # Test de notification
    try:
        notifier = get_notifier_from_env()
        notifier.send_message("✅ Bot SNCF configuré avec succès !")
    except ValueError as e:
        print(f"❌ {e}")

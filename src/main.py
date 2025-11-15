#!/usr/bin/env python3
"""
Script principal pour vérifier les prix SNCF et envoyer des notifications
"""
import sys
from datetime import datetime

# Import des modules locaux
from scraper import check_all_trips
from notifier import get_notifier_from_env

def main():
    print("="*70)
    print(f"🚄 SNCF Price Checker - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        # Initialiser le notifier Telegram
        notifier = get_notifier_from_env()
        print("✅ Telegram configuré\n")
        
        # Vérifier tous les trajets
        better_deals = check_all_trips()
        
        # Envoyer les notifications si des bons plans sont trouvés
        if better_deals:
            print(f"\n{'='*70}")
            print(f"🎉 {len(better_deals)} meilleur(s) prix trouvé(s) !")
            print("📱 Envoi de la notification Telegram...")
            
            notifier.notify_multiple_deals(better_deals)
            print("✅ Notification envoyée avec succès")
        else:
            print(f"\n{'='*70}")
            print("😊 Aucun meilleur prix pour le moment")
        
        print("="*70)
        return 0
        
    except ValueError as e:
        print(f"❌ Erreur de configuration: {e}")
        print("💡 Vérifiez que les secrets TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID sont bien définis")
        return 1
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        
        # Tenter d'envoyer une notification d'erreur
        try:
            notifier = get_notifier_from_env()
            notifier.send_message(f"❌ Erreur lors de la vérification des prix:\n```\n{str(e)}\n```")
        except:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

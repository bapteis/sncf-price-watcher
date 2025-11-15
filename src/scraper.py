import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import random

class SNCFPriceChecker:
    def __init__(self):
        self.base_url = "https://www.sncf-connect.com/bff/api/v1/itineraries"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "fr,fr-FR;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "x-bff-key": "ah1MPO-izehIHD-QZZ9y88n-kku876",
            "x-client-channel": "web",
            "x-client-app-id": "front-web",
            "x-market-locale": "fr_FR",
            "x-api-env": "production",
            "Origin": "https://www.sncf-connect.com",
            "Referer": "https://www.sncf-connect.com/home/shop/results/outward",
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
    
    def search_round_trip(self, origin: str, destination: str, 
                         outbound_date: str, outbound_time: str,
                         return_date: str, return_time: str,
                         flexibility_hours: int = 3) -> Optional[Dict]:
        """
        Recherche les prix pour un aller-retour avec carte Avantage
        
        Returns:
            Dict avec les informations du meilleur prix ou None si erreur
        """
        print(f"🔍 Recherche {origin} → {destination}")
        print(f"   Aller: {outbound_date} ~{outbound_time}")
        print(f"   Retour: {return_date} ~{return_time}")
        
        # Convertir la date et l'heure en timestamp ISO (format UTC)
        outbound_datetime = datetime.strptime(f"{outbound_date} 05:00:00", "%Y-%m-%d %H:%M:%S")
        return_datetime = datetime.strptime(f"{return_date} 05:00:00", "%Y-%m-%d %H:%M:%S")
        
        payload = {
            "schedule": {
                "outward": {
                    "date": outbound_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "arrivalAt": False
                },
                "inward": {
                    "date": return_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                }
            },
            "mainJourney": {
                "origin": {
                    "label": origin,
                    "codes": [],
                    "geolocation": False
                },
                "destination": {
                    "label": destination,
                    "codes": [],
                    "geolocation": False
                }
            },
            "passengers": [{
                "id": "passenger-1",
                "discountCards": [{
                    "code": "WEEKEND_PASS",
                    "label": "Carte Avantage Adulte",
                    "isChecked": True
                }],
                "typology": "ADULT",
                "withoutSeatAssignment": False,
                "hasDisability": False,
                "hasWheelchair": False
            }],
            "pets": [],
            "branch": "SHOP",
            "forceDisplayResults": True,
            "trainExpected": True,
            "wishBike": False,
            "strictMode": False,
            "directJourney": False,
            "transporterLabels": []
        }
        
        try:
            # Délai aléatoire pour paraître plus humain
            time.sleep(random.uniform(1, 3))
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Parser les résultats
            best_price = self._extract_best_price(
                data, outbound_time, return_time, flexibility_hours
            )
            
            return best_price
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Code: {e.response.status_code}")
                print(f"   Réponse: {e.response.text[:200]}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de parsing JSON: {e}")
            return None
    
    def _parse_price(self, price_str: str) -> float:
        """Convertit '65 €' en 65.0"""
        try:
            return float(price_str.replace('€', '').replace(',', '.').strip())
        except:
            return 0.0
    
    def _parse_time(self, time_str: str) -> tuple:
        """Convertit '08:18' en (8, 18)"""
        try:
            h, m = time_str.split(':')
            return (int(h), int(m))
        except:
            return (0, 0)
    
    def _time_diff_minutes(self, time1_str: str, time2_str: str) -> int:
        """Calcule la différence en minutes entre deux heures"""
        h1, m1 = self._parse_time(time1_str)
        h2, m2 = self._parse_time(time2_str)
        return abs((h1 * 60 + m1) - (h2 * 60 + m2))
    
    def _extract_best_price(self, data: Dict, target_out_time: str, 
                           target_ret_time: str, flex_hours: int) -> Optional[Dict]:
        """
        Extrait le meilleur prix des résultats SNCF
        Structure : data['longDistance']['proposals']['proposals']
        """
        try:
            proposals = data.get('longDistance', {}).get('proposals', {}).get('proposals', [])
            
            if not proposals:
                print("⚠️  Aucune proposition trouvée")
                return None
            
            best_price = None
            best_total = float('inf')
            flex_minutes = flex_hours * 60
            
            print(f"   Analyse de {len(proposals)} propositions...")
            
            for proposal in proposals:
                # Vérifier si le train est réservable
                status = proposal.get('status', {})
                if not status.get('isBookable', False):
                    continue
                
                # Extraire l'heure de départ
                departure_time = proposal.get('departure', {}).get('timeLabel', '')
                if not departure_time:
                    continue
                
                # Vérifier si dans la plage horaire
                time_diff = self._time_diff_minutes(departure_time, target_out_time)
                if time_diff > flex_minutes:
                    continue
                
                # Chercher le meilleur prix parmi les offres 2de classe
                second_class = proposal.get('secondComfortClassOffers', {})
                offers = second_class.get('offers', [])
                
                for offer in offers:
                    price_str = offer.get('priceLabel', '0 €')
                    price = self._parse_price(price_str)
                    
                    if price > 0 and price < best_total:
                        best_total = price
                        best_price = {
                            'total_price': price,
                            'outbound_departure': departure_time,
                            'train_number': proposal.get('globalTimeline', {})
                                .get('steps', [{}])[1]
                                .get('train', {})
                                .get('transporter', {})
                                .get('number', 'N/A'),
                            'origin_station': proposal.get('departure', {}).get('originStationLabel', ''),
                            'destination_station': proposal.get('arrival', {}).get('destinationStationLabel', ''),
                            'duration': proposal.get('durationLabel', ''),
                            'transporter': proposal.get('transporterDescription', ''),
                            'comfort_class': 'SECOND',
                            'fare_name': offer.get('header', {}).get('subtitle', 'Tarif standard')
                        }
                
                # Chercher aussi en 1re classe si pas de 2de classe
                if not offers:
                    first_class = proposal.get('firstComfortClassOffers', {})
                    first_offers = first_class.get('offers', [])
                    
                    for offer in first_offers:
                        price_str = offer.get('priceLabel', '0 €')
                        price = self._parse_price(price_str)
                        
                        if price > 0 and price < best_total:
                            best_total = price
                            best_price = {
                                'total_price': price,
                                'outbound_departure': departure_time,
                                'train_number': proposal.get('globalTimeline', {})
                                    .get('steps', [{}])[1]
                                    .get('train', {})
                                    .get('transporter', {})
                                    .get('number', 'N/A'),
                                'origin_station': proposal.get('departure', {}).get('originStationLabel', ''),
                                'destination_station': proposal.get('arrival', {}).get('destinationStationLabel', ''),
                                'duration': proposal.get('durationLabel', ''),
                                'transporter': proposal.get('transporterDescription', ''),
                                'comfort_class': 'FIRST',
                                'fare_name': offer.get('header', {}).get('subtitle', 'Tarif standard')
                            }
            
            if best_price:
                print(f"✅ Meilleur prix : {best_price['total_price']}€")
                print(f"   Train: {best_price['transporter']} {best_price['train_number']}")
                print(f"   Départ: {best_price['outbound_departure']} ({best_price['duration']})")
                return best_price
            else:
                print("⚠️  Aucun train dans la plage horaire ou prix disponible")
                return None
                
        except Exception as e:
            print(f"❌ Erreur extraction prix: {e}")
            import traceback
            traceback.print_exc()
            return None


def load_trips(filename: str = "data/my_trips.json") -> List[Dict]:
    """Charge la liste de vos trajets depuis le fichier JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('trips', [])
    except FileNotFoundError:
        print(f"⚠️  Fichier {filename} introuvable")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return []


def check_all_trips():
    """Vérifie tous les trajets configurés"""
    checker = SNCFPriceChecker()
    trips = load_trips()
    
    if not trips:
        print("Aucun trajet à vérifier")
        return []
    
    print(f"📋 {len(trips)} trajet(s) à vérifier\n")
    
    results = []
    
    for i, trip in enumerate(trips, 1):
        print(f"\n{'='*60}")
        print(f"Trajet {i}/{len(trips)}")
        
        # Vérifier que le trajet est dans le futur
        outbound_date = datetime.strptime(trip['outbound_date'], '%Y-%m-%d')
        if outbound_date < datetime.now():
            print(f"⏭️  Trajet déjà passé, ignoré")
            continue
        
        # Rechercher les prix actuels (uniquement pour l'aller dans cette version)
        best_result = checker.search_round_trip(
            origin=trip['origin'],
            destination=trip['destination'],
            outbound_date=trip['outbound_date'],
            outbound_time=trip['outbound_time'],
            return_date=trip['return_date'],
            return_time=trip['return_time'],
            flexibility_hours=trip.get('flexibility_hours', 3)
        )
        
        if best_result and best_result['total_price'] < trip['current_price']:
            savings = trip['current_price'] - best_result['total_price']
            results.append({
                'trip': trip,
                'new_price': best_result['total_price'],
                'savings': savings,
                'details': best_result
            })
            print(f"💰 PRIX INFÉRIEUR TROUVÉ!")
            print(f"   Prix actuel: {trip['current_price']}€")
            print(f"   Nouveau prix: {best_result['total_price']}€")
            print(f"   Économie: {savings:.2f}€")
        elif best_result:
            print(f"✅ Pas de meilleur prix")
            print(f"   Actuel: {trip['current_price']}€ | Trouvé: {best_result['total_price']}€")
        else:
            print(f"⚠️  Erreur lors de la recherche")
        
        # Pause entre chaque trajet pour éviter le rate limiting
        time.sleep(3)
    
    return results


if __name__ == "__main__":
    print("🚄 SNCF Price Checker")
    print("="*60)
    better_deals = check_all_trips()
    
    if better_deals:
        print(f"\n🎉 {len(better_deals)} meilleur(s) prix trouvé(s)!")
        for deal in better_deals:
            print(f"\n{deal['trip']['origin']} → {deal['trip']['destination']}")
            print(f"  Économie: {deal['savings']:.2f}€")
    else:
        print("\n😊 Aucun meilleur prix pour le moment")

import sys
import os

# Ajouter le chemin racine du backend pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database.database import engine
from sqlalchemy import text

def run():
    print("Début de la migration de la table utilisateurs...")
    try:
        with engine.connect() as conn:
            # PostgreSQL syntax: ADD COLUMN IF NOT EXISTS
            print("Ajout de la colonne 'langue'...")
            conn.execute(text("ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS langue VARCHAR(10) DEFAULT 'fr' NOT NULL;"))
            
            print("Ajout de la colonne 'notif_email'...")
            conn.execute(text("ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS notif_email BOOLEAN DEFAULT TRUE NOT NULL;"))
            
            print("Ajout de la colonne 'notif_commandes'...")
            conn.execute(text("ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS notif_commandes BOOLEAN DEFAULT TRUE NOT NULL;"))
            
            print("Ajout de la colonne 'notif_promotions'...")
            conn.execute(text("ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS notif_promotions BOOLEAN DEFAULT FALSE NOT NULL;"))
            
            print("Ajout de la colonne 'notif_newsletter'...")
            conn.execute(text("ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS notif_newsletter BOOLEAN DEFAULT TRUE NOT NULL;"))
            
            conn.commit()
            print("Migration terminée avec succès !")
    except Exception as e:
        print(f"Erreur lors de la migration : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run()

from app.database.database import SessionLocal
from modules.utilisateurs.models import Utilisateur, RoleEnum
from modules.auth.service import hasher_mot_de_passe
from sqlalchemy import select

def creer_administrateur():
    db = SessionLocal()
    try:
        existant = db.execute(
            select(Utilisateur).where(Utilisateur.email == "johann@gmail.com")
        ).scalar_one_or_none()

        if existant:
            print("Un administrateur avec cet email existe déjà.")
            return

        admin = Utilisateur(
            nom="Liebert",
            prenom="Johann",
            email="johann@gmail.com",
            mot_de_passe_hash=hasher_mot_de_passe("Joh@nn00securex9"),
            role=RoleEnum.admin,
            est_actif=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Administrateur créé avec succès : {admin.prenom} {admin.nom} ({admin.email})")
    finally:
        db.close()

if __name__ == "__main__":
    creer_administrateur()

"""
Seed du catalogue "Sagesse Africaine" — remplace les 9 livres placeholder
(mal encodés) par les 21 livres réels de la collection
"LUMIÈRE ET VÉRITÉ SUR LE MONDE DES TÉNÈBRES", avec des slugs qui
correspondent exactement aux ids statiques du frontend (src/data/livresSite.js).
"""
import uuid
from app.database.database import SessionLocal
from modules.livres.models import Livre
from modules.collections.models import Collection
from modules.fichiers_livres.models import FichierLivre  # requis pour résoudre la relation Livre.fichiers
from sqlalchemy import select

AUTEUR = "SIDA ABENA Jean Paul Sylvain"
PRIX = 6500
LANGUE = "Français"

COLLECTION_ID = uuid.UUID("1ad43801-da87-4df5-b1e0-5a08e614160d")
COLLECTION_NOM = "LUMIÈRE ET VÉRITÉ SUR LE MONDE DES TÉNÈBRES"
COLLECTION_DESCRIPTION = "Collection pour la promotion de la Médecine Traditionnelle des Handicapés Spirituels (MTHS)"

AUTRE_COLLECTION_ID = uuid.UUID("d89aaece-5a41-4a95-84d8-98be0123808c")
AUTRE_COLLECTION_DESCRIPTION = "Les cas d'école pour connaître le passé, maîtriser le présent, s'en inspirer pour le futur"

LIVRES = [
    dict(
        slug="ange-ou-demon",
        titre="Ange ou Démon ?",
        couverture_url="/images/livres-site/Ange%20ou%20demon/premiere_couverture.png",
        description="Découvrez dans « Ange ou Démon ? » une exploration saisissante de la nature spirituelle profonde de l'Homme, composé de quatre entités indissociables : le corps, l'esprit-central, le Saint-Esprit et l'esprit de tentation. Entre monde visible et invisible, ce livre dévoile comment l'âme, guidée par le Saint-Esprit, affronte sans cesse les forces obscures qui tentent de dominer notre destin. Grâce à une approche clinique inédite de la Médecine Traditionnelle des Handicapés Spirituels, l'auteur offre des clés concrètes pour comprendre ces luttes invisibles et reprendre le contrôle de sa vie spirituelle.",
    ),
    dict(
        slug="chretien-africain-et-la-maladie",
        titre="Chrétien Africain et la Maladie",
        couverture_url="/images/livres-site/Chr%C3%A9tien%20Africain%20et%20la%20Maladie/premiere_couverture.png",
        description="Dans « Chrétien Africain et la Maladie », l'Association Mariale d'Abili livre une œuvre dense et audacieuse au carrefour de la théologie pastorale, de l'anthropologie africaine et de la Médecine Traditionnelle des Handicapés Spirituels. La maladie y est envisagée non comme un simple fait biologique, mais comme une épreuve existentielle mêlant souffrances psychiques, blessures spirituelles et quête de sens. Face aux dérives du 3ème millénaire, l'ouvrage plaide pour une pastorale renouvelée et responsable — un appel vibrant à une Église africaine guérissante, lucide et compatissante envers les malades.",
    ),
    dict(
        slug="chretien-africain-face-a-la-sorcellerie",
        titre="Chrétien Africain face à la Sorcellerie",
        couverture_url="/images/livres-site/CHR%C3%89TIEN%20AFRICAIN%20FACE%20%20%C3%80%20LA%20SORCELLERIE/premiere_couverture.png",
        description="La sorcellerie en Afrique n'est pas un mythe mais une réalité vécue, qui fragilise les consciences et enferme de nombreux « handicapés spirituels » dans la peur, la culpabilité et le silence. Face à ce phénomène, le chrétien africain se retrouve souvent désarmé, tiraillé entre une foi peu incarnée et des pratiques traditionnelles mal comprises. Grâce à la Médecine Traditionnelle des Handicapés Spirituels (MTHS), ce livre propose une lecture audacieuse et thérapeutique de la sorcellerie, éclairée par l'anthropologie africaine et la foi chrétienne — un véritable guide pastoral pour dépasser la peur et accompagner les âmes blessées vers la guérison.",
    ),
    dict(
        slug="comment-comprendre-et-interpreter-le-reve",
        titre="Comment Comprendre et Interpréter le Rêve ?",
        couverture_url="/images/livres-site/Comment%20Comprendre%20et%20interpreter%20le%20R%C3%AAve/premiere_couverture.png",
        description="Et si vos rêves étaient bien plus que de simples images nocturnes, mais un langage subtil reliant le visible à l'invisible, le corps à l'esprit ? À travers l'approche originale de la Médecine Traditionnelle des Handicapés Spirituels (MTHS), ce livre offre une lecture clinique et spirituelle du monde onirique, alliant observation, discernement et sagesse traditionnelle. Il donne des clés concrètes pour interpréter les symboles, identifier les blocages spirituels et amorcer un chemin de guérison intérieure — un ouvrage audacieux pour donner du sens à vos nuits et transformer vos jours.",
    ),
    dict(
        slug="comment-obtenir-ta-delivrance-et-ta-victoire-sur-le-diable-les-demons-et-les-sorciers",
        titre="Comment obtenir ta Délivrance et ta Victoire sur le Diable, les Démons et les Sorciers",
        couverture_url="/images/livres-site/Comment%20obtenir%20ta%20D%C3%A9livrance%20et%20ta%20Victoire%20contre%20le%20Diable%20les%20D%C3%A9mons%20et%20les%20Sorciers/premiere_couverture.png",
        description="Depuis toujours, l'humanité reconnaît l'existence d'un combat invisible qui influence profondément la vie des hommes : attaques spirituelles, envoûtements, manipulations occultes et sorcellerie sont, pour beaucoup, une source réelle d'angoisse et de désorientation. Ce guide pratique rappelle une vérité essentielle : nul n'est condamné à vivre sous l'emprise des forces des ténèbres. Fondé sur l'expérience thérapeutique de la Médecine Traditionnelle des Handicapés Spirituels (MTHS), il accompagne pas à pas le lecteur vers la prise de conscience, la rupture avec les forces obscures et une protection spirituelle durable.",
    ),
    dict(
        slug="comment-te-soigner-des-persecutions-spirituelles-des-maladies-et-sorts-de-sorcellerie",
        titre="Comment te Soigner des Persécutions Spirituelles, des Maladies et Sorts de Sorcellerie ?",
        couverture_url="/images/livres-site/Comment%20se%20soigner%20des%20pers%C3%A9cutions%20spirituelles/premiere_couverture.png",
        description="La Médecine Traditionnelle des Handicapés Spirituels, née il y a trente ans au sein de la Clinique spirituelle Marie Reine de la Miséricorde d'Abili au Cameroun, vient en aide aux « handicapés spirituels » — ces personnes envoûtées, perturbées et exploitées par le Malin sans même le savoir. Troubles du comportement, cauchemars récurrents, maux persistants : autant de signes qui poussent souvent les victimes vers des marabouts et charlatans, au risque de trahir leur foi. Ce livre répond à une question essentielle : comment se soigner des persécutions spirituelles sans renier le Seigneur Jésus-Christ ? Un guide clinique et spirituel pour se protéger et guérir en toute fidélité à l'Évangile.",
    ),
    dict(
        slug="comment-vivre-ensemble-avec-les-sorciers",
        titre="Comment Vivre-ensemble avec les Sorciers",
        couverture_url="/images/livres-site/Comment%20vivre-ensemble%20avec%20les%20Sorciers/premiere_couverture.png",
        description="La sorcellerie divise, effraie et détruit silencieusement de nombreuses familles africaines : accusations hâtives, délivrances violentes, exclusions injustes sacrifient trop souvent la paix familiale au nom de la lutte contre le mal. À contre-courant des discours extrêmes, ce livre invite à un changement radical de regard, où la sorcellerie n'est ni niée ni banalisée mais comprise comme un handicap spirituel nécessitant discernement et soin. Un ouvrage nécessaire pour transformer la peur en discernement, et la violence en paix durable au sein de la famille.",
    ),
    dict(
        slug="les-consequences-spirituelles-de-la-masturbation-et-de-la-pornographie-dans-ta-vie",
        titre="Les Conséquences Spirituelles de la Masturbation et de la Pornographie dans ta Vie",
        couverture_url="/images/livres-site/CONSEQUENCES%20SPIRITUELLES%20DE%20LA%20MASTURBATION%20ET%20DE%20LA%20PORNOGRAPHIE%20DANS%20TA%20VIE/premiere_couverture.png",
        description="Ce livre percutant lève le voile sur les dimensions invisibles et souvent taboues de la masturbation et de la pornographie, révélant leurs impacts sur l'énergie vitale, l'équilibre spirituel et la réussite sociale. À travers une plume immersive, l'auteur décrypte le concept de « décharge d'énergie » et les « maladies mystiques » qui en découleraient, ainsi que les blocages socioprofessionnels. Un ouvrage révélateur qui invite à une véritable prise de conscience et à un chemin de restauration personnelle.",
    ),
    dict(
        slug="culture-de-la-paix-et-lutte-contre-la-deviance-spirituelle-dans-le-monde",
        titre="Culture de la Paix et Lutte contre la Déviance Spirituelle dans le Monde",
        couverture_url="/images/livres-site/CULTURE%20DE%20LA%20PAIX%20ET%20LUTTE%20CONTRE%20LA%20D%C3%89VIANCE%20SPIRITUELLE/premiere_couverture.png",
        description="Dans un monde bousculé par l'anxiété existentielle et la fragmentation du sens humain, cet ouvrage de référence propose une approche inédite de la Médecine Traditionnelle des Handicapés Spirituels (MTHS) pour comprendre, prévenir et guérir les désordres spirituels qui minent individus et sociétés. Par une méthodologie interreligieuse et intégrale, l'auteur montre comment restaurer la paix intérieure et la cohésion sociale. Un appel universel à la réconciliation entre science et sagesse, essentiel pour thérapeutes, leaders religieux et éducateurs.",
    ),
    dict(
        slug="la-guerre-des-spiritualites-en-afrique",
        titre="La Guerre des Spiritualités en Afrique",
        couverture_url="/images/livres-site/La%20Guerre%20des%20Spiritualit%C3%A9s%20en%20Afrique/premiere_couverture.png",
        description="Une plongée lucide et courageuse au cœur des conflits spirituels silencieux qui traversent l'Afrique, entre religions du Décalogue, traditions africaines et loges ésotériques occidentales. À travers l'approche clinique de la Médecine Traditionnelle des Handicapés Spirituels (MTHS), l'auteur décrypte syncrétisme, doubles appartenances et pactes invisibles à l'origine de fragmentation identitaire et de dépendance spirituelle. Un ouvrage qui invite leaders spirituels, thérapeutes et décideurs à repenser la guérison comme réconciliation profonde entre foi, culture et vie.",
    ),
    dict(
        slug="la-puissance-spirituelle-du-sexe",
        titre="La Puissance Spirituelle du Sexe",
        couverture_url="/images/livres-site/la%20puissance%20spirituelle%20du%20sexe/premiere_couverture.png",
        description="Et si le sexe était l'un des plus puissants vecteurs d'influence spirituelle sur l'être humain ? Cet ouvrage audacieux explore les liens méconnus entre sexualité, vulnérabilité spirituelle et domination invisible. À la croisée de la clinique traditionnelle africaine et d'une lecture spirituelle approfondie, l'auteur dévoile comment des forces obscures exploiteraient les déséquilibres intimes pour asservir les consciences et perturber les trajectoires de vie. Un livre puissant, destiné à éveiller et à équiper toute personne en quête de liberté intérieure et de maîtrise de soi.",
    ),
    dict(
        slug="la-sorcellerie-au-dessus-de-la-foi",
        titre="La Sorcellerie au-dessus de la Foi",
        couverture_url="/images/livres-site/la%20Sorcellerie%20au%20Dessus%20de%20la%20foi/premiere_couverture.png",
        description="Pourquoi le Mal, la déviance spirituelle et la sorcellerie semblent-ils dominer les hommes sur Terre ? Cet ouvrage audacieux et interdisciplinaire croise anthropologie, psychologie clinique et savoirs endogènes africains pour interroger les mécanismes par lesquels le mal devient une grille de lecture du monde. En s'appuyant sur la Médecine Traditionnelle des Handicapés Spirituels (MTHS), l'auteur propose une lecture innovante des troubles dits « spirituels ».",
    ),
    dict(
        slug="la-vie-apres-la-mort",
        titre="La Vie après la Mort",
        couverture_url="/images/livres-site/La%20Vie%20apr%C3%A8s%20la%20Mort/premiere_couverture.png",
        description="Et si la mort n'était pas une fin, mais un passage vers une existence exigeante et merveilleusement ordonnée ? Ayant vécu simultanément parmi les vivants et les défunts, l'auteur livre ici un témoignage et un guide unique sur le Purgatoire et le monde spirituel. À travers une approche clinique de la Médecine Traditionnelle des Handicapés Spirituels, il explique comment dialoguer avec les âmes, intercéder pour les défunts et renforcer sa protection spirituelle.",
    ),
    dict(
        slug="la-vie-spirituelle-du-sorcier",
        titre="La Vie Spirituelle du Sorcier",
        couverture_url="/images/livres-site/La%20Vie%20spirituelle%20du%20Sorcier%20-Univers%20Astral%20de%20la%20Sorcellerie/premiere_couverture.png",
        description="Que se passe-t-il vraiment la nuit, lorsque le corps du sorcier repose mais que son esprit voyage dans l'univers astral de la sorcellerie ? Ce livre saisissant dévoile le phénomène du dédoublement astral, jusqu'aux lieux où se tiendraient les réunions spirituelles des sorciers et les sorts qui s'y décident. Une plongée rare et troublante dans l'invisible.",
    ),
    dict(
        slug="le-musulman-face-a-la-sorcellerie",
        titre="Le Musulman face à la Sorcellerie",
        couverture_url="/images/livres-site/LE%20MUSULMAN%20FACE%20A%20LA%20SORCELLERIE/premiere_couverture.png",
        description="Dans l'Afrique contemporaine, la sorcellerie fragilise les familles, isole les victimes et met à l'épreuve la foi. À travers la Médecine Traditionnelle des Handicapés Spirituels (MTHS), fondée sur la théologie islamique, la sagesse soufie et l'anthropologie africaine, ce guide offre aux imams, praticiens et leaders communautaires des outils concrets pour identifier, accompagner et guérir.",
    ),
    dict(
        slug="le-remede-traditionnel-ameliore-post-covid-19",
        titre="Le Remède Traditionnel Amélioré post-Covid-19",
        couverture_url="/images/livres-site/Le%20Rem%C3%A8de%20Traditionnel%20Am%C3%A9lior%C3%A9/premiere_couverture.png",
        description="La pandémie de Covid-19 a révélé les failles des systèmes de santé africains, mais aussi la richesse trop souvent négligée des savoirs thérapeutiques endogènes. Ancré dans la Médecine Traditionnelle des Handicapés Spirituels (MTHS), cet ouvrage défend une approche holistique du soin, alliant remèdes traditionnels améliorés, validation scientifique et accompagnement spirituel.",
    ),
    dict(
        slug="l-hygiene-de-l-ame",
        titre="L'Hygiène de l'Âme",
        couverture_url="/images/livres-site/L'Hygi%C3%A8ne%20de%20l'%C3%A2me/premiere_couverture.png",
        description="Et si la véritable santé commençait au cœur de l'âme ? Face au stress et à la perte de repères spirituels, ce livre propose une approche novatrice à la croisée de la science, de la théologie et des savoirs traditionnels, fondée sur la Médecine Traditionnelle des Handicapés Spirituels (MTHS). Guide pratique et parcours initiatique à la fois.",
    ),
    dict(
        slug="les-consequences-du-phenomene-de-maris-et-femmes-de-nuit",
        titre="Les Conséquences du Phénomène de Maris et Femmes de Nuit",
        couverture_url="/images/livres-site/MARIS%20ET%20FEMMES%20DE%20NUIT/premiere_couverture.png",
        description="Pourquoi tant de femmes et d'hommes de qualité peinent-ils à construire une relation conjugale stable et épanouissante ? À travers une approche clinique novatrice inspirée de la Médecine Traditionnelle des Handicapés Spirituels (MTHS), ce livre décrypte les blocages affectifs, les échecs relationnels répétés et les expériences spirituelles souvent tues.",
    ),
    dict(
        slug="enjeux-et-defis-du-controle-spirituel-de-l-homme",
        titre="Enjeux et Défis du Contrôle Spirituel de l'Homme",
        couverture_url="/images/livres-site/Sectes%20et%20Soci%C3%A9t%C3%A9s%20Secr%C3%A8tes%20africaines/premiere_couverture.png",
        description="Dans un monde où le pouvoir invisible façonne les consciences, ce livre explore avec rigueur les mécanismes de contrôle spirituel à l'œuvre dans les sociétés initiatiques secrètes africaines, les sectes contemporaines et les loges exotériques occidentales. Grâce à la Médecine Traditionnelle des Handicapés Spirituels (MTHS), il décrypte comment traditions, rituels et symboles peuvent être détournés pour dominer l'homme.",
    ),
    dict(
        slug="l-avenir-des-traditions-ancestrales-africaines-et-le-christianisme",
        titre="L'Avenir des Traditions ancestrales africaines et le Christianisme",
        couverture_url="/images/livres-site/Traditions%20africaines%20et%20Christianisme/premiere_couverture.png",
        description="Entre héritages ancestraux et christianisme importé, l'Afrique contemporaine se tient à une croisée décisive : faut-il tout rejeter pour croire, ou tout mélanger pour survivre ? S'appuyant sur la Médecine Traditionnelle des Handicapés Spirituels (MTHS), ce livre explore les souffrances nées des syncrétismes inconscients et des ruptures culturelles mal accompagnées.",
    ),
    dict(
        slug="la-transmission-de-la-sorcellerie-au-sein-de-la-famille",
        titre="La Transmission de la Sorcellerie au sein de la Famille",
        couverture_url="/images/livres-site/Transmission%20de%20la%20Sorcellerie%20au%20sein%20de%20la%20famille/premiere_couverture.png",
        description="Comment la sorcellerie se transmet-elle au sein des familles ? Ce livre plonge au cœur de l'Évu, ce germe de l'envoûtement transmis comme une empreinte spirituelle à travers les lignées, à la lumière de la Médecine Traditionnelle des Handicapés Spirituels (MTHS). L'auteur y dévoile les liens entre maladies mystiques, blocages répétitifs et héritages spirituels non purifiés.",
    ),
]

assert len(LIVRES) == 21, f"Attendu 21 livres, trouvé {len(LIVRES)}"
assert len({l['slug'] for l in LIVRES}) == 21, "Slugs dupliqués détectés"


def run():
    db = SessionLocal()
    try:
        # 1) Nettoyer l'encodage des collections existantes
        collection = db.execute(
            select(Collection).where(Collection.id == COLLECTION_ID)
        ).scalar_one_or_none()
        if collection:
            collection.nom = COLLECTION_NOM
            collection.description = COLLECTION_DESCRIPTION
        else:
            collection = Collection(
                id=COLLECTION_ID,
                nom=COLLECTION_NOM,
                slug="lumiere-et-verite-sur-le-monde-des-tenebres",
                description=COLLECTION_DESCRIPTION,
            )
            db.add(collection)

        autre_collection = db.execute(
            select(Collection).where(Collection.id == AUTRE_COLLECTION_ID)
        ).scalar_one_or_none()
        if autre_collection:
            autre_collection.description = AUTRE_COLLECTION_DESCRIPTION

        db.commit()

        # 2) Supprimer les 9 livres placeholder (cascade vers fichiers_livres)
        anciens = db.execute(select(Livre)).scalars().all()
        for livre in anciens:
            db.delete(livre)
        db.commit()
        print(f"{len(anciens)} ancien(s) livre(s) supprimé(s).")

        # 3) Insérer les 21 nouveaux livres
        for data in LIVRES:
            livre = Livre(
                titre=data["titre"],
                slug=data["slug"],
                auteur=AUTEUR,
                description=data["description"],
                couverture_url=data["couverture_url"],
                langue=LANGUE,
                prix=PRIX,
                est_gratuit=False,
                est_publie=True,
                collection_id=collection.id,
            )
            db.add(livre)
        db.commit()
        print(f"{len(LIVRES)} nouveau(x) livre(s) inséré(s).")

    finally:
        db.close()


if __name__ == "__main__":
    run()

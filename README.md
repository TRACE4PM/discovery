# discovery



## Add your files

```
cd existing_repo
git remote add origin https://gitlab.univ-lr.fr/trace_clustering/services/discovery.git
git branch -M main
git push -uf origin main
```

## Installation and Configuration
- Pour utiliser le service discover dans le projet, il faut juste l'installer comme un module python. Dans notre cas, avec poetry, il suffit d'exécuter les différentes étapes suivantes :
    - Inclure le lien du dépôt du service dans le fichier de configuration (pyproject.toml) du projet dans la section [tool.poetry.dependencies] de la manière suivante (discover = {git = "https://gitlab.univ-lr.fr/trace_clustering/services/discovery.git"})
    - Installer le service comme un module avec la commande suivante (poetry add discover)
    - Importer les fonctions du service comme on importe n'importe quel module python par exemple (from discover.main import heuristic_miner) et importer l'algorithm de process discovery que vous voulez utiliser
    - Installer R  et quelqes packages necessaire pour le fonctionnement de l'animation
```
  install.packages("bupaR")
  install.packages("curl")
  install.packages("dplyr")
  install.packages("xesreadR")
  install.packages("processanimateR")
   ```
Dependencies : (a tester si ça peut marcher sans les installer) 
```
  install.packages("magrittr")
  install.packages("rmarkdown")
  install.packages("plotly")
  install.packages("openssl")
  install.packages("igraph")
  install.packages("DiagrammeR")
  install.packages("processmapR")
```

### Fonctionnement du discover 
Ce service discover implémente plusieurs algorithmes pour le process discovery des fichiers logs en utilisant la packet PM4PY. 
Les algorithmes peuvent traiter des fichiers en format `.csv` ou `.xes`.
Chaque algorithme a 2 fonctions, comme par exemple le Alpha miner, on a la fonction `alpha_miner_algo ` qui  génère un **modele Petri Net** et le sauvegarder en tant que png dans un fichier temp. 
Le 2eme fonction sert a déterminer la qualité du modèle généré, en calculant les mesures : la fitness,la précision, la généralisation
et la simplicité. Cette fonction retourne un fichier Zip qui contient: 
- un PNG du modèle généré par l'algorithme 
- un JSON des mesures de qualités calculé
- un pnml file.
En ce qui concerne le calcul de la fitness et la précision 2 approches sont proposées : 
- Token based 
- Alignemet based 

Ce service implémente également une fonction `process_animate` qui produit une animation du fichier log en utilisant 
la librairie `processanimateR` du packet `BupaR`, il faut donc avoir installé un environnement R et les librairies 
necessaires. 



### Contributions et Améliorations

Les contributions à ce projet sont les bienvenues. Si vous souhaitez apporter des améliorations, veuillez suivre les étapes suivantes :

    Forkez le dépôt et clonez votre propre copie.
    Créez une branche pour vos modifications : git checkout -b feature/ma-nouvelle-fonctionnalite
    Effectuez les modifications nécessaires et testez-les de manière approfondie.
    Soumettez une pull request en expliquant en détail les modifications apportées et leur impact.

### Auteur(s)

    - Amira Ania DAHACHE

### Licence

Ce projet est sous licence L3I.

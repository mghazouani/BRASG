# 📋 Plan d’Action Priorisé DBA PostgreSQL (PAP_DBA)

## 1. Sécurisation de l’accès à la base
- [ ] Créer un utilisateur PostgreSQL dédié à l’application avec les droits minimaux nécessaires
- [ ] Désactiver l’accès superutilisateur pour les connexions applicatives
- [ ] Restreindre l’accès réseau à la base (firewall, listen_addresses)
- [ ] Changer le mot de passe de l’utilisateur DB régulièrement

## 2. Sauvegardes et restauration
- [ ] Mettre en place une sauvegarde automatique quotidienne (pg_dump, outils dédiés)
- [ ] Tester régulièrement la restauration à partir des sauvegardes
- [ ] Stocker les sauvegardes sur un support externe sécurisé
- [ ] Documenter la procédure de restauration

## 3. Surveillance et maintenance
- [ ] Mettre en place la supervision des logs PostgreSQL (erreurs, accès, requêtes lentes)
- [ ] Configurer des alertes sur espace disque, erreurs critiques, connexions anormales
- [ ] Mettre à jour PostgreSQL et appliquer les correctifs de sécurité
- [ ] Activer et surveiller l’autovacuum
- [ ] Vérifier régulièrement les index et la fragmentation

## 4. Optimisation et bonnes pratiques
- [ ] Limiter le nombre de connexions simultanées (max_connections)
- [ ] Optimiser les paramètres de performance (work_mem, shared_buffers, etc.)
- [ ] Mettre en place des scripts de maintenance régulière (analyse, reindex, vacuum)
- [ ] Documenter les accès, rôles et schémas utilisés

## 5. Conformité et documentation
- [ ] Documenter la politique de gestion des accès et des mots de passe
- [ ] Tenir à jour la cartographie des bases, utilisateurs et droits
- [ ] S’assurer que les logs d’audit sont conservés selon la politique de sécurité

---

**Ce plan doit être suivi et coché par le DBA lors de la mise en place et de l’exploitation de PostgreSQL pour BRASG.**

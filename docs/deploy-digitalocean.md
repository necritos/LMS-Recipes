# Deploy Digital Ocean (Droplet)

Guía para CI/CD: tests en GitHub Actions + deploy por SSH al Droplet.

## Flujo

1. **Pull request a `main`** → workflow `CI` (ruff + pytest).
2. **Push a `main`** → workflow `Deploy`:
   - pasa tests
   - SSH al Droplet
   - `git fetch` + `reset --hard origin/main`
   - `pip install`, `migrate`, `collectstatic`
   - reinicia `recetario-api` y `recetario-worker`
   - health check local

> En push a `main` solo corre **Deploy** (no se duplica con CI).

## Secrets de GitHub

Repo → **Settings** → **Secrets and variables** → **Actions** → New repository secret:

| Secret | Valor |
|--------|--------|
| `DEPLOY_HOST` | `146.190.232.43` |
| `DEPLOY_USER` | `root` |
| `DEPLOY_PATH` | `/var/www/recetario-backend` |
| `DEPLOY_SSH_KEY` | Contenido completo de la **clave privada** de deploy |

Opcional: crea Environment `production` (Settings → Environments) para proteger deploys.

## Crear clave SSH solo para deploy

### En tu Mac

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/recetario_deploy -N ""
```

- **Pública** → va al Droplet
- **Privada** → va a secret `DEPLOY_SSH_KEY` (todo el contenido de `recetario_deploy`)

```bash
# Ver privada (pegar completa en GitHub secret)
cat ~/.ssh/recetario_deploy

# Ver pública
cat ~/.ssh/recetario_deploy.pub
```

### En el Droplet

```bash
mkdir -p /root/.ssh
chmod 700 /root/.ssh
echo "PEGA_AQUI_LA_CLAVE_PUBLICA" >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
```

Prueba desde tu Mac:

```bash
ssh -i ~/.ssh/recetario_deploy root@146.190.232.43 'echo ok'
```

## Acceso del Droplet al repo (git pull)

Si el repo es **público**, no hace falta nada más.

Si es **privado**, en el Droplet:

```bash
# Como root, deploy key de solo lectura para GitHub
ssh-keygen -t ed25519 -C "droplet-git-pull" -f /root/.ssh/github_deploy -N ""
cat /root/.ssh/github_deploy.pub
```

En GitHub → Settings → Deploy keys → Add (read-only). Luego:

```bash
cat >> /root/.ssh/config <<'EOF'
Host github.com
  IdentityFile /root/.ssh/github_deploy
  IdentitiesOnly yes
EOF
chmod 600 /root/.ssh/config

cd /var/www/recetario-backend
git remote set-url origin git@github.com:necritos/LMS-Recipes.git
git fetch origin
```

## CORS para frontend en localhost

En `.env` del Droplet:

```env
CORS_ALLOW_LOCALHOST=true
CORS_ALLOWED_ORIGINS=https://petralicious.sk,https://www.petralicious.sk,http://localhost:5173,http://127.0.0.1:5173
```

```bash
systemctl restart recetario-api
```

## Certificado SSL (Let's Encrypt / certbot)

| Tema | Detalle |
|------|---------|
| Duración | **90 días** |
| Renovación | Automática vía timer `certbot.timer` (suele renovar ~30 días antes) |
| Comprobar timer | `systemctl status certbot.timer` |
| Renovar a mano | `certbot renew` |

## Deploy manual (si hace falta)

```bash
ssh root@146.190.232.43
cd /var/www/recetario-backend
git fetch origin main && git reset --hard origin/main
bash deploy/remote_deploy.sh
```

## URLs producción

- Health: https://petralicious.sk/health/
- API: https://petralicious.sk/api/v1/
- Docs: https://petralicious.sk/api/docs/

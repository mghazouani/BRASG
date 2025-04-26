// next.config.js fusionné (supporte le lint désactivé et la configuration Next.js)
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Désactive le lint lors du build pour Next.js
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Ajoute ici d'autres options de configuration si besoin
};

module.exports = nextConfig;

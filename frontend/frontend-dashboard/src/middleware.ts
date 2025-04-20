import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Vérifie la présence du token (auth simple, à améliorer pour production)
  const token = request.cookies.get('token')?.value || request.headers.get('authorization')?.replace('Bearer ', '') || '';
  const isAuthPage = request.nextUrl.pathname.startsWith('/login');
  const isDashboard = request.nextUrl.pathname.startsWith('/dashboard');

  // Si pas de token et on veut accéder au dashboard => redirige vers login
  if (!token && isDashboard) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  // Si déjà authentifié et on va sur login => redirige dashboard
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login'],
};

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

export type RouteName = 'home' | 'services' | 'work' | 'about' | 'careers' | 'job-detail' | 'contact' | 'admin' | 'not-found';

export interface RouteMatch {
  name: RouteName;
  path: string;
  params: Record<string, string>;
  title: string;
}

interface RouterContextType {
  currentPath: string;
  route: RouteName;
  params: Record<string, string>;
  navigate: (path: string, options?: { replace?: boolean }) => void;
  goBack: () => void;
}

const RouterContext = createContext<RouterContextType | undefined>(undefined);

// Route parsing helper
export function matchRoute(pathname: string): RouteMatch {
  // Normalize path
  const path = pathname.trim().replace(/\/+$/, '') || '/';

  if (path === '/' || path === '') {
    return { name: 'home', path: '/', params: {}, title: 'Azyntrix — Software Engineering Consultancy & Digital Product Studio' };
  }

  if (path === '/services') {
    return { name: 'services', path: '/services', params: {}, title: 'Technical Disciplines & Practice Areas — Azyntrix' };
  }

  if (path.startsWith('/work')) {
    const parts = path.split('/').filter(Boolean);
    const caseId = parts[1] || '';
    return { name: 'work', path: '/work', params: { caseId }, title: 'Selected Works & Architecture Systems — Azyntrix' };
  }

  if (path === '/about') {
    return { name: 'about', path: '/about', params: {}, title: 'Studio Narrative & Engineering Manifesto — Azyntrix' };
  }

  if (path === '/careers') {
    return { name: 'careers', path: '/careers', params: {}, title: 'Engineering Careers & Guild Opportunities — Azyntrix' };
  }

  if (path.startsWith('/careers/')) {
    const parts = path.split('/').filter(Boolean);
    const jobId = parts[1] || 'senior-fullstack-web-architect';
    return { name: 'job-detail', path, params: { jobId }, title: 'Role Specification & Application — Azyntrix' };
  }

  if (path === '/contact' || path === '/start-a-project') {
    return { name: 'contact', path: '/contact', params: {}, title: 'Initiate Project Discovery & Scoping — Azyntrix' };
  }

  // Fallback / standard tab mapping for backward compatibility (e.g. #home or /home)
  if (path === '/home') {
    return { name: 'home', path: '/', params: {}, title: 'Azyntrix — Software Engineering Consultancy' };
  }

  if (path === '/admin' || path.startsWith('/admin/')) {
    return { name: 'admin', path: '/admin', params: {}, title: 'Admin Control Panel — Azyntrix' };
  }

  return { name: 'not-found', path, params: {}, title: 'Page Not Found — Azyntrix' };
}

export const RouterProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentPath, setCurrentPath] = useState<string>(() => {
    return window.location.pathname || '/';
  });

  const [routeMatch, setRouteMatch] = useState<RouteMatch>(() => {
    return matchRoute(window.location.pathname || '/');
  });

  const updateRoute = useCallback((path: string) => {
    setCurrentPath(path);
    const match = matchRoute(path);
    setRouteMatch(match);
    document.title = match.title;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Listen to browser Back / Forward events
  useEffect(() => {
    const handlePopState = () => {
      updateRoute(window.location.pathname);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [updateRoute]);

  const navigate = useCallback((targetPath: string, options?: { replace?: boolean }) => {
    // Map tab IDs to clean URL paths if a plain tab string is passed
    let normalized = targetPath;
    if (targetPath === 'home') normalized = '/';
    else if (targetPath === 'services') normalized = '/services';
    else if (targetPath === 'work') normalized = '/work';
    else if (targetPath === 'about') normalized = '/about';
    else if (targetPath === 'careers') normalized = '/careers';
    else if (targetPath === 'contact') normalized = '/contact';
    else if (targetPath === 'job-detail') normalized = '/careers/senior-fullstack-web-architect';
    else if (!targetPath.startsWith('/')) normalized = `/${targetPath}`;

    if (normalized === currentPath) return;

    if (options?.replace) {
      window.history.replaceState({}, '', normalized);
    } else {
      window.history.pushState({}, '', normalized);
    }

    updateRoute(normalized);
  }, [currentPath, updateRoute]);

  const goBack = useCallback(() => {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      navigate('/');
    }
  }, [navigate]);

  return (
    <RouterContext.Provider value={{
      currentPath,
      route: routeMatch.name,
      params: routeMatch.params,
      navigate,
      goBack,
    }}>
      {children}
    </RouterContext.Provider>
  );
};

export function useRouter() {
  const context = useContext(RouterContext);
  if (!context) {
    throw new Error('useRouter must be used within a RouterProvider');
  }
  return context;
}

// Declarative Link component for accessible routing
export const Link: React.FC<{
  href: string;
  className?: string;
  children: ReactNode;
  onClick?: () => void;
  [key: string]: any;
}> = ({ href, className, children, onClick, ...props }) => {
  const { navigate } = useRouter();

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    // Allow default browser behavior for external links or Cmd/Ctrl clicks
    if (e.metaKey || e.ctrlKey || e.shiftKey || href.startsWith('http') || href.startsWith('mailto:')) {
      return;
    }

    e.preventDefault();
    onClick?.();
    navigate(href);
  };

  return (
    <a href={href} className={className} onClick={handleClick} {...props}>
      {children}
    </a>
  );
};
